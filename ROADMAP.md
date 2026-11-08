# rulescope roadmap and recommendations

## Before selling anything

1. **Ownership.** Under Israeli law, inventions made in the course of employment can belong to the employer by default (Patents Law section 132), so confirm in writing that rulescope is yours. Build and test it on your own time and hardware, never on employer configs.
2. **Validation corpus.** Run 0.4 against 10+ real configs across FortiOS 6.4, 7.0, 7.2, 7.4 and 7.6 (and 8.0 when you can), small and large, single and multi-VDOM, from backups and from the API. Keep `--redact` copies of the outputs as a regression set, and fix every false positive before a client sees it. The default values that backups omit are the main risk for the new hardening checks: confirm them on each major version with `get system global`, `get system auto-install` and friends.
3. **Name.** Check that "rulescope" is free as a trademark and domain in your market before it goes on invoices.

## Go to market

- **Offer 1: fixed-price FortiGate audit.** Deliverables: the HTML report, the best-practice baseline (practices.csv doubles as the client's remediation tracker), the quick-wins script, the full remediation script, and a 30-day re-audit with the "Progress since" section. The re-audit is what turns a one-off into a relationship.
- **Offer 2: managed change control.** Hourly fleet runs, risky-change alerts to the client's chat or SIEM, daily vulnerability refresh, and a monthly report. This is a monthly fee.
- **Offer 3: end-of-support sweep.** With FortiOS 7.2 out of support since 30 September 2026, many organizations run unsupported firewalls. A one-day fleet sweep that lists unsupported devices, exploited CVEs and the upgrade path is an easy first sale that leads to Offer 1.
- **Targets.** Mid-market organizations under audit pressure: ISO 27001, PCI DSS, health-sector and government suppliers. The CIS and compliance mapping speaks their language, and "on-prem, no cloud, read-only" removes the security objection.
- **Channel.** Fortinet partners and MSPs, who have many FortiGates and no time to audit them. Give them the fleet dashboard under their own name (the palettes make a quick re-brand possible).
- **Demo.** A `--redact` report from a lab or home config. Never show a client's report to another client.
- **Competition.** At the high end are AlgoSec and Tufin (both Israeli). Fortinet's own tools are FortiManager policy checks and the Security Rating, which needs a license and an internet connection. The gap to own is a fast, affordable, offline audit with client-ready reporting.

## Product, in priority order

1. **Check Point adapter.** Check Point is everywhere in Israel. The snapshot model and the checks are vendor-neutral, so a Check Point Management API adapter reuses most of the engine and roughly doubles the addressable market.
2. **Hebrew report (`--lang he`, RTL).** A differentiator for Israeli management and regulators that international tools don't offer.
3. **Profile quality checks.** IPS sensors in monitor mode or without critical signatures, antivirus not blocking, web filter allowing high-risk categories, application control not blocking high-risk categories (CIS 4.4.1, 4.4.2), SSL inspection coverage. This is the next layer of the best-practice baseline.
4. **Fortinet PSIRT feed next to NVD.** Fortinet publishes advisories monthly with fixed versions; NVD sometimes lags or lacks version ranges. Read the PSIRT RSS feed to catch CVEs sooner and to name the minimum fixed build in the report.
5. **FortiManager source.** Pull policy packages for many devices through the FortiManager JSON-RPC API. This is how MSPs work.
6. **Consolidation suggestions.** Rules that differ in one dimension only and can be merged, and partial overlaps between accept and deny rules.
7. **Change workflow.** A web UI with roles, change requests linked to tickets, and approval before a remediation script runs.
8. **Packaging and licensing.** A Docker image or OVA for appliance-style installs. Add signed license files once there are paying customers; contracts are enough before that.

## Done

- 0.4: best-practice baseline (37 practices with evidence), 35 new checks (device hardening, logging, profiles, firmware), FortiOS lifecycle, NVD/CISA KEV lookup with cache, quick wins, CIS mapping, effort tags, five palettes in light and dark, hardening-drift alerts.
- 0.3: report redesign, dark mode, internet-facing interface detection with reasons and overrides.
- 0.2: fleet mode, change tracking with attribution, alerts, usage import, redaction.
