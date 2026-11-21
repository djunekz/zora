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


class SSLAnalyzer:
    @staticmethod
    def run(domain):
        sec("SSL/TLS DEEP ANALYZER", "🔒")
        dots("Analyzing SSL")
        try:
            ctx=ssl.create_default_context()
            with socket.create_connection((domain,443),timeout=5) as sk:
                with ctx.wrap_socket(sk,server_hostname=domain) as ss:
                    cert=ss.getpeercert(); ci=ss.cipher(); ver=ss.version()

                    sub("📜 Certificate")
                    subj=dict(x[0] for x in cert.get("subject",[]))
                    iss =dict(x[0] for x in cert.get("issuer",[]))
                    for k,v in subj.items(): res(f"Subject/{k}",v,"info")
                    for k,v in iss.items():  res(f"Issuer/{k}", v,"info")

                    sub("📅 Validity")
                    res("Not Before",cert.get("notBefore","N/A"),"info")
                    res("Not After", cert.get("notAfter", "N/A"),"info")
                    try:
                        exp=datetime.strptime(cert["notAfter"],"%b %d %H:%M:%S %Y %Z")
                        days=(exp-datetime.utcnow()).days
                        res("Days Left",str(days),"success" if days>30 else "error")
                    except: pass

                    sub("🌐 SANs")
                    sans=cert.get("subjectAltName",[])
                    for t,v in sans[:10]: res(t,v,"info")

                    sub("🔐 Connection")
                    res("Protocol",ver,"success" if "1.3" in ver else "warning")
                    res("Cipher",  ci[0] if ci else "?","info")
                    res("Key Bits",str(ci[2]) if ci and len(ci)>2 else "?","info")

                    sub("⚠️  Weak Cipher Check")
                    weak=["RC4","DES","3DES","NULL","EXPORT","MD5","anon"]
                    cipher_name=ci[0] if ci else ""
                    found_weak=[w for w in weak if w in cipher_name]
                    if found_weak: warn(f"Weak cipher: {','.join(found_weak)}")
                    else: ok("No weak ciphers detected")

                    sub("🔍 Certificate Transparency")
                    ct_data=req_json(f"https://crt.sh/?q={domain}&output=json")
                    if ct_data and isinstance(ct_data,list):
                        res("CT Logs", f"{len(ct_data)} certificates found","info")
                        th(["ID","Issuer","Logged"])
                        for entry in ct_data[:5]:
                            tr([str(entry.get("id","")),
                                str(entry.get("issuer_name",""))[:35],
                                str(entry.get("entry_timestamp",""))[:16]],"found")
                    ok("SSL Analysis done")
        except Exception as e: err(f"SSL failed: {e}")
