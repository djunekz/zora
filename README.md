# ZORA

**A modular OSINT and network-reconnaissance toolkit, built in pure Python.**

ZORA bundles 43 individual modules — IP/domain/email/phone/username
intelligence, DNS and certificate analysis, port scanning, web technology
fingerprinting, breach/leak lookup links, and more — behind a single
interactive menu or a scriptable CLI.

```
┌─ CORE OSINT
│   1  IP Intelligence              Multi-source IP + Shodan + BGP + ports
│   2  Domain Intelligence          WHOIS, DNS, SSL, subdomains, headers, tech
│   3  Email Intelligence           MX, SPF, DMARC, DKIM, disposable, SMTP
│   4  Username OSINT               50+ platforms, soft-404 aware
│   5  Phone Intelligence           Country, carrier, format, lookups
└─ ... 37 more modules across Network, Web, Security, People, and Tools
```

> **Before you scan anything that isn't yours:** several modules are active
> and intrusive (port scanning, directory brute-forcing, SSRF/redirect
> testing, zone-transfer attempts). Read [`SECURITY.md`](SECURITY.md) first.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
  - [Linux / macOS](#linux--macos)
  - [Termux (Android)](#termux-android)
- [Usage](#usage)
  - [Interactive menu](#interactive-menu)
  - [Direct CLI](#direct-cli)
- [Module Reference](#module-reference)
- [Project Structure](#project-structure)
- [Exporting a Report](#exporting-a-report)
- [Design Notes](#design-notes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

---

## Requirements

- Python **3.10+** (Python 3.9 reached end-of-life in October 2025 and is no longer supported, since some dependencies have already dropped it)
- `phonenumbers` — accurate, offline phone number parsing/validation
- `dnspython` — pure-Python DNS resolution (no `dig` binary required)

Both are listed in [`requirements.txt`](requirements.txt).

## Installation

### Quick install (recommended)

Works on Linux, macOS, and Termux — the script detects the environment,
installs Python if needed (Termux only), installs dependencies with the
correct fallback for "externally-managed-environment" systems, verifies every
module imports correctly, and installs a `zora` command.

```bash
git clone https://github.com/djunekz/zora.git
cd zora
chmod +x install.sh
./install.sh
```

Then run it with:

```bash
zora
```

To remove the `zora` command later:

```bash
./uninstall.sh
```

This only removes the launcher command, not the cloned folder itself, and it
will ask before removing the `phonenumbers`/`dnspython` packages (in case
something else on your system depends on them).

### Manual install

```bash
git clone https://github.com/djunekz/zora.git
cd zora
pip install -r requirements.txt
python -m zora.main
```

On Linux distributions that refuse `pip install` with an
`externally-managed-environment` error, use
`pip install --break-system-packages -r requirements.txt`, or create a
virtual environment first (`python3 -m venv .venv && source .venv/bin/activate`).

### Termux (Android) notes

ZORA is built and tested to run cleanly on Termux, including on devices
without root. WHOIS, DNS resolution, and ARP/route lookups all work out of
the box with no extra `pkg install` needed — these were historically
implemented by shelling out to binaries (`whois`, `dig`, `arp`, `route`) that
are **not** preinstalled on Termux, and have since been reimplemented in pure
Python (see [`CHANGELOG.md`](CHANGELOG.md)).

One optional package improves accuracy further:

```bash
pkg install termux-api   # accurate WiFi SSID/signal in "Local Network Scanner"
                         # (also install the Termux:API companion app)
```

## Usage

### Interactive menu

```bash
python -m zora.main
```

This prints the banner and the full numbered menu (0–43). Pick a number,
supply the target when prompted, and the module runs immediately.

### Direct CLI

For scripting or quick one-off lookups, a subset of modules can be invoked
directly without going through the menu:

```bash
python -m zora.main <module> <target> [extra]
```

| Module keyword | Example |
|---|---|
| `ip` | `python -m zora.main ip 1.1.1.1` |
| `domain` | `python -m zora.main domain example.com` |
| `email` | `python -m zora.main email test@example.com` |
| `username` | `python -m zora.main username johndoe` |
| `phone` | `python -m zora.main phone +6285645558880` |
| `port` | `python -m zora.main port example.com 1-1000` |
| `cidr` | `python -m zora.main cidr 192.168.1.0/24` |
| `dns` | `python -m zora.main dns example.com` |
| `subdomain` | `python -m zora.main subdomain example.com` |
| `ssl` | `python -m zora.main ssl example.com` |
| `whois` | `python -m zora.main whois example.com` |
| `waf` | `python -m zora.main waf example.com` |
| `headers` | `python -m zora.main headers example.com` |
| `cms` | `python -m zora.main cms example.com` |
| `dirbrute` | `python -m zora.main dirbrute example.com` |
| `typosquat` | `python -m zora.main typosquat example.com` |
| `update` | `python -m zora.main update` |

Any other module (the remaining ~27) is reachable through the interactive
menu by its number.

## Module Reference

### Core OSINT
| # | Module | What it does |
|---|---|---|
| 1 | IP Intelligence | Multi-source IP geolocation, ASN/BGP, open ports, risk scoring |
| 2 | Domain Intelligence | WHOIS, DNS records, SPF/DMARC/BIMI, SSL, subdomains, tech stack |
| 3 | Email Intelligence | MX records, SPF/DMARC/DKIM, disposable-email check, SMTP connectivity |
| 4 | Username OSINT | Checks 50+ platforms, with baseline calibration to filter soft-404 false positives |
| 5 | Phone Intelligence | Country/carrier/line-type detection via `phonenumbers`, reverse-lookup links |

### Network & Infrastructure
| # | Module | What it does |
|---|---|---|
| 6 | Advanced Port Scanner | Threaded TCP scan with service/banner grabbing |
| 7 | CIDR / Network Scan | Live host discovery across an IP range |
| 8 | DNS Full Analyzer | All record types, multi-resolver propagation check, DNSSEC |
| 9 | Subdomain Scanner | Wordlist brute force + a real AXFR zone-transfer attempt |
| 10 | BGP / ASN Lookup | ASN details, announced prefixes, routing info |
| 11 | Traceroute + Geo | Hop-by-hop trace with per-hop geolocation |
| 12 | Network Utilities | Public IP, local IP/hostname, IPv6 connectivity, latency to major resolvers |
| 13 | IPv6 Deep Scanner | AAAA records, IPv6 port checks, IPv6 connectivity |
| 14 | Advanced Banner Grabber | Multi-protocol service banners + TLS fingerprint |
| 15 | Network Diagnostics | Ping statistics, TCP handshake timing, jitter, reverse DNS |
| 16 | Local Network Scanner | Local interfaces, WiFi info (via Termux:API when available), ARP cache, default gateway |

### Web & Analysis
| # | Module | What it does |
|---|---|---|
| 17 | Web Tech Profiler | 50+ technology signatures, robots.txt, sitemap |
| 18 | SSL/TLS Deep Analyzer | Certificate details, CT logs, cipher suite, expiry |
| 19 | URL Metadata Extractor | Open Graph/Twitter tags, page stats, flagged HTML comments |
| 20 | WHOIS + Domain History | Full WHOIS, Wayback Machine snapshots, crt.sh history |
| 21 | URL / Link Deep Analyzer | Decomposes a URL, flags suspicious patterns, VirusTotal link |

### Security & Vulnerability
| # | Module | What it does |
|---|---|---|
| 22 | WAF / CDN Detector | Signature-based WAF and CDN fingerprinting |
| 23 | CVE / Vuln Lookup | Links into NVD, Exploit-DB, and OSV for a given product/CVE |
| 24 | HTTP Header Auditor | Security header coverage, grading, cookie flag check |
| 25 | CMS Vulnerability Scanner | WordPress/Joomla/Drupal path probing, exposed-file detection |
| 26 | Open Redirect & SSRF Tester | Follows redirect chains, generates SSRF test payloads |
| 27 | Directory Brute Forcer | Threaded wordlist brute force with wildcard/soft-404 detection |
| 28 | DNS Takeover Checker | CNAME dangling detection against known vulnerable service signatures |
| 29 | API Endpoint Finder | Probes common API paths, including GraphQL introspection |
| 30 | Tor/Proxy/VPN Checker | Tor exit-node DNS check, DNSBL lookups, IP reputation |
| 31 | Shodan Alternatives | InternetDB, GreyNoise Community, plus links to Censys/FOFA/ZoomEye |

### People & Identity OSINT
| # | Module | What it does |
|---|---|---|
| 32 | People / Identity OSINT | People-search engine links, reverse image/face search, email permutations |
| 33 | Dark Web & Paste Monitor | Paste-site/breach-database links, HIBP check (requires an API key for full results) |
| 34 | Certificate Transparency | crt.sh monitoring with apex-domain-aware subdomain filtering, sensitive-subdomain flagging |
| 35 | Typosquatting Checker | Generates common typo variants and checks which ones resolve |
| 36 | Passive DNS History | CT-based subdomain history, Wayback snapshots, current NS records |

### Advanced Tools
| # | Module | What it does |
|---|---|---|
| 37 | Google Dork Generator | Generates targeted Google dork queries for a domain |
| 38 | SOCMINT | Social-media and OSINT-engine search links |
| 39 | Breach Resources | Curated links to breach databases and dark-web monitoring services |
| 40 | Hash & Crypto Toolbox | Hashing, encode/decode, Caesar cipher |
| 41 | Bulk WHOIS Checker | WHOIS + expiry check across multiple domains at once |
| 42 | Report Exporter | Saves everything run so far this session to a JSON report |
| 43 | Check for Updates | Compares your version against the latest GitHub release |

## Project Structure

```
zora/
  core/
    colors.py        ANSI color palette (class C)
    constants.py     VERSION, USER_AGENT, COMMON_PORTS, ...
    validate.py      is_ip / is_domain / is_email / is_phone / is_cidr / ...
    net.py           req_json, req_headers, port_open, dns_query, whois_query, ...
    ui.py            sec/sub/res/bar/th/tr/... output helpers + automatic session log
  modules/           one file per module (ip_intel.py, domain_intel.py, ...)
  main.py            interactive menu + CLI entry point
install.sh
uninstall.sh
requirements.txt
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
CODE_OF_CONDUCT.md
LICENSE
```

Each module is a single class exposing a `run(...)` staticmethod, importing
only from `zora.core`. This keeps modules independent of one another — no
module calls into another module directly — so any one of them can be read,
tested, or modified in isolation.

## Exporting a Report

Every call to the shared output helpers (`sec`, `sub`, `res`, `tr`, `ok`,
`warn`, `err`) is automatically recorded to an in-memory session log for the
lifetime of the process (see `core/ui.py`). Run module **42, Report
Exporter**, at any point and it will serialize everything logged so far in
the session to a timestamped JSON file in the current directory:

```json
{
  "tool": "ZORA v2.0.0",
  "target": "example-session",
  "timestamp": "2026-11-21T03:01:08.821312",
  "session_entries": 5,
  "session_log": [
    { "type": "section", "title": "IP INTELLIGENCE" },
    { "type": "result", "key": "Country", "value": "Indonesia", "status": "info" }
  ],
  "data": {}
}
```

Run other modules first, then export — the report only contains what has
actually been run in the current session.

## Design Notes

- **No silent failures.** Every network call is expected to either produce a
  result or an explicit `warn()`/`err()` message. A blank section with no
  explanation is treated as a bug (see `CHANGELOG.md` for several that were
  fixed this way).
- **No binary dependencies where avoidable.** WHOIS and DNS resolution are
  implemented in pure Python (`core/net.py`) rather than shelling out to
  `whois`/`dig`, because those binaries are commonly missing on minimal
  environments like Termux.
- **No inline comments or docstrings.** This is an intentional style choice
  for this codebase — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for the
  reasoning and the expected alternative (clear naming, small functions).
- **Differential/baseline checks over raw status codes.** Several detection
  modules (username existence, directory brute-forcing, API endpoint
  discovery) compare a target's response against a deliberately-invalid probe
  first, to avoid false positives on servers that return `200 OK` for
  everything (a very common pattern on modern SPA/catch-all deployments).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| A section shows a `!` warning instead of data | The underlying lookup genuinely failed (network, rate limit, or missing optional dependency) | Read the warning text — it states the reason, not just "no data" |
| WiFi info has no SSID on Termux | `termux-api` package / Termux:API app not installed | `pkg install termux-api` and install the Termux:API companion app |
| `ModuleNotFoundError: phonenumbers` or `dns` | Dependencies not installed | `pip install -r requirements.txt` |
| Traceroute module produces no hops | `traceroute` binary not installed (common on Termux) | `pkg install traceroute`, or use module 15 (Network Diagnostics) / module 1 (IP Intelligence) instead |

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the module structure, code
style, and how to submit a fix or a new module.

## Security

See [`SECURITY.md`](SECURITY.md) for responsible-use guidance on the
intrusive modules, and the process for reporting a security issue in ZORA
itself.

## License

Released under the [MIT License](LICENSE).
