# Security Policy

## Responsible Use

ZORA is an OSINT and network-reconnaissance toolkit. A number of its modules are
**active and intrusive**, meaning they send real traffic to the target instead
of only reading public, already-published information. Before running any of
the following modules against a host, domain, or network you do not own,
confirm you have **explicit written authorization** to test it:

| Module | Why it's intrusive |
|---|---|
| Port Scanner | Opens TCP connections across a port range |
| Directory Brute Forcer | Sends hundreds of HTTP requests probing for hidden paths |
| Open Redirect & SSRF Tester | Sends crafted redirect/payload requests |
| API Endpoint Finder | Probes dozens of common API paths, including GraphQL introspection |
| DNS Takeover Checker / Subdomain Scanner | Attempts DNS zone transfers (AXFR) |
| CMS Vulnerability Scanner | Probes for known exposed files and admin paths |
| Local Network Scanner | Reads ARP cache, routing table, and WiFi state of the host device |

Running these against systems you do not control, without permission, may
violate computer-misuse laws in your jurisdiction, including (but not limited
to) the U.S. Computer Fraud and Abuse Act, the UK Computer Misuse Act, the EU's
national cybercrime statutes, and Indonesia's UU ITE. **You are solely
responsible for how you use this tool.** The maintainers and contributors of
this project accept no liability for misuse.

All other modules (WHOIS, DNS record lookups, certificate transparency
monitoring, WHOIS history, breach-database links, social media search links,
and similar) are passive: they only query public third-party services and
read already-published data.

## Supported Versions

| Version | Supported |
|---|---|
| 2.0.x | :white_check_mark: |
| < 2.0 | :x: (legacy single-file release, unsupported) |

## Reporting a Vulnerability

If you find a security issue **in ZORA itself** (e.g. a bug that could let a
scanned target compromise the machine running ZORA, an injection
vulnerability in how input is parsed, or a bug that silently reports false
"safe"/"not vulnerable" results — a false negative — which has safety
implications for the person relying on it):

1. **Do not open a public issue.** Instead, open a private security advisory
   from the repository's **Security** tab (GitHub → Security → Advisories →
   "Report a vulnerability"), or contact a maintainer directly if that option
   is unavailable.
2. Include:
   - A clear description of the issue and its impact.
   - Steps to reproduce (a minimal example is ideal).
   - The affected module(s) and version/commit.
3. You can expect an initial response within **7 days**. Confirmed issues will
   be patched and credited in the next `CHANGELOG.md` entry unless you request
   otherwise.

## Known Limitations (not security issues, but worth knowing)

- Some modules rely on external binaries (e.g. `traceroute`) that may be
  missing on minimal environments like Termux. A missing binary causes that
  specific section to report an explicit warning rather than fail silently —
  but it does mean that check did not run. See `CHANGELOG.md` for which
  binary dependencies have already been replaced with pure-Python
  implementations.
- Signature-based detections (WAF fingerprinting, CMS detection, technology
  profiling) are heuristic and can produce false positives/negatives,
  especially against custom-hardened or heavily obfuscated deployments.
