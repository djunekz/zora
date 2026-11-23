import urllib.request
import urllib.parse
import urllib.error

from zora.core import C, ok, sec, sub


class BreachResources:
    @staticmethod
    def run(query):
        sec("BREACH & DARK WEB RESOURCES", "🚨")
        q=urllib.parse.quote(query)

        sub("🔓 Breach Databases")
        for name,url in [
            ("HaveIBeenPwned",    "https://haveibeenpwned.com/"),
            ("DeHashed",          f"https://dehashed.com/search?query={q}"),
            ("LeakCheck",         "https://leakcheck.io/"),
            ("SnusBase",          "https://snusbase.com/"),
            ("IntelX",            f"https://intelx.io/?s={q}"),
        ]: print(f"  {C.BRED}•{C.R} {C.BOLD}{name:<20}{C.R} {C.GRAY}{url}{C.R}")

        sub("🌑 Dark Web Monitoring")
        for name,url in [
            ("DarkOwl",           "https://www.darkowl.com/"),
            ("Flare.io",          "https://flare.io/"),
            ("SpyCloud",          "https://spycloud.com/"),
        ]: print(f"  {C.BMAGENTA}•{C.R} {C.BOLD}{name:<20}{C.R} {C.GRAY}{url}{C.R}")

        ok("Breach Resources done")
