## Summary

<!-- What does this PR change, and why? -->

## Type of change

- [ ] Bug fix (accuracy, reliability, or crash)
- [ ] New module
- [ ] New data source for an existing module
- [ ] Refactor (no behavior change)
- [ ] Documentation
- [ ] CI / tooling

## Which module(s) does this affect?

<!-- e.g. modules/username_osint.py, core/net.py -->

## How was this tested?

<!--
This project does not yet have an automated test suite. Please describe how
you verified the change manually, e.g.:
- Exact command(s) run and target(s) used (redact anything sensitive)
- Before/after output comparison
- Which environment (Termux / Linux / macOS) you tested on
-->

## Checklist

- [ ] I read [CONTRIBUTING.md](../CONTRIBUTING.md), including the code style
      section (no inline comments/docstrings; use the shared `core/ui.py`
      output helpers, not raw `print()`)
- [ ] If this touches a module that shells out to an external binary, I
      checked whether a pure-Python equivalent in `core/net.py` already
      exists, or should be added instead (several binaries are missing by
      default on Termux — see `CHANGELOG.md`)
- [ ] I added an entry to `CHANGELOG.md` under `## [Unreleased]`
- [ ] If this adds a new module: I registered it in `zora/modules/__init__.py`
      and added a menu entry + dispatch line in `zora/main.py`
- [ ] This does **not** make an existing module more intrusive/offensive, or
      add new attack/exploitation capability (see
      [CONTRIBUTING.md § Responsible Use](../CONTRIBUTING.md#responsible-use))
- [ ] Every new network call degrades gracefully with an explicit
      `warn()`/`err()` message rather than failing silently

## Related issues

<!-- Closes #123 -->
