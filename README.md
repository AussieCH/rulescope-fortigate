# rulescope

FortiGate security audit, best-practice baseline, rule base cleanup and change control. Read-only, fully on-prem, pure Python 3.9+, zero dependencies.

One firewall or a whole fleet, from the live REST API or from a config backup a client emails you.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/report-overview-dark.png">
  <img alt="Audit report overview: security score, high-severity findings, internet exposure, firmware, best-practice baseline, quick wins and cleanup potential" src="docs/images/report-overview.png">
</picture>

## What it finds

| Area | Checks |
|---|---|
| Internet exposure | Every service reachable from the internet: VIP port-forwards, static NAT, routed inbound rules, admin GUI/SSH on WAN, SSL-VPN portal, IKE listeners. Risky services (RDP, SMB, databases, WinRM, VNC, SNMP, ICS protocols ...) exposed, all-ports exposure, inbound rules without IPS. Severity depends on who can reach it: anyone, some countries, or specific addresses. Local-in deny policies and trusted hosts are taken into account. |
| Rule base | Shadowed deny rules, dead accept rules, redundant rules (provable full coverage, earliest covering rule named), any-to-any, unrestricted outbound, service ALL, zero-hit and stale rules, expired one-time schedules, disabled and undocumented rules, no ISDB deny for Tor/scanner/malicious sources above published services, zones with intrazone allow |
| Device hardening | Telnet/HTTP management, trusted hosts on admins and API users, admins without MFA, API users with super_admin, many super_admins, default `admin` account, lockout threshold and duration, password policy, admin GUI TLS versions, strong-crypto, static-key ciphers, idle timeout, default admin ports, login banner, hostname on the login page, USB auto-install, private data encryption, NTP, SNMP v1/v2c and SNMPv3 without auth-priv, LDAP without TLS, HA monitoring and management interface |
| Firmware | FortiOS lifecycle (end of engineering support, end of support) and the CVEs that affect this exact version, flagged when CISA lists them as exploited in the wild (NIST NVD lookup with local cache) |
| Logging & inspection | Accept rules without logging, event logging off, no central logging (FortiAnalyzer, cloud or syslog), unencrypted log transport, internet-bound rules without security profiles or missing IPS / antivirus / DNS filter / application control, IPS without botnet blocking, DNS filter without C&C blocking, FortiGuard update schedule off, expired subscriptions (API) |
| VPN | Weak IPsec proposals and DH groups, IKEv1 aggressive mode with PSK, phase 2 without PFS, SSL-VPN allowing TLS < 1.2, SSL-VPN on the factory certificate, SSL-VPN tunnel mode still in use (removed in FortiOS 7.6.3) |
| Objects | Unreferenced addresses, groups, services, VIPs |

**Best-practice baseline.** 37 FortiGate practices from Fortinet's hardening guide and administrator best practices, the CIS FortiGate benchmark and the Canadian Cyber Centre advisory AL25-005, each marked Pass, Partial, Fail, Manual check, Not applicable or Not assessed, with the evidence from this configuration. "Not assessed" means the data was not available (for example a token without permission); it never counts as a pass.

Every finding maps to CIS FortiGate 7.0.x v1.4.0, ISO 27001:2022, PCI DSS 4.0 and NIST SP 800-53 r5 controls (indicative, for auditors), and carries an effort tag: quick fix, change window or project.

Outputs: client-ready HTML report (key tiles, executive summary, priority actions, quick wins, best-practice baseline, exposure map, firmware and advisories, compliance appendix), FortiOS remediation script, CSV for Excel (findings and baseline), JSON, change reports with who-changed-what, and a fleet dashboard. Every page has light and dark modes and five color palettes (Harbor, Forest, Ocean, Graphite, High contrast) that readers can switch; printing always uses the light variant.

## Screenshots

All screenshots come from the demo site in [`examples/demo-site`](examples/demo-site) (three made-up firewalls; addresses are documentation ranges).

| | |
|---|---|
| **Internet exposure**: every service reachable from the internet, with who can reach it and what protects it<br><img alt="Internet exposure table" src="docs/images/report-exposure.png"> | **Best-practice baseline**: 37 practices with the evidence from this configuration<br><img alt="Best-practice baseline with pass and fail status" src="docs/images/report-practices.png"> |
| **Fleet dashboard**: score, firmware status and risky changes for every device<br><img alt="Fleet dashboard" src="docs/images/fleet-dashboard.png"> | **Change report**: what changed since the last snapshot, with alerts for risky changes<br><img alt="Configuration change report with alerts" src="docs/images/change-report.png"> |

