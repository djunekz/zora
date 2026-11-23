import re
import base64
import urllib.request
import urllib.parse
import urllib.error

from zora.core import C, ok, req_headers, res, sec, sub, warn


class URLAnalyzer:
    @staticmethod
    def run(url):
        sec("URL / LINK DEEP ANALYZER", "🔗")
        if not (url.startswith("https://") or url.startswith("http://")):
            url="https://"+url
        parsed=urllib.parse.urlparse(url)

        sub("📋 URL Decomposition")
        res("Scheme",  parsed.scheme,"info"); res("Host",parsed.netloc,"info")
        res("Path",    parsed.path or "/","info"); res("Query",parsed.query or "None","info")
        res("Fragment",parsed.fragment or "None","info"); res("Length",str(len(url)),"info")

        if parsed.query:
            sub("🔍 Query Parameters")
            for k,v in urllib.parse.parse_qs(parsed.query).items():
                res(k,", ".join(v),"info")

        sub("⚠️  Suspicious Pattern Check")
        suspicious=[]
        if re.search(r'(\.\./|%2e%2e)',url,re.I): suspicious.append("Path Traversal")
        if re.search(r'(<|>|script|javascript:)',url,re.I): suspicious.append("XSS Pattern")
        if re.search(r'(union|select|insert|drop|exec)',url,re.I): suspicious.append("SQLi Pattern")
        if re.search(r'(169\.254|127\.0\.0|0\.0\.0\.0)',url): suspicious.append("SSRF Target")
        if re.search(r'%[0-9a-f]{2}',url,re.I): suspicious.append("URL Encoded")
        if suspicious: warn(f"Suspicious: {', '.join(suspicious)}")
        else: ok("No suspicious patterns detected")

        sub("🌐 Reputation Links")
        for nm,lnk in [
            ("VirusTotal",       f"https://www.virustotal.com/gui/url/{base64.b64encode(url.encode()).decode().rstrip('=')}"),
            ("URLScan.io",       f"https://urlscan.io/search/#page.domain:{parsed.netloc}"),
            ("URLVoid",          f"https://www.urlvoid.com/scan/{parsed.netloc}/"),
            ("MXToolbox",        f"https://mxtoolbox.com/SuperTool.aspx?action=blacklist%3a{parsed.netloc}"),
        ]: print(f"    {C.BCYAN}•{C.R} {C.BOLD}{nm:<22}{C.R} {C.GRAY}{lnk[:70]}{C.R}")

        sub("⚡ Quick Fetch")
        h,status=req_headers(url)
        if status == 0:
            warn("Could not connect to host (unreachable, DNS failure, or timeout)")
        res("HTTP Status",    str(status),"success" if 0<status<400 else "warning")
        res("Content-Type",   h.get("Content-Type","?"),"info")
        res("Content-Length", h.get("Content-Length","?"),"info")
        res("Cache-Control",  h.get("Cache-Control","?"),"info")
        ok("URL Analysis done")
