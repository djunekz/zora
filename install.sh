#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

RED="$(printf '\033[31m')"
GREEN="$(printf '\033[32m')"
YELLOW="$(printf '\033[33m')"
CYAN="$(printf '\033[36m')"
BOLD="$(printf '\033[1m')"
RESET="$(printf '\033[0m')"

info()  { printf "%s[*]%s %s\n" "$CYAN" "$RESET" "$1"; }
ok()    { printf "%s[OK]%s %s\n" "$GREEN" "$RESET" "$1"; }
warn()  { printf "%s[!]%s %s\n" "$YELLOW" "$RESET" "$1"; }
fail()  { printf "%s[FAIL]%s %s\n" "$RED" "$RESET" "$1"; exit 1; }

printf "%s\n" "${BOLD}=== ZORA installer ===${RESET}"

IS_TERMUX=0
if [ -n "${PREFIX:-}" ] && [ -d "/data/data/com.termux" ]; then
    IS_TERMUX=1
    info "Termux environment detected."
fi

if ! command -v python3 >/dev/null 2>&1; then
    if [ "$IS_TERMUX" -eq 1 ]; then
        info "python3 not found — installing via pkg..."
        pkg update -y && pkg install -y python || fail "pkg install python failed."
    else
        fail "python3 not found. Install Python 3.10+ with your system's package manager, then re-run this script."
    fi
fi

PY_OK=$(python3 - <<'PYEOF'
import sys
print(1 if sys.version_info >= (3, 10) else 0)
PYEOF
)
if [ "$PY_OK" != "1" ]; then
    fail "Python 3.10+ is required. Found: $(python3 --version 2>&1)"
fi
ok "Using $(python3 --version 2>&1)"

if ! python3 -m pip --version >/dev/null 2>&1; then
    info "pip not found — bootstrapping with ensurepip..."
    python3 -m ensurepip --upgrade >/dev/null 2>&1 || fail "Could not bootstrap pip. Install pip manually and re-run."
fi

REQ_FILE="$REPO_ROOT/requirements.txt"
[ -f "$REQ_FILE" ] || fail "requirements.txt not found at $REQ_FILE"

info "Installing Python dependencies from requirements.txt..."
INSTALL_OK=0

if python3 -m pip install -q -r "$REQ_FILE" 2>/tmp/zora_pip_err.log; then
    INSTALL_OK=1
elif grep -qi "externally-managed-environment" /tmp/zora_pip_err.log 2>/dev/null; then
    warn "This Python is externally managed (PEP 668)."
    warn "Retrying with --break-system-packages (safe for a userland tool like this one)..."
    if python3 -m pip install -q --break-system-packages -r "$REQ_FILE" 2>/tmp/zora_pip_err.log; then
        INSTALL_OK=1
    fi
fi

if [ "$INSTALL_OK" -ne 1 ]; then
    warn "Still failing — retrying with --user..."
    if python3 -m pip install -q --user -r "$REQ_FILE" 2>/tmp/zora_pip_err.log; then
        INSTALL_OK=1
    fi
fi

if [ "$INSTALL_OK" -ne 1 ]; then
    cat /tmp/zora_pip_err.log >&2
    fail "Dependency installation failed. See the pip output above for the exact cause."
fi
rm -f /tmp/zora_pip_err.log
ok "Dependencies installed (phonenumbers, dnspython)."

info "Verifying every module imports correctly..."
IMPORT_CHECK=$(PYTHONPATH="$REPO_ROOT" python3 - <<'PYEOF'
import importlib
import pkgutil
import sys

try:
    import zora.modules as modules_pkg
    count = 0
    for _, name, _ in pkgutil.iter_modules(modules_pkg.__path__):
        importlib.import_module(f"zora.modules.{name}")
        count += 1
    import zora.main
    print(f"OK:{count}")
except Exception as e:
    print(f"FAIL:{type(e).__name__}: {e}")
PYEOF
)

case "$IMPORT_CHECK" in
    OK:*)
        MODULE_COUNT="${IMPORT_CHECK#OK:}"
        ok "$MODULE_COUNT modules + main.py imported successfully."
        ;;
    *)
        fail "Import check failed: ${IMPORT_CHECK#FAIL:}"
        ;;
esac

if [ "$IS_TERMUX" -eq 1 ]; then
    BIN_DIR="$PREFIX/bin"
else
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
fi

WRAPPER="$BIN_DIR/zora"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="$REPO_ROOT\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m zora.main "\$@"
EOF
chmod +x "$WRAPPER"
ok "Installed launcher: $WRAPPER"

if [ "$IS_TERMUX" -eq 1 ] && ! command -v termux-wifi-connectioninfo >/dev/null 2>&1; then
    warn "Tip: run 'pkg install termux-api' (and install the Termux:API app) for accurate WiFi SSID/signal info in module 16."
fi

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        warn "$BIN_DIR is not on your PATH."
        warn "Add this to your shell profile (~/.bashrc, ~/.zshrc, or ~/.profile):"
        printf "    export PATH=\"%s:\$PATH\"\n" "$BIN_DIR"
        ;;
esac

printf "\n%s\n" "${BOLD}=== Install complete ===${RESET}"
printf "Run it with:\n"
printf "    %szora%s                   (if %s is on your PATH)\n" "$GREEN" "$RESET" "$BIN_DIR"
printf "    %spython3 -m zora.main%s   (from %s)\n" "$GREEN" "$RESET" "$REPO_ROOT"
