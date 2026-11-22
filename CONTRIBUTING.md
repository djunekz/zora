# Contributing to ZORA

Thanks for considering a contribution. This project is a modular OSINT/recon
toolkit written in pure Python, organized as one class per file so it stays
easy to navigate and extend.

## Project Layout

```
zora/
  core/              shared building blocks used by every module
    colors.py        ANSI color palette (class C)
    constants.py     VERSION, USER_AGENT, COMMON_PORTS, ...
    validate.py      is_ip / is_domain / is_email / is_phone / ...
    net.py           req_json, req_headers, port_open, dns_query, whois_query, ...
    ui.py            sec/sub/res/bar/th/tr/... terminal output helpers + session log
  modules/           one file per OSINT module (ip_intel.py, domain_intel.py, ...)
  main.py            interactive menu + `python -m zora.main <module> <target>` CLI
```

## Getting Set Up

```bash
git clone <this-repo>
cd zora
pip install -r requirements.txt
python -m zora.main
```

## Adding a New Module

1. Create `zora/modules/your_module.py`. Each module is a single class with a
   `run(...)` staticmethod as its entry point:

   ```python
   from zora.core import *

   class YourModule:
       @staticmethod
       def run(target):
           sec("YOUR MODULE TITLE", "🔍")
           sub("Section name")
           res("Label", "value", "info")
           ok("Done")
   ```

2. Register it in `zora/modules/__init__.py`:

   ```python
   from zora.modules.your_module import YourModule
   ```

3. Add a menu entry and dispatch line in `zora/main.py` (both the numbered
   menu text and the `elif ch=="N":` branch). If the module makes sense as a
   non-interactive command, add it to the `direct` dict in `run_cli()` too.

4. If your module depends on an external binary (e.g. shelling out to a CLI
   tool), check first whether a pure-Python equivalent already exists in
   `core/net.py` (`dns_query`, `whois_query`, `port_open`, ...), or whether one
   should be added there instead of adding a new binary dependency — several
   binaries (`dig`, `whois`, `arp`, `route`) are **not installed by default on
   Termux/Android**, which is a common runtime for this tool, so pure-Python
   implementations are strongly preferred over shelling out.

## Code Style

- **No inline comments or docstrings.** This is an intentional, existing
  convention across the codebase (not a universal Python best practice) —
  keep code self-explanatory through clear naming, small functions, and
  early returns instead.
- Follow the existing output helpers (`sec`, `sub`, `res`, `ok`, `warn`,
  `err`, `th`/`tr`) rather than raw `print()`, so your module's output is
  captured by the session log (`core/ui.py`) and can be exported by
  `ReportExporter`.
- Prefer `concurrent.futures.ThreadPoolExecutor` over manual thread
  batching for anything that fans out many network requests.
- Never assume a request succeeds. Every network call should degrade
  gracefully and surface an explicit `warn()`/`err()` message rather than
  silently rendering an empty section — a silent failure that looks like "no
  data found" is worse than a visible one.

## Fixing a Bug

1. Reproduce it and identify the root cause before patching — several past
   bugs in this project turned out to be the same root cause appearing in
   multiple modules (see `CHANGELOG.md`), so check whether a fix belongs in a
   shared `core/` helper instead of a single module.
2. Add or update a short manual verification (a before/after example in your
   pull request description is enough; this project does not yet have an
   automated test suite).
3. Document the fix in `CHANGELOG.md` under `## [Unreleased]`.

## Reporting Bugs / Requesting Features

Open an issue describing:
- What you expected to happen.
- What actually happened (include the exact module, input, and output).
- Your environment (OS/Termux version, Python version).

## Releasing a New Version

Releases are automated (`.github/workflows/auto-release.yml`): pushing a tag
matching `vX.X.X` creates a GitHub Release named `Zora vX.X.X`, with its body
pulled straight from `CHANGELOG.md`. For that to produce the right content:

1. Before tagging, rename the `## [Unreleased]` heading to the version being
   released, with today's date, e.g.:

   ```markdown
   ## [v2.1.0] - 2026-12-01
   ```

2. Add a fresh empty `## [Unreleased]` heading above it for whatever comes
   next.
3. Commit that change, then tag and push:

   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

The workflow matches the tag (`v2.1.0`) against a `## [v2.1.0]` (or
`## [2.1.0]`, the leading `v` is optional) heading in `CHANGELOG.md` and uses
everything under it, up to the next `## [` heading, as the release body. If no
matching heading exists yet (e.g. the very first release, or the heading
rename was forgotten), it falls back to whatever is currently under
`## [Unreleased]` instead of failing.

## Security Issues

Do **not** open a public issue for a security-relevant bug. See
[`SECURITY.md`](SECURITY.md) for the private reporting process.

## Responsible Use

Several modules are intentionally intrusive (port scanning, directory
brute-forcing, SSRF/redirect testing, and similar). Contributions that make
these checks more invasive, or that add new attack/exploitation capability
rather than fixing accuracy or reliability, are out of scope for this
project. See [`SECURITY.md`](SECURITY.md) for details on what each module
does and the legal considerations around using them.
