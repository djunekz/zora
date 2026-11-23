# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to semantic versioning.

## [Unreleased]

### Removed
- `phone_intel.py` - removed `COUNTRY_CODES` dict, duplicated by `PHONE_DB` and never referenced anywhere (dead code)
- `phone_intel.py` - removed dead variables `full`, `is_mobile`, `qn` left over from the pre-`phonenumbers` implementation

### Added
- `update_checker.py` (menu 43 / CLI `update`) - checks the latest GitHub release for `djunekz/zora` and compares it against the running version
- `.gitignore`, `LICENSE` (MIT), `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
- `install.sh` / `uninstall.sh` - environment-aware installer with `externally-managed-environment` (PEP 668) fallback handling, an import smoke test after install, and a `zora` launcher command
- `.github/ISSUE_TEMPLATE/` - bug report, feature request, and accuracy report (false positive/negative) forms, plus issue-template chooser config
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/workflows/ci.yml` - syntax/import smoke test matrix, `install.sh`/`uninstall.sh` end-to-end test, and a check against committing runtime report artifacts
- `.github/workflows/codeql.yml`, `dependency-review.yml`, `stale.yml`
- `.github/workflows/auto-release.yml` - on a `vX.X.X` tag push, creates a GitHub Release named "Zora vX.X.X" with its body pulled from the matching `## [vX.X.X]` section of `CHANGELOG.md` (falls back to `## [Unreleased]` if that section doesn't exist yet)
- `.github/scripts/extract_changelog.py` - extracts a single version's section from `CHANGELOG.md` for the release workflow above
- `.github/dependabot.yml` - weekly dependency update checks for `pip` (`requirements.txt`) and GitHub Actions
- Project restructured from a single 3344-line file into a modular package: `core/` (colors, constants, validate, net, ui) and `modules/` (one file per module, 42 total)
- `main.py` - direct CLI invocation (`python -m zora.main <module> <target>`) alongside the interactive menu
- `requirements.txt` - declares new dependencies: `phonenumbers`, `dnspython`
- `core/net.py` - `whois_query()` / `_whois_raw()`, a pure-Python WHOIS client (raw socket, port 43) replacing the `whois` binary dependency
- `core/net.py` - `dns_query()` / `dns_query_raw()` rebuilt on `dnspython`, replacing the `dig` binary dependency
- `core/ui.py` - automatic session log (`get_session_log`, `clear_session_log`) capturing every `sec()/sub()/res()/tr()/ok()/warn()/err()` call
- `local_net_scanner.py` - pure-Python fallback via `/proc/net/arp` and `/proc/net/route` when the `arp`/`route` binaries are unavailable
- `local_net_scanner.py` - `termux-wifi-connectioninfo` (Termux:API) support for accurate SSID/BSSID/RSSI/link speed
- `username_osint.py` - per-platform baseline calibration (probes a known-nonexistent username) to detect soft-404 responses
- `dir_brute.py`, `api_finder.py` - wildcard/soft-404 detection via baseline differential comparison
- `subdomain_scanner.py` - real AXFR zone-transfer test implemented with `dnspython`

### Changed
- `port_scanner.py`, `subdomain_scanner.py`, `dir_brute.py`, `api_finder.py`, `username_osint.py`, `typosquat_checker.py` - manual batched threading replaced with `concurrent.futures.ThreadPoolExecutor`
- `dns_analyzer.py`, `proxy_checker.py` - direct `dig` subprocess calls replaced with the centralized `dns_query()`
- `phone_intel.py` - number validation engine replaced entirely with the `phonenumbers` library, removing the homegrown `PHONE_DB` / `NUM_LENGTH` tables
- All modules - comments (`#`) and docstrings (`"""..."""`) stripped via `ast` + `tokenize` (not regex), so strings/URLs containing `#` were not corrupted

### Fixed
- All 43 module files - replaced the blanket, copy-pasted import header (`import re / socket / ssl / json / time / base64 / hashlib / threading / ipaddress / subprocess / urllib.*` and `from zora.core import *`) with precise, per-file imports based on actual usage; this was the root cause of the vast majority of CodeQL's 579 findings (unused imports + star-import namespace pollution), confirmed by `pyflakes` going from hundreds of entries to zero
- `zora/core/__init__.py`, `zora/modules/__init__.py` - added `__all__` to mark these re-export files' imports as intentional, so linters stop flagging them as unused
- `ssl_analyzer.py`, `domain_intel.py`, `banner_grabber.py` - explicitly set `ctx.minimum_version = ssl.TLSVersion.TLSv1_2` on every `ssl.create_default_context()` call (CodeQL: "Use of insecure SSL/TLS version", High severity) instead of relying on the Python version's implicit default, which isn't guaranteed consistent across the 3.9–3.12 range this project supports
- `phone_intel.py` - `CURRENCY_BY_REGION` had the `"PK"` key defined twice (CodeQL: "Duplicate key in dict literal"); removed the duplicate
- `net_utils.py` - `local_ip` was assigned an initial `"N/A"` that was always overwritten before being read on every code path (CodeQL: "Variable defined multiple times"); removed the dead initial assignment and tightened the inner bare `except:` to `except Exception:`
- `header_auditor.py` - CodeQL flagged a potential `TypeError` ("Membership test with a non-container") on `"same-origin" in v` if a header value were ever not a string; the call site already guarded this with a try/except, but the header value is now explicitly coerced with `str(...)` at the point it's read, so every `good()` lambda always receives a string
- `local_net_scanner.py` - a local variable named `tw` (holding the Termux WiFi JSON result) shadowed the imported `tw()` terminal-width helper within the same function, making the import dead and the code confusing; renamed the variable to `wifi_json`
- `main.py` - removed an import of `sec` that was no longer used after prior edits
- `requirements.txt` - was missing `dnspython`, which `core/net.py` imports directly (`import dns.resolver`); a fresh `pip install -r requirements.txt` would succeed but every DNS/WHOIS-dependent module would then raise `ModuleNotFoundError: No module named 'dns'` at runtime
- `.github/workflows/ci.yml` - the import-smoke-test step used an indented heredoc (`<<'PYEOF' ... PYEOF`) inside a YAML block scalar; since the closing delimiter wasn't at column 0, bash never recognized it as the end of the heredoc, which fed the literal (indented) Python source to the interpreter and raised `IndentationError` on every Python version — replaced with a checked-in script (`.github/scripts/check_imports.py`)
- `.github/scripts/check_imports.py` - regression from the fix above: running `python .github/scripts/check_imports.py` puts that script's own directory on `sys.path[0]` instead of the repo root, so `import zora.modules` failed with `ModuleNotFoundError: No module named 'zora'`; added `sys.path.insert(0, os.getcwd())`
- `.github/workflows/ci.yml` - the Python 3.9 matrix job failed on `ubuntu-latest` (Ubuntu 26.04) because `actions/setup-python` has no 3.9 x64 build for that image; pinned that job to `ubuntu-22.04`, which still has it
- `.github/ISSUE_TEMPLATE/config.yml` - replaced the `OWNER/REPO` placeholder with the actual repository (`djunekz/zora`)
- `report_exporter.py` - always wrote an empty JSON report because it never received scan results from other modules; now pulls automatically from the session log
- `username_osint.py` - a profile was marked "found" based solely on HTTP 200, even though many platforms (Instagram, TikTok, X/Twitter, Telegram) always return 200 for nonexistent usernames (soft-404)
- `dir_brute.py`, `api_finder.py` - the same soft-404 issue: a catch-all/SPA server made every wordlist entry read as "found"
- `local_net_scanner.py` - WiFi Info reported "No wireless interface detected" while `wlan0` was clearly active in the interfaces list above it; ARP Cache and Default Gateway rendered empty with no error message
- `phone_intel.py` - a valid number was flagged "Length MISMATCH" / "Risk: MEDIUM" because the digit count including the country code was compared against a value meant for the local number only; local-format numbers (leading `0`) failed to resolve a country at all
- `cms_scanner.py` - sensitive files (`.env`, config backups) were always flagged HIGH RISK based on the label text, regardless of whether the HTTP status was actually 200
- `subdomain_scanner.py` - the AXFR zone-transfer check always reported "Refused (good)" even when `dig` was missing and the test never actually ran (false sense of security)
- `proxy_checker.py` - DNSBL and Tor-exit checks always reported "Clean" even when `dig` was missing and the query was never sent (false sense of security)
- `domain_intel.py` - WHOIS showed only the first of several Name Server lines; "external domain" detection used a substring match that could misclassify unrelated domains (e.g. `evilexample.com` matching `example.com`); SSL certificate expiry was computed against local time instead of UTC
- `ct_monitor.py`, `passive_dns.py` - the same substring-match bug when filtering subdomains from Certificate Transparency data
- `whois_history.py`, `bulk_whois.py`, `ssl_analyzer.py` - the same local-time-vs-UTC bug when computing domain age / certificate expiry
- `header_auditor.py`, `url_analyzer.py` - an HTTP status of `0` (total connection failure) was displayed in "success" color
- `waf_detector.py` - the Varnish signature `"via: varnish"` could never match due to a formatting mismatch in the comparison string
- `redirect_tester.py` - an HTTP connection was left unclosed on one code path (minor resource leak)
- `net_utils.py` - "Local IP" used `gethostbyname(hostname)`, which commonly returns `127.0.0.1` on Android/Termux instead of the real network IP
- `geo_traceroute.py` - the hop number and IP line was skipped entirely when ping timing couldn't be parsed, leaving an orphaned location line
- `metadata_extractor.py` - the Open Graph/Twitter meta-tag regex only matched when the `property` attribute appeared before `content`
- `email_intel.py`, `people_osint.py` - the Email Permutations section rendered silently empty with no explanation when the name/username had no separator

### Known limitations
- `geo_traceroute.py` depends on the `traceroute` binary, which is likely also unavailable by default on Termux (same class of issue as `dig`/`whois`/`arp`). A pure-Python replacement would require raw sockets/root privileges that haven't been verified on-device.
