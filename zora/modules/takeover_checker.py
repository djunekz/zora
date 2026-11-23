import socket

from zora.core import C, dns_query, ok, req_text, res, sec, sub, warn


TAKEOVER_SIGS = {
    "GitHub Pages":  ["There isn't a GitHub Pages site here"],
    "Heroku":        ["No such app","herokucdn.com"],
    "Shopify":       ["Sorry, this shop is currently unavailable"],
    "Fastly":        ["Fastly error: unknown domain"],
    "Surge.sh":      ["project not found"],
    "Tumblr":        ["There's nothing here"],
    "Zendesk":       ["Help Center Closed"],
    "Statuspage.io": ["Better luck next time"],
}

class TakeoverChecker:
    @staticmethod
    def run(domain):
        sec("DNS TAKEOVER CHECKER", "⚠️")
        sub("🔗 CNAME Chain Analysis")
        cname = dns_query(domain,"CNAME")
        if cname:
            res("CNAME", cname[0], "warning")
            try:
                ip = socket.gethostbyname(cname[0].rstrip("."))
                res("CNAME Resolves", ip, "success")
            except:
                res("CNAME Resolves","NXDOMAIN — TAKEOVER POSSIBLE!","error")
                warn(f"{cname[0]} does not resolve!")
        else:
            a = dns_query(domain,"A")
            res("A Records",", ".join(a) if a else "None","info" if a else "warning")

        sub("🔍 Takeover Signature Check")
        html = req_text(f"https://{domain}") or req_text(f"http://{domain}")
        vuln = []
        if html:
            for svc,sigs in TAKEOVER_SIGS.items():
                if any(s.lower() in html.lower() for s in sigs):
                    vuln.append(svc)
                    res(f"VULNERABLE — {svc}","Takeover signature detected!","error")
        if not vuln: ok("No known takeover signatures found")

        sub("📝 Risky Subdomains Check")
        for s in ["dev","staging","test","beta","old","demo","uat","qa","temp"]:
            fqdn = f"{s}.{domain}"
            try:
                socket.gethostbyname(fqdn)
                hs = req_text(f"http://{fqdn}")
                v = any(any(sig.lower() in (hs or "").lower() for sig in sigs) for sigs in TAKEOVER_SIGS.values())
                status = f"{C.BRED}POSSIBLE TAKEOVER{C.R}" if v else f"{C.BGREEN}Resolves OK{C.R}"
            except:
                status = f"{C.BYELLOW}NXDOMAIN{C.R}"
            print(f"    {C.GRAY}•{C.R} {fqdn:<40} {status}")
        ok("Takeover Check done")
