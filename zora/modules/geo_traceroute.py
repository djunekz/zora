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


class GeoTraceroute:
    @staticmethod
    def run(target):
        sec("TRACEROUTE + GEOLOCATION", "🛣️")
        dots("Tracing route")
        trace=cmd(["traceroute","-m","20","-w","2",target])
        hops=[l.strip() for l in trace.splitlines() if l.strip() and not l.startswith("traceroute")]
        sub(f"📍 Hops ({len(hops)})")
        for i,hop in enumerate(hops,1):
            ips=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',hop)
            times=re.findall(r'([\d.]+)\s*ms',hop)
            avg=sum(float(t) for t in times)/len(times) if times else None
            col=C.BGREEN if avg and avg<50 else C.BYELLOW if avg and avg<150 else C.BRED
            if ips:
                geo=req_json(f"https://ipinfo.io/{ips[0]}/json")
                loc=f"{geo.get('city','?')}, {geo.get('country','?')}" if geo else "?"
                if avg:
                    print(f"  {C.GRAY}{i:2d}.{C.R} {C.BWHITE}{ips[0]:<16}{C.R} {col}{avg:.1f}ms{C.R}")
                else:
                    print(f"  {C.GRAY}{i:2d}.{C.R} {C.BWHITE}{ips[0]:<16}{C.R} {C.GRAY}(no timing){C.R}")
                print(f"      {C.GRAY}└─{C.R} {C.DIM}{loc}{C.R}")
            else:
                print(f"  {C.GRAY}{i:2d}.{C.R} * * * (no response)")
        ok("Traceroute done")