## Install

```bash
python3 -m pip install .          # or: pipx install .
rulescope --version
```

No install needed: `python3 -m rulescope ...` from this folder, or the single-file build: `python3 rulescope-0.4.0.pyz ...`.

## 1. Read-only API user on the FortiGate

Replace `192.0.2.50` with the IP of the machine that runs rulescope.

```
config system accprofile
    edit "rulescope-ro"
        set secfabgrp read
        set ftviewgrp read
        set authgrp read
        set sysgrp read
        set netgrp read
        set loggrp read
        set fwgrp read
        set vpngrp read
        set utmgrp read
        set wifi read
    next
end
config system api-user
    edit "rulescope"
        set accprofile "rulescope-ro"
        set vdom "root"
        config trusthost
            edit 1
                set ipv4-trusthost 192.0.2.50 255.255.255.255
            next
        end
    next
end
execute api-user generate-key rulescope
```

Skip any profile line your FortiOS version rejects. `sysgrp read` covers admins, password policy, SNMP, HA and licenses; `loggrp read` covers log settings and lets rulescope show who made each change; `utmgrp read` covers IPS and DNS filter profiles. Whatever the token cannot read is reported as "Not assessed", never as a pass. Save the key:

```bash
install -m 600 /dev/null ~/.rulescope-token && nano ~/.rulescope-token
```

## 2. Audit one firewall

Live (hit counters, change log):

```bash
# once: the SHA-256 fingerprint of the FortiGate's (self-signed) certificate
openssl s_client -connect 192.0.2.1:443 </dev/null 2>/dev/null | openssl x509 -noout -fingerprint -sha256

rulescope audit --host 192.0.2.1 --token-file ~/.rulescope-token --pin-sha256 AA:BB:...:FF \
  --client "Home lab" --auditor "Your Name" \
  --html report.html --cli fix.txt --csv findings.csv --save-snapshot snapshots
```

With a certificate from your own CA use `--ca-file ca.pem` instead of the pin. `--insecure` skips verification and exposes the API token to anyone on the path.

Offline, from a config backup (no device access):

```bash
rulescope audit --config FGT_backup.conf --client "Client Ltd" --html report.html --cli fix.txt
```

Useful options:

| Option | Effect |
|---|---|
| `--usage FILE --usage-since DATE` | Hit counts from a SIEM, FortiAnalyzer or the FortiGate's own JSON (section 3) |
| `--baseline OLD.json` | Adds "Progress since ..." (score change, resolved and new findings). Takes a snapshot or a findings JSON. |
| `--redact [--redact-map map.json]` | Pseudonymizes names (objects, interfaces, VDOM, custom internet services), published IPs, hostname, serial and policy UUIDs in every output. Findings are identical, and with `--baseline` both snapshots share one pseudonym table. Use it for sales samples or to share output for support. |
| `--wan port1,port2` / `--not-wan port10` | Set the internet-facing interfaces yourself, or remove wrongly detected ones (zone names work too). Fleet inventory keys: `wan =`, `not_wan =` |
| `--advisories online` | Look up known CVEs for this FortiOS version in the NIST NVD (section 4) |
| `--palette forest` | Default palette of the report: `harbor`, `forest`, `ocean`, `graphite`, `contrast`. Readers can still switch it, and light/dark. |
| `--practices-csv baseline.csv` | The best-practice baseline as a spreadsheet with owner and target-date columns |
| `--fail-on high` | Exit code 2 when anything at that severity or above is found (cron/CI) |
| `--host 192.0.2.1:8443`, `--vdom DMZ` | Non-default admin port, other VDOM |
| `--pin-sha256 FINGERPRINT` / `--ca-file ca.pem` | Verify the FortiGate certificate: pin a self-signed one, or check it against your CA |

## 3. Usage data that survives reboots

FortiGate hit counters reset on every reboot. Logs usually cover a longer window, so rulescope can import usage. Policies missing from a log-based import count as zero-hit only if they log all sessions (`logtraffic all`). The rest are left unknown, so you never get a false "unused" verdict.

