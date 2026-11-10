"""Change notifications: generic JSON webhook (Slack/Mattermost/Teams-workflow style 'text') and syslog."""
from __future__ import annotations

import datetime as _dt
import json
import os
import socket
import urllib.request
from typing import Any, Callable, Dict, List, Optional

from . import net


def webhook_url(url: Optional[str] = None, url_file: Optional[str] = None) -> Optional[str]:
    """The webhook URL from a file, the RULESCOPE_WEBHOOK environment variable or the command line.
    A chat webhook URL is a secret (anyone who has it can post), so the file or variable is preferred:
    a command-line argument shows up in the process list and in unit files."""
    if url_file:
        with open(url_file, encoding="utf-8") as fh:
            url = fh.read().strip()
    url = url or os.environ.get("RULESCOPE_WEBHOOK") or None
    if url and not url.lower().startswith(("https://", "http://")):
        raise ValueError("webhook URL must start with https:// or http://")
    return url


def webhook(url: str, device: str, alerts: List[str], changes: int, report_link: Optional[str] = None,
            timeout: int = 10) -> None:
    if not url.lower().startswith(("https://", "http://")):
        raise ValueError("webhook URL must start with https:// or http://")
    text = f"rulescope: {len(alerts)} risky change(s) on {device}\n" + "\n".join(f"- {a}" for a in alerts)
    if report_link:
        text += f"\n{report_link}"
    payload: Dict[str, Any] = {"text": text, "device": device, "alerts": alerts, "changes": changes}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with net.build_opener().open(req, timeout=timeout) as r:  # no redirects: alerts go to the configured host only
        r.read()


def deliver(pending_path: str, send: Callable[[List[str]], None], alerts: List[str]) -> Optional[str]:
    """Send `alerts` together with any that could not be sent earlier. Undelivered alerts are kept in
    `pending_path` and retried on the next run, so a webhook outage never loses one. Returns the
    error text if delivery failed, else None."""
    pending: List[str] = []
    try:
        with open(pending_path, encoding="utf-8") as fh:
            pending = [str(x) for x in json.load(fh)]
    except (OSError, ValueError, TypeError):
        pending = []
    todo = pending + [a for a in alerts if a not in pending]
    if not todo:
        return None
    try:
        send(todo)
    except Exception as e:  # any failure (network, DNS, HTTP status) keeps the alerts for the next run
        try:
            with open(pending_path, "w", encoding="utf-8") as fh:
                json.dump(todo[-500:], fh)
        except OSError:
            pass
        return f"{type(e).__name__}: {e}"
    try:
        os.remove(pending_path)
    except OSError:
        pass
    return None


def _one_line(s: str) -> str:
    """Names come from the device: no line breaks or control characters in a syslog record."""
    return "".join(c if c.isprintable() else " " for c in str(s)).replace('"', "'")


def syslog(target: str, device: str, alerts: List[str]) -> None:
    """RFC 5424 over UDP, facility local0, severity warning. target = host, host:port, IPv6 or [IPv6]:port."""
    from .source import split_host_port
    host, port = split_host_port(target, 514)
    family, _, _, _, addr = socket.getaddrinfo(host, port, type=socket.SOCK_DGRAM)[0]
    ts = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    me = socket.gethostname()
    with socket.socket(family, socket.SOCK_DGRAM) as s:
        for a in alerts:
            msg = f"<132>1 {ts} {me} rulescope - change - device={_one_line(device)} alert=\"{_one_line(a)}\""
            s.sendto(msg.encode()[:2048], addr)
