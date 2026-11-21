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


class NetUtils:
    @staticmethod
    def run():
        sec("NETWORK UTILITIES", "🛠️")

        sub("🌐 My Public IP")
        for svc in ["https://api.ipify.org?format=json","https://ipinfo.io/json"]:
            d=req_json(svc)
            if d:
                myip=d.get("ip") or d.get("query")
                if myip:
                    res("Public IP", myip,"info")
                    geo=req_json(f"https://ipinfo.io/{myip}/json")
                    if geo:
                        res("Location", f"{geo.get('city')}, {geo.get('region')}, {geo.get('country')}","info")
                        res("ISP",      geo.get("org","N/A"),"info")
                    break

        sub("🔍 Local Network Info")
        hostname=socket.gethostname()
        local_ip="N/A"
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.connect(("8.8.8.8", 80))
            local_ip=s.getsockname()[0]
            s.close()
        except Exception:
            try: local_ip=socket.gethostbyname(hostname)
            except: local_ip="N/A"
        res("Hostname",  hostname,"info")
        res("Local IP",  local_ip,"info")

        sub("🌍 IPv6 Connectivity")
        ipv6=req_text("https://api6.ipify.org")
        res("IPv6 Address", ipv6.strip() if ipv6 else "No IPv6","info" if ipv6 else "warning")

        sub("⏱️  Latency to Major Servers")
        targets={"Google DNS":"8.8.8.8","Cloudflare":"1.1.1.1","Quad9":"9.9.9.9"}
        for name,host in targets.items():
            p=cmd(["ping","-c","3","-W","2",host])
            times=re.findall(r'time=([\d.]+)',p)
            if times:
                avg=sum(float(t) for t in times)/len(times)
                res(name,f"{avg:.1f} ms","success" if avg<50 else "warning")
            else:
                res(name,"Unreachable","error")

        ok("Network Utilities done")