**CSV** (FortiAnalyzer report, SIEM export, Excel): a policy-id column and a hit-count column; last-seen optional. Header names are matched loosely (`policyid`, `Policy ID`, `hits`, `count`, `last_seen` ...), and `,` `;` and tab delimiters all work.

**FortiGate JSON** (good for remote audits; the client runs one command):

```bash
curl -sk -H "Authorization: Bearer $TOKEN" "https://FGT/api/v2/monitor/firewall/policy?vdom=root" > hits.json
```

**OpenSearch / Elasticsearch aggregation** (Wazuh indexer, Graylog, Elastic): run a terms aggregation on the policy-id field and pass the response file as is. Field and index names depend on your decoder or pipeline. Use the index that holds raw FortiGate traffic logs (for Wazuh, the archives index when log-all is enabled).

```bash
curl -sk -u USER:PASS "https://INDEXER:9200/INDEX-PATTERN/_search" -H 'Content-Type: application/json' -d '{
  "size": 0,
  "query": {"bool": {"filter": [{"exists": {"field": "data.policyid"}},
                                {"range": {"timestamp": {"gte": "now-90d"}}}]}},
  "aggs": {"by_policy": {"terms": {"field": "data.policyid", "size": 10000},
           "aggs": {"last_seen": {"max": {"field": "timestamp"}}}}}}' > hits.json

rulescope audit --config FGT_backup.conf --usage hits.json --usage-since 2026-08-06 --html report.html
```

## 4. Firmware lifecycle and known vulnerabilities

The report always shows where the FortiOS branch is in Fortinet's lifecycle: GA, end of engineering support (no more committed fixes) and end of support (no more security patches at all). The dates ship with rulescope and were checked on 2026-11-05, including Fortinet's one-year extension of 7.4 and 7.6. If Fortinet changes them, pass `--lifecycle-file dates.json` (`{"7.4": ["2023-05-11", "2027-05-11", "2028-11-11"]}`).

Known vulnerabilities come from the NIST National Vulnerability Database, queried with the exact version (`cpe:2.3:o:fortinet:fortios:7.4.3`), so only CVEs whose affected range includes the build are listed. CVEs on CISA's Known Exploited Vulnerabilities list are flagged and rated high.

| `--advisories` | Behavior |
|---|---|
| `cache` (default) | Uses results already in `~/.cache/rulescope/nvd` (or `--cache-dir`). No network access. |
| `online` | Refreshes results older than a day from services.nvd.nist.gov (outbound HTTPS, honors `HTTPS_PROXY`), falls back to the cache if NVD is unreachable. |
| `off` | No lookup; the baseline marks the practice as not fully assessed. |

Without a key NVD allows 5 requests per 30 seconds, and rulescope paces itself. A free API key (`--nvd-api-key-file` or `NVD_API_KEY`) raises that tenfold. For air-gapped sites, run `rulescope firmware 7.4.3 7.2.10 --advisories online` on a connected machine and copy the cache folder across. The same command prints the lifecycle and CVEs of any version, which is handy before an upgrade.

A CVE in the list may already be mitigated by a workaround; each one links to its FortiGuard advisory. NVD can lag a few days behind Fortinet's own PSIRT publications.

## 5. Fleet mode

```bash
rulescope fleet --inventory fleet.ini --out site --snapshots snapshots --auditor "Security team"
```

See `examples/fleet.ini.example`. Each section is a device (live `host` or offline `config`). `vdom = root, DMZ` gives one report per VDOM. Devices are collected in parallel (`--workers`), and one failing device does not stop the run.

Output: `site/index.html` (scores, trends, best-practice results, firmware lifecycle and exploited CVEs per device, exposure, cleanup potential, risky-change alerts, most common findings across the fleet, FortiOS versions with their end-of-support dates) plus per device `report.html`, `changes.html`, `findings.csv`, `practices.csv`, `findings.json` and `fix.txt`. Add `--advisories online` to keep vulnerability data fresh (one NVD request per distinct FortiOS version per day). Each report's "Progress since" section compares against a snapshot about `--baseline-days` old (default 30). Snapshots are pruned automatically: the newest 48 are kept, then one per day.

Hourly with systemd:

