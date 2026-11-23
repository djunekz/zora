import urllib.request
import urllib.parse
import urllib.error

from zora.core import C, dns_query, ok, req_json, res, sec, sub, th, tr


class PassiveDNS:
    @staticmethod
    def run(domain):
        sec("PASSIVE DNS & HISTORICAL IP", "🕰️")
        q=urllib.parse.quote(domain)

        sub("📜 CT-Based Subdomain History")
        crt=req_json(f"https://crt.sh/?q=%.{domain}&output=json")
        if crt and isinstance(crt,list):
            sub_hist=set()
            apex = domain.lower()
            for entry in crt[:50]:
                for n in entry.get("name_value","").split("\n"):
                    n=n.strip().lstrip("*.").lower()
                    if n and (n == apex or n.endswith("." + apex)):
                        sub_hist.add(n)
            res("Unique Subdomains (CT)",str(len(sub_hist)),"info")
            for s in sorted(sub_hist)[:20]: print(f"    {C.GRAY}•{C.R} {C.BWHITE}{s}{C.R}")

        sub("🕰️  Wayback Machine Snapshots")
        wb=req_json(f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&fl=timestamp,original&limit=10&collapse=digest")
        if wb and len(wb)>1:
            th(["Timestamp","URL"])
            for row in wb[1:11]:
                ts=row[0]; ts_fmt=f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
                tr([ts_fmt,row[1][:65]],"found")

        sub("🔍 External History Tools")
        for nm,url in [
            ("ViewDNS IP History",  f"https://viewdns.info/iphistory/?domain={domain}"),
            ("SecurityTrails",      f"https://securitytrails.com/domain/{domain}/dns"),
            ("DNSdumpster",         "https://dnsdumpster.com/"),
            ("RiskIQ PassiveDNS",   f"https://community.riskiq.com/research?query={q}"),
            ("Shodan Facets",       f"https://www.shodan.io/search?query=hostname:{domain}"),
        ]: print(f"    {C.BCYAN}•{C.R} {C.BOLD}{nm:<28}{C.R} {C.GRAY}{url[:65]}{C.R}")

        sub("📡 Current NS Records")
        ns=dns_query(domain,"NS")
        res("Name Servers",", ".join(ns) if ns else "?","info")
        ok("Passive DNS done")
