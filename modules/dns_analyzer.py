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


class DNSAnalyzer:
    @staticmethod
    def run(domain):
        sec("FULL DNS ANALYZER", "🗂️")
        dots("Querying DNS")
        for rt,desc in [
            ("A","IPv4 Addresses"),("AAAA","IPv6 Addresses"),("MX","Mail Servers"),
            ("NS","Name Servers"),("TXT","Text Records"),("CNAME","Canonical"),
            ("SOA","Start of Authority"),("CAA","CA Authorization"),
            ("DS","DNSSEC DS"),("DNSKEY","DNSSEC Key"),
        ]:
            recs=dns_query(domain,rt)
            if recs:
                sub(f"{desc} ({rt})")
                for r in recs[:6]: print(f"    {C.GRAY}•{C.R} {C.BWHITE}{r[:90]}{C.R}")

        sub("🌍 DNS Propagation Check")
        resolvers={
            "Google":"8.8.8.8","Cloudflare":"1.1.1.1","OpenDNS":"208.67.222.222",
            "Quad9":"9.9.9.9","AdGuard":"94.140.14.14",
        }
        for name,ns_ip in resolvers.items():
            ips=dns_query(domain,"A",nameserver=ns_ip)
            res(name, ", ".join(ips) if ips else "No result","info" if ips else "warning")

        sub("🔐 DNSSEC")
        dnskey=dns_query(domain,"DNSKEY")
        ds    =dns_query(domain,"DS")
        res("DNSKEY", f"{len(dnskey)} key(s)" if dnskey else "Not signed","success" if dnskey else "warning")
        res("DS",     f"{len(ds)} record(s)" if ds else "None","info")

        ok("DNS Analysis done")
