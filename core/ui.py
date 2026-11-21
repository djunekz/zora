import os
import time

from zora.core.colors import C
from zora.core.constants import VERSION, CODENAME, DEVELOPER

_SESSION_LOG = []


def get_session_log():
    return list(_SESSION_LOG)


def clear_session_log():
    _SESSION_LOG.clear()


def _log(entry_type, **fields):
    entry = {"type": entry_type}
    entry.update(fields)
    _SESSION_LOG.append(entry)


def tw():
    try: return os.get_terminal_size().columns
    except: return 100

def print_banner():
    w = tw()
    print(f"""
{C.BCYAN}{C.BOLD}
  ██████╗ ██████╗ ██████╗  █████╗  {C.BMAGENTA}v{VERSION} {CODENAME}{C.BCYAN}
 ╚══███╔╝██╔═══██╗██╔══██╗██╔══██╗ {C.GRAY}The Most Complete OSINT Framework{C.BCYAN}
   ███╔╝ ██║   ██║██████╔╝███████║ {C.GRAY}42 Modules • 500+ Data Points{C.BCYAN}
  ███╔╝  ██║   ██║██╔══██╗██╔══██║ {C.GRAY}Security • OSINT • Recon • Intel{C.BCYAN}
 ███████╗╚██████╔╝██║  ██║██║  ██║ {C.GRAY}Developer: {C.BMAGENTA}{DEVELOPER}{C.BCYAN}
 ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝{C.R}
{C.GRAY}{'═'*w}{C.R}""")

def sec(title, icon="🔍"):
    w = tw()
    _log("section", title=title)
    print(f"\n{C.BG_CYAN}{C.BLACK}{C.BOLD} {icon} {title} {C.R}")
    print(f"{C.CYAN}{'─'*w}{C.R}")

def sub(title):
    _log("subsection", title=title)
    print(f"\n  {C.BBLUE}◈{C.R} {C.BOLD}{C.BWHITE}{title}{C.R}")

def inf(label, value, indent=4):
    sp = " "*indent
    _log("info", label=label, value=str(value))
    print(f"{sp}{C.GRAY}{label}:{C.R} {C.BWHITE}{value}{C.R}")

def ok(msg):
    _log("ok", message=msg)
    print(f"  {C.BG_GREEN}{C.BLACK}{C.BOLD} ✓ {C.R} {C.BGREEN}{msg}{C.R}")

def warn(msg):
    _log("warning", message=msg)
    print(f"  {C.BG_YELLOW}{C.BLACK}{C.BOLD} ! {C.R} {C.BYELLOW}{msg}{C.R}")

def err(msg):
    _log("error", message=msg)
    print(f"  {C.BG_RED}{C.BLACK}{C.BOLD} ✗ {C.R} {C.BRED}{msg}{C.R}")

def res(key, value, status="info"):
    icons = {"success": f"{C.BGREEN}✓{C.R}", "warning": f"{C.BYELLOW}!{C.R}",
             "error": f"{C.BRED}✗{C.R}", "info": f"{C.BCYAN}•{C.R}"}
    _log("result", key=key, value=str(value), status=status)
    print(f"    {icons.get(status,icons['info'])} {C.BOLD}{key}:{C.R} {C.BWHITE}{value}{C.R}")

def bar(cur, total, prefix="Progress"):
    w = min(45, tw()-35)
    filled = int(w*cur/max(total,1))
    b = "█"*filled + "░"*(w-filled)
    pct = int(100*cur/max(total,1))
    print(f"\r  {C.BCYAN}{prefix}:{C.R} [{C.BGREEN}{b}{C.R}] {C.BWHITE}{pct}%{C.R}", end="", flush=True)
    if cur==total: print()

def dots(msg, dur=0.8):
    for i in range(3):
        print(f"\r  {C.BYELLOW}⟳{C.R} {msg}{'.'*(i+1)}   ", end="", flush=True)
        time.sleep(dur/3)
    print("\r"+" "*(len(msg)+20)+"\r", end="", flush=True)

def th(cols):
    _log("table_header", columns=list(cols))
    cw = (tw()-10)//len(cols)
    print("\n  "+"".join(f"{C.BOLD}{C.BCYAN}{c:<{cw}}{C.R}" for c in cols))
    print(f"  {C.GRAY}{'─'*(tw()-4)}{C.R}")

def tr(vals, status=""):
    _log("table_row", values=[str(v) for v in vals], status=status)
    cw = (tw()-10)//len(vals)
    color = {"found":C.BGREEN,"notfound":C.GRAY,"warn":C.BYELLOW}.get(status,C.BWHITE)
    print("  "+"".join(f"{color}{str(v):<{cw}}{C.R}" for v in vals))
