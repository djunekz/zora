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


class RedirectTester:
    @staticmethod
    def run(domain):
        sec("OPEN REDIRECT & SSRF TESTER", "↩️")
        base = f"https://{domain}"

        sub("🔍 Redirect Chain Analysis")
        import http.client as _hc
        dots("Following redirects")
        try:
            url = base; chain = []
            for _ in range(10):
                p = urllib.parse.urlparse(url)
                cls = _hc.HTTPSConnection if p.scheme=="https" else _hc.HTTPConnection
                conn = cls(p.netloc, timeout=5)
                path = (p.path or "/") + (("?"+p.query) if p.query else "")
                conn.request("HEAD", path, headers={"User-Agent":USER_AGENT})
                resp = conn.getresponse()
                chain.append((url, resp.status))
                should_continue = False
                if resp.status in (301,302,303,307,308):
                    loc = resp.getheader("Location","")
                    if loc:
                        if loc.startswith("/"): loc = f"{p.scheme}://{p.netloc}{loc}"
                        url = loc
                        should_continue = True
                conn.close()
                if not should_continue:
                    break
            th(["Step","URL","Status"])
            for i,(u,s) in enumerate(chain,1):
                tr([str(i), u[:60], str(s)], "found" if s==200 else "warn")
        except Exception as e: warn(f"Redirect chain error: {e}")

        sub("🎯 Open Redirect Payloads (test manually)")
        for p in [f"{base}?url=https://evil.com",f"{base}?redirect=https://evil.com",
                  f"{base}?next=https://evil.com",f"{base}?return=https://evil.com",
                  f"{base}?goto=https://evil.com",f"{base}?dest=https://evil.com",
                  f"{base}?redir=//evil.com"]:
            print(f"    {C.BYELLOW}•{C.R} {C.DIM}{p}{C.R}")

        sub("🌐 SSRF Test Payloads (test manually)")
        for p in [f"{base}?url=http://169.254.169.254/latest/meta-data/",
                  f"{base}?url=http://localhost/",f"{base}?url=http://127.0.0.1/",
                  f"{base}?url=file:///etc/passwd"]:
            print(f"    {C.BRED}•{C.R} {C.DIM}{p}{C.R}")

        sub("🔎 Redirect Params Found in Page")
        html = req_text(base)
        if html:
            params = list(set(re.findall(r'[?&](url|redirect|next|return|goto|dest|target|redir)=', html, re.I)))
            res("Redirect Params", ", ".join(params) if params else "None found", "warning" if params else "info")
        ok("Redirect/SSRF Tester done")
