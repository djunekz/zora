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
import difflib
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed

from zora.core import *

MAX_WORKERS = 40
PROBE_PATH = "zzq9xf3knotarealpath00112233"
BODY_SAMPLE_BYTES = 8000
SIMILARITY_THRESHOLD = 0.92


DIR_WORDLIST = [
    "admin","login","dashboard","api","v1","v2","v3","backup","uploads","files",
    "images","static","assets","js","css","config","settings","setup","install",
    "phpinfo","test","debug","dev","staging","old","temp","tmp","logs","data",
    "database","db","sql","export","import","download","media","docs","documentation",
    "help","support","git","svn","mobile","secure","cloud","app","console","panel",
    "auth","status","monitor","bot","ci","jenkins","jira","wiki","intranet",
    "wp-admin","wp-login","wp-json","xmlrpc","phpmyadmin","adminer","cpanel",
    "webmail","graphql","metrics","actuator","swagger","openapi","redoc",
    "server-status","server-info",".well-known","cgi-bin","private","secret",
    "hidden","internal","payment","billing","search","analytics","crm","erp",
]

class DirBrute:
    @staticmethod
    def _get(url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=6) as resp:
                body = resp.read(BODY_SAMPLE_BYTES).decode(errors="ignore")
                return resp.status, dict(resp.headers), body
        except urllib.error.HTTPError as e:
            try:
                body = e.read(BODY_SAMPLE_BYTES).decode(errors="ignore")
            except Exception:
                body = ""
            return e.code, dict(e.headers), body
        except Exception:
            return None, {}, ""

    @staticmethod
    def run(domain):
        sec("DIRECTORY BRUTE FORCER", "📂")
        inf("Target", domain, 2); inf("Wordlist", f"{len(DIR_WORDLIST)} entries", 2)

        wc_status, _, wc_body = DirBrute._get(f"https://{domain}/{PROBE_PATH}")
        wildcard = wc_status in (200, 201, 301, 302, 403)
        if wildcard:
            warn(f"Wildcard response detected (HTTP {wc_status} for a random nonexistent path) — filtering false positives")

        def probe(word):
            url = f"https://{domain}/{word}"
            status, headers, body = DirBrute._get(url)
            if status not in (200,201,301,302,403):
                return None
            if wildcard and status == wc_status:
                similarity = difflib.SequenceMatcher(None, body, wc_body).quick_ratio()
                if similarity >= SIMILARITY_THRESHOLD:
                    return None
            return (f"/{word}", status, headers.get("Content-Length","?"))

        found = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(probe, w): w for w in DIR_WORDLIST}
            for i, fut in enumerate(as_completed(futures), 1):
                bar(i,len(DIR_WORDLIST),"Bruteforcing")
                result = fut.result()
                if result: found.append(result)
        print()

        if found:
            found.sort(key=lambda x:x[0])
            sub(f"✅ Found {len(found)} paths")
            th(["Path","Status","Size"])
            for path,code,size in found:
                tr([path,str(code),str(size)],"found" if code==200 else "warn" if code==403 else "")
        else: warn("No paths discovered")
        ok(f"Dir Brute done — {len(found)}/{len(DIR_WORDLIST)} found")
