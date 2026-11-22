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

printf "%s\n" "${BOLD}=== ZORA uninstaller ===${RESET}"

IS_TERMUX=0
if [ -n "${PREFIX:-}" ] && [ -d "/data/data/com.termux" ]; then
    IS_TERMUX=1
fi

if [ "$IS_TERMUX" -eq 1 ]; then
    BIN_DIR="$PREFIX/bin"
else
    BIN_DIR="$HOME/.local/bin"
fi

WRAPPER="$BIN_DIR/zora"
if [ -f "$WRAPPER" ]; then
    rm -f "$WRAPPER"
    ok "Removed launcher: $WRAPPER"
else
    info "No launcher found at $WRAPPER (nothing to remove there)."
fi

PURGE_DEPS=0
if [ "${1:-}" = "--purge-deps" ]; then
    PURGE_DEPS=1
elif [ -t 0 ]; then
    printf "Also remove the Python packages 'phonenumbers' and 'dnspython'? [y/N] "
    read -r REPLY
    case "$REPLY" in
        [yY]|[yY][eE][sS]) PURGE_DEPS=1 ;;
    esac
fi

if [ "$PURGE_DEPS" -eq 1 ]; then
    warn "Removing phonenumbers and dnspython — skip this if another tool on this system depends on them."
    python3 -m pip uninstall -y phonenumbers dnspython >/dev/null 2>&1 \
        && ok "Removed phonenumbers and dnspython." \
        || warn "Could not remove them automatically — run manually: python3 -m pip uninstall phonenumbers dnspython"
else
    info "Leaving phonenumbers/dnspython installed (they may be used by other projects)."
    info "To remove them later: python3 -m pip uninstall phonenumbers dnspython"
fi

printf "\n%s\n" "${BOLD}=== Uninstall complete ===${RESET}"
info "This only removed the 'zora' launcher command. The source folder at:"
info "    $REPO_ROOT"
info "was left untouched — delete it manually if you no longer need it."
