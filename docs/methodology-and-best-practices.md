# RuleScope methodology and FortiGate best practices

Full doc (editable): https://claude.ai/artifact/NEnCWhvEUWoxjiFwsUCUtF (updated 2026-11-05 for RuleScope 0.4.0)

Baseline: 37 FortiGate practices from Fortinet guidance, CIS FortiGate 7.0.x v1.4.0 / 7.4.x v1.0.1 and Canadian Cyber Centre AL25-005. RuleScope 0.4 checks all 37: 33 fully, 4 partly (backup encryption, timezone, the default admin's password and one-account-per-person cannot be read from a configuration). Every report shows each practice as Pass / Partial / Fail / Manual check / Not applicable / Not assessed, with evidence.

0.4 decisions:
- Areas and weights: internet exposure 25%, rule base 20%, device hardening 25% (was "admin access"), logging & inspection 15%, VPN 10%, objects 5%. Any high finding caps the score at 69.
- 35 new checks (device hardening, logging, profiles, firmware). "Not assessed" never counts as a pass; comparisons only use checks both runs evaluated.
- Firmware: built-in FortiOS lifecycle table (7.2 end of support 2026-09-30; 7.4 and 7.6 extended one year), NVD CVE lookup by exact CPE with CISA KEV flag, cached on disk (--advisories cache|online|off).
- Effort tags (quick fix / change window / project) and a quick-wins script of safe single-setting fixes.
- Five palettes (Harbor, Forest, Ocean, Graphite, High contrast), light and dark, validated for color-vision deficiency; print always uses light.

Next checks, in priority order:
1. Security-profile quality (IPS monitor mode, AV not blocking, web filter / app control high-risk categories)
2. Fortinet PSIRT feed next to NVD, with minimum fixed builds
3. Proxy and DoS policies
4. Verify FortiOS defaults per major version against real backups (validation corpus)
