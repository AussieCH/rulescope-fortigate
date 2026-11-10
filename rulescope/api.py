"""Read-only FortiOS REST API collector (stdlib only, no requests dependency).

Use a REST API admin bound to a read-only admin profile and restricted to the
auditor's IP with trusted hosts. Nothing here ever writes to the device.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from . import net
from .usage import to_epoch


class ApiError(Exception):
    def __init__(self, status: int, path: str, detail: str = ""):
        self.status, self.path = status, path
        hint = {
            401: "token rejected - check the token and that this machine's IP is in the API user's trusted hosts",
            403: "token lacks permission for this object",
            404: "endpoint not available on this FortiOS version",
            405: "method not allowed on this FortiOS version",
        }.get(status, "")
        if 300 <= status < 400:
            hint = ("the address answers with a redirect; rulescope never follows redirects, so the API token "
                    "is not sent to another host - check the host and admin port")
        super().__init__(f"HTTP {status} on {path}" + (f": {hint}" if hint else "") + (f" ({detail})" if detail else ""))


# attr[old->new] or attr[old]->[new]: mask every bracketed value that belongs to a secret-looking attribute
_SECRET_RE = re.compile(r"([\w.-]*(?:passw|pwd|passphrase|psk|secret|key|token|private|community|credential)[\w.-]*)"
                        r"\[[^\]]*\](?:\s*->\s*\[[^\]]*\])?", re.I)


def _sanitize(s: Any, limit: int) -> str:
    s = _SECRET_RE.sub(r"\1[***]", str(s or ""))
    return s if len(s) <= limit else s[:limit - 3] + "..."


def _event_time(e: Dict[str, Any]) -> int:
    for k in ("eventtime", "itime"):
        if e.get(k):
            try:
                return to_epoch(e[k])
            except ValueError:
                pass
    date, tm, tz = e.get("date"), e.get("time"), str(e.get("tz") or "+0000")
    if date and tm:
        if re.fullmatch(r"[+-]\d{4}", tz):
            tz = tz[:3] + ":" + tz[3:]
        try:
            return int(_dt.datetime.fromisoformat(f"{date}T{tm}{tz}").timestamp())
        except ValueError:
            return 0
    return 0


def _progress(resp: Dict[str, Any]) -> float:
    """Percent complete of a log search; a missing value means done, 0 means just started."""
    v = resp.get("completed")
    try:
        return 100.0 if v is None or v == "" else float(v)
    except (TypeError, ValueError):
        return 100.0


def normalize_event(e: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "time": _event_time(e), "user": str(e.get("user", "")), "ui": str(e.get("ui", "")),
        "action": str(e.get("action", "")), "cfgpath": str(e.get("cfgpath", "")), "cfgobj": str(e.get("cfgobj", "")),
        "cfgattr": _sanitize(e.get("cfgattr", ""), 400), "msg": _sanitize(e.get("msg", ""), 300),
    }


class FortiGateAPI:
    def __init__(self, host: str, token: str, port: int = 443, vdom: str = "root",
                 verify: bool = True, ca_file: Optional[str] = None, timeout: int = 30,
                 pin_sha256: Optional[str] = None):
        """`pin_sha256`: SHA-256 fingerprint of the FortiGate's certificate. It replaces CA verification,
        so a self-signed certificate is still checked on every connection (unlike verify=False)."""
        h = host.strip("[]")
        self.base = f"https://[{h}]:{port}" if ":" in h else f"https://{h}:{port}"
        self.token, self.vdom, self.timeout = token, vdom, timeout
        pin = net.normalize_pin(pin_sha256) if pin_sha256 else None
        if pin or not verify:
            self.ctx = net.unverified_context()
        else:
            self.ctx = ssl.create_default_context(cafile=ca_file)
        self.opener = net.build_opener(self.ctx, pin)

    def _request(self, method: str, path: str, params: Optional[Dict[str, str]] = None,
                 body: Optional[Dict[str, Any]] = None, raw: bool = False) -> Any:
        q = dict(params or {})
        url = f"{self.base}/api/v2/{path}"
        if q:
            url += "?" + urllib.parse.urlencode(q)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with self.opener.open(req, timeout=self.timeout) as r:
                payload = r.read()
        except urllib.error.HTTPError as e:
            detail = e.read()[:200].decode(errors="replace").strip()
            e.close()
            raise ApiError(e.code, path, detail) from None
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot reach {self.base}: {e.reason}") from None
        if raw:
            return payload.decode(errors="replace")
        return json.loads(payload)

    def get(self, path: str, vdom_scoped: bool = True, **params: str) -> Any:
        if vdom_scoped:
            params.setdefault("vdom", self.vdom)
        return self._request("GET", path, params)

    def backup(self) -> Optional[str]:
        """Full config text, used only in memory for reference counting. Endpoint differs by version."""
        attempts = [
            ("GET", {"scope": "global"}, None),
            ("POST", None, {"destination": "file", "scope": "global"}),
            ("POST", None, {"scope": "global"}),
        ]
        for method, params, body in attempts:
            try:
                text = self._request(method, "monitor/system/config/backup", params, body, raw=True)
            except ApiError:
                continue
            if "config system global" in text or text.lstrip().startswith("#config-version"):
                return text
        return None

    def config_events(self, rows: int = 1000) -> Tuple[Optional[List[Dict[str, Any]]], str]:
        """Configuration-change events (who changed what) from the system event log: disk first, then memory."""
        last_err = ""
        for source in ("disk", "memory"):
            path = f"log/{source}/event/system"
            params = {"rows": str(rows), "vdom": self.vdom}
            try:
                resp = self._request("GET", path, params)
                tries = 0
                while (isinstance(resp, dict) and resp.get("session_id") and tries < 10
                       and _progress(resp) < 100):
                    time.sleep(0.5)
                    tries += 1
                    resp = self._request("GET", path, {**params, "session_id": str(resp["session_id"])})
            except ApiError as e:
                last_err = str(e)
                continue
            results = resp.get("results", []) if isinstance(resp, dict) else []
            events = [normalize_event(e) for e in results if isinstance(e, dict) and e.get("cfgpath")]
            if events or source == "memory":
                events.sort(key=lambda e: e["time"], reverse=True)
                return events[:500], source
        return None, last_err

    def collect_raw(self, with_backup: bool = True, with_events: bool = True) -> Dict[str, Any]:
        """Pull everything the analyzer needs. Optional objects that fail are recorded, not fatal."""
        out: Dict[str, Any] = {"errors": []}
        out["status"] = self.get("monitor/system/status")      # fail fast on auth problems
        out["policy"] = self.get("cmdb/firewall/policy")

        optional = {
            "global": ("cmdb/system/global", False, False),
            "address": ("cmdb/firewall/address", True, True),
            "addrgrp": ("cmdb/firewall/addrgrp", True, True),
            "service_custom": ("cmdb/firewall.service/custom", True, True),
            "service_group": ("cmdb/firewall.service/group", True, True),
            "vip": ("cmdb/firewall/vip", True, True),
            "vipgrp": ("cmdb/firewall/vipgrp", True, True),
            "zone": ("cmdb/system/zone", True, False),
            "sdwan": ("cmdb/system/sdwan", True, False),
            "interface": ("cmdb/system/interface", False, False),
            "admin": ("cmdb/system/admin", False, False),
            "api_user": ("cmdb/system/api-user", False, False),
            "sched_onetime": ("cmdb/firewall.schedule/onetime", True, False),
            "sched_group": ("cmdb/firewall.schedule/group", True, False),
            "vpn_ssl": ("cmdb/vpn.ssl/settings", True, False),
            "phase1": ("cmdb/vpn.ipsec/phase1-interface", True, False),
            "phase2": ("cmdb/vpn.ipsec/phase2-interface", True, False),
            "local_in": ("cmdb/firewall/local-in-policy", True, False),
            "router_static": ("cmdb/router/static", True, False),
            "policy_stats": ("monitor/firewall/policy", True, False),
            "webui_state": ("monitor/web-ui/state", False, False),
            # tables rulescope does not analyze: read only to say so in the report when they hold rules
            "security_policy": ("cmdb/firewall/security-policy", True, False),
            "proxy_policy": ("cmdb/firewall/proxy-policy", True, False),
            "vip6": ("cmdb/firewall/vip6", True, False),
            "vdom_settings": ("cmdb/system/settings", True, False),
        }
        quiet = {"admin", "api_user", "webui_state", "sdwan", "sched_onetime", "sched_group", "phase2",
                 "security_policy", "proxy_policy", "vip6", "vdom_settings"}
        exposure_inputs = {"vpn_ssl", "phase1", "local_in", "router_static"}
        for key, (path, scoped, meta) in optional.items():
            try:
                out[key] = self.get(path, vdom_scoped=scoped, **({"with_meta": "1"} if meta else {}))
            except ApiError as e:
                out[key] = None
                if key in exposure_inputs:
                    out["errors"].append(f"Could not read {path} ({e.status}); exposure checks may be incomplete.")
                elif key not in quiet:
                    out["errors"].append(str(e))

        # hardening settings for the best-practice checks; unreadable ones stay None (reported once as a note)
        from .model import API_SETTING_PATHS
        out["cfg"] = {}
        for cpath, (path, scoped) in API_SETTING_PATHS.items():
            try:
                out["cfg"][cpath] = self.get(path, vdom_scoped=scoped)
            except ApiError:
                out["cfg"][cpath] = None
        try:
            out["license"] = self.get("monitor/license/status", vdom_scoped=False)
        except ApiError:
            out["license"] = None

        have_qref = all(
            all("q_ref" in row for row in ((out.get(k) or {}).get("results") or []))
            for k in ("address", "addrgrp", "service_custom", "service_group", "vip", "vipgrp"))
        out["backup_text"] = self.backup() if (with_backup and not have_qref) else None
        if with_events:
            events, info = self.config_events()
            out["config_events"] = events
            if events is None:
                out["errors"].append(f"Config change log not readable ({info}); change attribution unavailable.")
        return out
