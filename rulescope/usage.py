"""Import per-policy usage (hit counts) from outside the FortiGate.

Hit counters on the box reset at every reboot. Logs in a SIEM or FortiAnalyzer usually
cover a longer, known window, and offline audits have no counters at all. Accepted inputs:

  * CSV   - columns policyid, hits[, last_used][, first_used][, bytes]; header names are
            matched loosely (policy_id, "Policy ID", hit_count, count, last_seen ...).
  * JSON  - the FortiGate's own /api/v2/monitor/firewall/policy response (or its "results" list)
  * JSON  - an OpenSearch / Elasticsearch terms aggregation on the policy-id field
            (Wazuh indexer, Graylog, Elastic): buckets[].key = policy id, doc_count = hits,
            optional max sub-aggregation on the timestamp = last use.

Rows in a log-based source exist only for policies that logged sessions, so a policy
missing from the import counts as zero hits ONLY if it logs all sessions (logtraffic all).
Policies that log only security events, or nothing, are left as unknown.
"""
from __future__ import annotations

import csv
import datetime as _dt
import io
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

Usage = Dict[str, Dict[str, int]]

_ALIASES = {
    "policyid": {"policyid", "policy_id", "policy", "id", "policyid_keyword", "data_policyid", "key"},
    "hit_count": {"hit_count", "hits", "hitcount", "count", "sessions", "doc_count", "total"},
    "last_used": {"last_used", "last_hit", "lastseen", "last_seen", "last", "max_timestamp", "latest"},
    "first_used": {"first_used", "first_hit", "first_seen", "first", "min_timestamp", "earliest"},
    "bytes": {"bytes", "total_bytes", "sum_bytes"},
}


def _norm(h: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in h.strip().lower()).strip("_")


def to_epoch(v: Any) -> int:
    """Epoch seconds from int/float (s, ms, us, ns) or ISO-like date strings. 0 if unknown."""
    if v is None or v == "":
        return 0
    if isinstance(v, (int, float)) or (isinstance(v, str) and v.strip().replace(".", "", 1).isdigit()):
        n = float(v)
        for limit, div in ((1e17, 1e9), (1e14, 1e6), (1e11, 1e3)):
            if n > limit:
                return int(n / div)
        return int(n)
    s = str(v).strip().replace("/", "-")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    for cand in (s, s.replace(" ", "T", 1)):
        try:
            d = _dt.datetime.fromisoformat(cand)
            if d.tzinfo is None:
                d = d.replace(tzinfo=_dt.timezone.utc)
            return int(d.timestamp())
        except ValueError:
            continue
    raise ValueError(f"cannot parse date '{v}' (use epoch or YYYY-MM-DD[ HH:MM[:SS]])")


def _add(out: Usage, pid: Any, hits: Any, last: Any = None, first: Any = None, nbytes: Any = None) -> None:
    try:
        key = str(int(float(str(pid).strip())))
    except ValueError:
        return
    e = out.setdefault(key, {"hit_count": 0, "bytes": 0, "last_used": 0, "first_used": 0})
    e["hit_count"] += int(float(hits or 0))
    e["bytes"] += int(float(nbytes or 0))
    lu = to_epoch(last)
    e["last_used"] = max(e["last_used"], lu)
    fu = to_epoch(first)
    if fu and (not e["first_used"] or fu < e["first_used"]):
        e["first_used"] = fu


def _from_csv(text: str) -> Usage:
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    if not rows:
        return {}
    header = [_norm(h) for h in rows[0]]
    col: Dict[str, int] = {}
    for field, names in _ALIASES.items():
        for i, h in enumerate(header):
            if h in names and field not in col:
                col[field] = i
    if "policyid" not in col or "hit_count" not in col:
        raise ValueError(f"CSV needs a policy id and a hit count column; found headers {rows[0]}")
    out: Usage = {}
    for r in rows[1:]:
        if not r or len(r) <= max(col.values()):
            continue
        g = lambda f: r[col[f]] if f in col else None  # noqa: E731
        _add(out, g("policyid"), g("hit_count"), g("last_used"), g("first_used"), g("bytes"))
    return out


def _find_buckets(obj: Any) -> Optional[List[Dict[str, Any]]]:
    if isinstance(obj, dict):
        if isinstance(obj.get("buckets"), list):
            return obj["buckets"]
        for v in obj.values():
            b = _find_buckets(v)
            if b is not None:
                return b
    return None


def _sub_value(bucket: Dict[str, Any], kind: str) -> Any:
    for k, v in bucket.items():
        if isinstance(v, dict) and "value" in v:
            name = k.lower()
            if (kind == "last" and any(t in name for t in ("last", "max", "latest"))) or \
               (kind == "first" and any(t in name for t in ("first", "min", "earliest"))):
                return v.get("value_as_string") or v.get("value")
    return None


def _from_json(obj: Any) -> Usage:
    out: Usage = {}
    buckets = _find_buckets(obj.get("aggregations", obj)) if isinstance(obj, dict) else None
    if buckets is not None:
        for b in buckets:
            _add(out, b.get("key"), b.get("doc_count"), _sub_value(b, "last"), _sub_value(b, "first"))
        return out
    rows: Iterable[Any] = obj.get("results", []) if isinstance(obj, dict) else obj
    for r in rows or []:
        if isinstance(r, dict) and r.get("policyid") is not None:
            _add(out, r["policyid"], r.get("hit_count", r.get("hits", 0)), r.get("last_used"),
                 r.get("first_used"), r.get("bytes"))
    return out


def load(path: str) -> Usage:
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        text = fh.read()
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return _from_json(json.loads(text))
    return _from_csv(text)


def apply(snap: Dict[str, Any], usage: Usage, source: str, since: Optional[int] = None) -> Tuple[int, int]:
    """Replace the snapshot's hit data. Returns (policies with data, policies left unknown)."""
    hits: Usage = {}
    unknown = 0
    for p in snap["policies"]:
        key = str(p["policyid"])
        if key in usage:
            hits[key] = usage[key]
        elif p["logtraffic"] == "all":
            hits[key] = {"hit_count": 0, "bytes": 0, "last_used": 0, "first_used": 0}
        else:
            unknown += 1
    snap["hits"] = hits
    snap["usage_source"] = f"import:{os.path.basename(source)}"
    snap["counter_since"] = since
    snap["notes"].append(
        f"Usage imported from {os.path.basename(source)}: {sum(1 for k in usage if k in hits)} policies with "
        f"recorded hits. {unknown} policies do not log all sessions (logtraffic not 'all'), so their usage "
        "is unknown and they are excluded from zero-hit checks.")
    return len(hits), unknown
