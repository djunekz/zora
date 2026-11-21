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


class CTMonitor:
    @staticmethod
    def run(domain):
        sec("CERTIFICATE TRANSPARENCY MONITOR", "📜")
        dots("Querying crt.sh")
        crt = req_json(f"https://crt.sh/?q=%.{domain}&output=json")
        if not crt or not isinstance(crt,list):
            warn("No CT log data found"); return

        res("Total Certificates", str(len(crt)), "info")
        domains_found=set(); issuers={}; dates=[]
        apex = domain.lower()
        for entry in crt:
            for line in entry.get("name_value","").split("\n"):
                line=line.strip().lstrip("*.").lower()
                if line and (line == apex or line.endswith("." + apex)):
                    domains_found.add(line)
            iss=entry.get("issuer_name","?"); issuers[iss]=issuers.get(iss,0)+1
            ts=entry.get("entry_timestamp","")
            if ts: dates.append(str(ts)[:10])

        sub(f"🌐 Unique Domains via CT ({len(domains_found)})")
        for d in sorted(domains_found)[:30]: print(f"    {C.BGREEN}•{C.R} {C.BWHITE}{d}{C.R}")
        if len(domains_found)>30: print(f"    {C.GRAY}... and {len(domains_found)-30} more{C.R}")

        sub("🏢 Certificate Issuers")
        for issuer,count in sorted(issuers.items(),key=lambda x:-x[1])[:5]:
            short=issuer[:60].split(",")[0].replace("CN=","")
            res(f"{count}x",short,"info")

        sub("📅 Timeline")
        if dates:
            dates.sort()
            res("First Cert",dates[0],"info"); res("Latest Cert",dates[-1],"info")

        sub("🔍 Sensitive Subdomains in CT")
        sensitives=[d for d in domains_found if any(w in d for w in
            ["dev","staging","test","beta","admin","internal","vpn","mail","smtp"])]
        if sensitives:
            res("Sensitive",str(len(sensitives)),"warning")
            for s in sensitives[:10]: print(f"    {C.BYELLOW}• {s}{C.R}")
        ok(f"CT Monitor done — {len(domains_found)} domains, {len(crt)} certs")
