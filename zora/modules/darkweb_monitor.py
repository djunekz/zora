import urllib.request
import urllib.parse
import urllib.error

from zora.core import C, ok, req_json, res, sec, sub


class DarkWebMonitor:
    @staticmethod
    def run(query):
        sec("DARK WEB & PASTE SITE MONITOR", "🌑")
        q = urllib.parse.quote(query)

        sub("📋 Paste Sites")
        for nm,url in [("Pastebin",f"https://pastebin.com/search?q={q}"),
                       ("Ghostbin","https://ghostbin.com/"),("Rentry.co","https://rentry.co/"),
                       ("ControlC","https://controlc.com/"),("Dpaste","https://dpaste.org/")]:
            print(f"    {C.BYELLOW}•{C.R} {C.BOLD}{nm:<16}{C.R} {C.GRAY}{url}{C.R}")

        sub("🚨 Breach & Leak Databases")
        for nm,url in [
            ("HaveIBeenPwned",  f"https://haveibeenpwned.com/account/{q}"),
            ("DeHashed",        f"https://dehashed.com/search?query={q}"),
            ("LeakCheck",       "https://leakcheck.io/"),
            ("SnusBase",        "https://snusbase.com/"),
            ("IntelX",          f"https://intelx.io/?s={q}"),
            ("Breachdirectory", "https://breachdirectory.org/"),
            ("WeLeak",          "https://weleakinfo.to/"),
        ]: print(f"    {C.BRED}•{C.R} {C.BOLD}{nm:<20}{C.R} {C.GRAY}{url}{C.R}")

        sub("🌑 Dark Web Monitoring Services")
        for nm,url in [("DarkOwl","https://www.darkowl.com/"),("Flare.io","https://flare.io/"),
                       ("SpyCloud","https://spycloud.com/"),
                       ("Recorded Future","https://www.recordedfuture.com/"),
                       ("Cybersixgill","https://cybersixgill.com/")]:
            print(f"    {C.BMAGENTA}•{C.R} {C.BOLD}{nm:<20}{C.R} {C.GRAY}{url}{C.R}")

        sub("⚡ HIBP Check (email)")
        if "@" in query:
            hibp = req_json(f"https://haveibeenpwned.com/api/v3/breachedaccount/{q}",
                            headers={"hibp-api-key":"demo","User-Agent":"ZORA-OSINT"})
            if hibp and isinstance(hibp,list):
                res("Breaches Found", str(len(hibp)), "error")
                for b in hibp[:5]: print(f"    {C.BRED}• {b.get('Name','?')}{C.R} — {C.DIM}{b.get('BreachDate','?')}{C.R}")
            else:
                res("HIBP","No data (API key required for full access)","warning")
        ok("Dark Web Monitor done")