```bash
sudo useradd --system --home /var/lib/rulescope --create-home rulescope
sudo install -d -m 700 -o rulescope /etc/rulescope
sudo install -m 600 -o rulescope ~/.rulescope-token /etc/rulescope/token
sudo install -m 600 -o rulescope fleet.ini /etc/rulescope/fleet.ini
sudo cp deploy/rulescope-fleet.service deploy/rulescope-fleet.timer /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now rulescope-fleet.timer
```

Serve `/var/lib/rulescope/site` to administrators only (`deploy/nginx-rulescope.conf` restricts by IP and requires basic auth). The pages describe exactly how each firewall is weak.

### Risky-change alerts

Every run compares each device with its previous snapshot. These changes raise alerts:
- Management access added on an internet-facing interface
- New admin or API account
- Trusted hosts removed from an account
- Account profile changed
- New or changed inbound rule from the internet
- Logging disabled on a rule, or event logging disabled
- Two-factor authentication removed from an admin
- strong-crypto disabled, static-key ciphers enabled, admin TLS weakened, admin idle timeout raised above 15 minutes
- Password policy, NTP, scheduled FortiGuard updates or private data encryption disabled; USB auto-install enabled
- SSL-VPN settings changed
- A local-in deny policy removed, or a local-in policy changed
- A deny rule for traffic from the internet removed or disabled, or a rule from the internet moved in the sequence
- An address, service or VIP object (or group) changed that an inbound rule uses

The diff also lists changes to zones, VIP groups and local-in policies.

Send alerts anywhere with a webhook (JSON with a `text` field, which Slack, Mattermost and workflow-style webhooks accept) and/or `--syslog host:514` (RFC 5424, so the SIEM can alert too). Give the webhook URL with `--webhook-file FILE` or the `RULESCOPE_WEBHOOK` environment variable; `--webhook URL` works too, but puts the URL in the process list. Single device: `rulescope collect ... --diff --webhook-file FILE`.

Alerts are not lost when delivery fails: undelivered alerts are kept on disk and sent again with the next run, the dashboard lists the failure, and the command exits with code 4. The dashboard shows the alerts of the last 7 days.

With API access, each change shows who made it (user, GUI/CLI/API and source IP, time), taken from the FortiGate's system event log. Values of password, PSK and key attributes are masked before anything is stored.

## Reading the results

- **Score.** Each area starts at 100. Absolute findings cost severity weight × (1 + log2 n), capped at 4× the weight. Hygiene findings cost weight × (1 + 9 × share of rules or objects affected), so 5 unused rules out of 2,000 is a minor issue while 5 out of 10 is not. The overall score is the weighted mean of areas: internet exposure 25%, rule base 20%, device hardening 25%, logging & inspection 15%, VPN 10%, objects 5%. Any high-severity finding (an exploited CVE, an unsupported FortiOS branch, RDP open to the world ...) caps the overall score at 69 (D).
- **Best-practice baseline vs. score.** The score weighs findings by risk; the baseline answers "which recommended practices does this firewall follow". A device can score well and still miss practices with no direct risk weight, such as login banners.
- **Quick wins** are findings fixed by one setting whose command does not change allowed traffic or management access. The report gives them as a separate, ready-to-paste script.
- **Comparisons are fair across versions.** "Progress since" only compares checks that both runs evaluated, so new checks in a newer rulescope, or data an older token could not read, never show up as "new" findings.
- **Internet-facing interfaces** = WAN role ∪ SD-WAN members ∪ default-route egress interfaces ∪ DHCP/PPPoE clients ∪ VIP external interfaces. IPsec tunnels and interfaces whose role is explicitly `lan` or `dmz` are never picked by these guesses, so a default route to an upstream internal network is not misread as the internet. The console and the report list each interface with the reason it was chosen; correct it with `--wan` / `--not-wan`.
- **Coverage findings** are reported only when provable. FQDN, geography, wildcard, ISDB and VIP objects are treated conservatively. The index that makes this fast is verified against brute force in the tests: 10,000 rules take under a second.
- **Remediation script.** Rules are disabled (not deleted) with a dated comment. Anything that changes allowed traffic, VPN peers or management reachability is commented out, including the removal of Telnet or HTTP from an interface. A zero-hit rule gets a live disable command only when the counters are known to cover at least `--stale-days`; after a recent reboot, or when the period is unknown, the command is commented out.
- **Not assessed, never a pass.** When an input could not be read (a token without permission, or a partial backup without `config system global`), the practices that depend on it are "Not assessed". This covers interface, SSL-VPN, IPsec and local-in settings and API users. NTP is "Not assessed" when a backup does not set `ntpsync` explicitly, because its default differs between FortiOS versions.
- **Compliance references** help an auditor find the right control. They are not a certification.

