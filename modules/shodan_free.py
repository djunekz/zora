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


class ShodanFree:
    @staticmethod
    def run(query):
        sec("SHODAN ALTERNATIVES (FREE)", "🔭")
        q=urllib.parse.quote(query); ip_mode=is_ip(query)

        if ip_mode:
            sub("🔍 InternetDB (Shodan Free)")
            data=req_json(f"https://internetdb.shodan.io/{query}")
            if data and not data.get("detail"):
                ports=data.get("ports",[]); vulns=data.get("vulns",[])
                res("Open Ports",", ".join(map(str,ports)) if ports else "None","warning" if ports else "success")
                res("Hostnames",", ".join(data.get("hostnames",[])[:5]) or "None","info")
                res("Tags",", ".join(data.get("tags",[])) or "None","info")
                if vulns:
                    res("CVEs",str(len(vulns)),"error")
                    for v in vulns[:10]: print(f"      {C.BRED}• {v}{C.R}")
            else: warn("No InternetDB data")

            sub("📡 GreyNoise Community")
            gn=req_json(f"https://api.greynoise.io/v3/community/{query}")
            if gn and gn.get("ip"):
                res("Classification",gn.get("classification","?"),"info")
                res("Noise",str(gn.get("noise",False)),"warning" if gn.get("noise") else "success")
                res("RIOT",str(gn.get("riot",False)),"info")
            else:
                print(f"    {C.GRAY}https://www.greynoise.io/viz/ip/{query}{C.R}")

        sub("🌐 Other Free Tools")
        for nm,url in [
            ("Censys Search",   f"https://search.censys.io/search?resource=hosts&q={q}"),
            ("FOFA",            f"https://en.fofa.info/result?qbase64={base64.b64encode(query.encode()).decode()}"),
            ("Zoomeye",         f"https://www.zoomeye.org/searchResult?q={q}"),
            ("BinaryEdge",      f"https://app.binaryedge.io/services/query?q={q}"),
            ("Shodan",          f"https://www.shodan.io/search?query={q}"),
        ]: print(f"    {C.BCYAN}•{C.R} {C.BOLD}{nm:<18}{C.R} {C.GRAY}{url[:75]}{C.R}")
        ok("Shodan Alternatives done")
