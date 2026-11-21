import re
import socket
import ssl
import json
import time
import base64
import hashlib
import threading
import ipaddress
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

from zora.core import *


class BulkWhois:
    @staticmethod
    def run(domains_str):
        sec("BULK WHOIS CHECKER", "📋")
        domains=[d.strip() for d in re.split(r'[,\n\s]+',domains_str) if d.strip()]
        inf("Targets",str(len(domains)),2); results=[]
        for i,domain in enumerate(domains,1):
            bar(i,len(domains),"Querying")
            if not is_domain(domain):
                results.append((domain,"Invalid","?","?","?")); continue
            w=whois_query(domain)
            reg_m=re.search(r'Registrar:\s*(.+)',w,re.I)
            exp_m=re.search(r'Registry Expiry Date:\s*(.+)',w,re.I)
            cre_m=re.search(r'Creation Date:\s*(.+)',w,re.I)
            registrar=reg_m.group(1).strip()[:25] if reg_m else "?"
            expires  =exp_m.group(1).strip()[:10]  if exp_m else "?"
            created  =cre_m.group(1).strip()[:10]  if cre_m else "?"
            status="OK"
            if exp_m:
                try:
                    exp_date=datetime.fromisoformat(exp_m.group(1).strip()[:19].replace("T"," "))
                    days=(exp_date-datetime.utcnow()).days
                    status="EXPIRED" if days<0 else f"EXPIRING ({days}d)" if days<30 else f"OK ({days}d)"
                except: pass
            results.append((domain,registrar,created,expires,status))
        print()
        sub("📊 Results")
        th(["Domain","Registrar","Created","Expires","Status"])
        for row in results:
            color="found" if "OK" in row[4] else "warn" if "EXPIRING" in row[4] else "notfound"
            tr(list(row),color)
        expired=[r for r in results if "EXPIRED" in r[4]]
        if expired: warn(f"{len(expired)} domain(s) EXPIRED!")
        ok(f"Bulk WHOIS done — {len(domains)} domains")