## Remote audit kit (for the audit service)

Ask the client for:
1. An unencrypted config backup (System > Configuration > Backup, encryption off). It still contains encrypted secrets, so use a secure transfer.
2. The hit counts: the `curl` above, or a FortiAnalyzer/SIEM export covering at least 90 days.

Then run:

```bash
rulescope audit --config backup.conf --usage hits.json --client "Client Ltd" --auditor "Your Name" \
  --html report.html --cli fix.txt --csv findings.csv --save-snapshot audits
```

For the follow-up audit, add `--baseline` with the first snapshot: the report then shows the progress the client paid for.

## Security of the tool

The API token is read-only and restricted to one source IP by trusted hosts. Snapshots never contain the raw config, password hashes, PSKs or keys, and are written with mode 600. Reports and dashboards are sensitive: they list weaknesses.

- **TLS.** Verify the FortiGate certificate with `--ca-file`, or pin a self-signed certificate with `--pin-sha256` (fleet inventory: `pin_sha256 =`). The pin is checked on every connection before the token is sent. Get the fingerprint once, over a path you trust: `openssl s_client -connect 192.0.2.1:443 </dev/null 2>/dev/null | openssl x509 -noout -fingerprint -sha256`. `--insecure` switches verification off, so anyone on the path can read the token; keep it for a first test in a lab.
- **Redirects are never followed**, so the API token, the NVD key and alert texts only go to the host you configured.
- **Config backups are untrusted input.** A backup a client sends can contain crafted names. Line breaks and control characters are removed before a name reaches the remediation script, so a name cannot add commands to it; spreadsheet cells that start with `=`, `+`, `-` or `@` are prefixed with `'`; only `https` URLs become links in the report. Still review `fix.txt` before applying it.
- **File permissions.** Reports written by `audit`, `analyze` and `diff` are mode 600. The systemd units set `UMask=0027`; add the web server user to the `rulescope` group to serve the fleet site.
- **Webhook URLs are secrets.** Use `--webhook-file` or `RULESCOPE_WEBHOOK` instead of `--webhook`, which shows up in the process list.

## Limits (v0.4)

- IPv4 coverage math; IPv6 addresses in unified policies are compared by name.
- Firewall policies, local-in policies, VPN and system settings; proxy and DoS policies are not analyzed yet. Security policies (NGFW policy-based mode), IPv6 policies of FortiOS before 6.4 and IPv6 virtual IPs are not analyzed either: when a device has any, the report says so in its notes instead of showing a clean rule base.
- Rules that use negated addresses, services or internet services, ZTNA tags, IPv6 internet services or vendor MAC matching are left out of shadow and redundancy detection.
- A static route to a named address or internet service is not treated as a default route.
- A source counts as "anyone" when it is `all`, negated, or covers a /8 or more of public address space (this includes groups built as "everything except ...").
- A local-in deny only counts as protection when it is always active, has no negated field, applies to every source and its destination is `all` or contains the interface address.
- Security profiles are checked for presence and botnet blocking, not for full quality (an IPS sensor in monitor mode still counts as IPS).
- Partial overlaps (rule B only partly covered by A) are not reported, only full coverage.
- Config backups omit default values. rulescope fills in FortiOS defaults where they are known for the version; where a default differs between versions and is not known (for example admin TLS versions before 7.0), the setting is marked not assessed instead of guessed.
- The REST API paths are validated against a mock; check your first live run's notes for endpoints your FortiOS version names differently.

## Tests

```bash
python3 -m unittest discover -s tests -v
python3 tests/bench.py 10000          # performance on a synthetic 10k-rule base
```

## License

Copyright 2026 Pavel Simanovski

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.

rulescope is provided "as is", without warranty of any kind. It reads configurations and never changes them; review every remediation script before applying it to a firewall.
