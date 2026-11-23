import re
from datetime import datetime

from zora.core import C, dots, ok, req_json, res, sec, sub, warn, whois_query


class WHOISHistory:
    @staticmethod
    def run(domain):
        sec("WHOIS + DOMAIN HISTORY", "📋")
        dots("Querying WHOIS")
        whois=whois_query(domain)
        if not whois:
            warn("WHOIS lookup failed (server unreachable or rate-limited)")
        sub("📊 Full WHOIS")
        important=[
            ("Registrar",r"Registrar:\s*(.+)"),
            ("Registrar URL",r"Registrar URL:\s*(.+)"),
            ("Created",r"Creation Date:\s*(.+)"),
            ("Expires",r"Registry Expiry Date:\s*(.+)"),
            ("Updated",r"Updated Date:\s*(.+)"),
            ("Status",r"Domain Status:\s*(.+)"),
            ("Registrant Org",r"Registrant Organization:\s*(.+)"),
            ("Registrant Country",r"Registrant Country:\s*(.+)"),
            ("Abuse Email",r"Registrar Abuse Contact Email:\s*(.+)"),
        ]
        for key,pat in important:
            m=re.findall(pat,whois,re.I)
            if m: res(key,m[0][:70],"info")

        ns=re.findall(r"Name Server:\s*(.+)",whois,re.I)
        if ns:
            sub("🌐 Name Servers")
            for s in ns: print(f"    {C.GRAY}•{C.R} {C.BWHITE}{s.lower()}{C.R}")

        created_m=re.search(r"Creation Date:\s*(.+)",whois,re.I)
        if created_m:
            try:
                date_str=created_m.group(1).strip()[:19]
                created=datetime.fromisoformat(date_str.replace("T"," "))
                age=(datetime.utcnow()-created).days
                res("Domain Age",f"{age} days ({age//365} years, {(age%365)//30} months)","info")
            except: pass

        sub("🕰️  Wayback Machine")
        wb=req_json(f"http://archive.org/wayback/available?url={domain}")
        if wb and wb.get("archived_snapshots",{}).get("closest"):
            snap=wb["archived_snapshots"]["closest"]
            res("Archived",  "YES","success")
            res("Closest Snapshot",snap.get("timestamp","?"),"info")
            res("Wayback URL",snap.get("url","?"),"info")
        else: warn("Not archived in Wayback Machine")

        sub("📜 Certificate History (crt.sh)")
        crt=req_json(f"https://crt.sh/?q={domain}&output=json")
        if crt and isinstance(crt,list):
            res("Total Certificates", str(len(crt)),"info")
            issuers=list({c.get("issuer_name","?") for c in crt})
            for i in issuers[:3]: res("Issuer",i[:60],"info")

        ok("WHOIS History done")
