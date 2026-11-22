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

from concurrent.futures import ThreadPoolExecutor, as_completed

from zora.core import *

MAX_WORKERS = 30


class TyposquatChecker:
    @staticmethod
    def generate(domain):
        parts=domain.rsplit(".",1)
        if len(parts)!=2: return []
        name,tld=parts; typos=set()
        subs={'a':'@4','e':'3','i':'1l','o':'0','s':'5$','t':'7','g':'9'}
        for i,c in enumerate(name):
            if c in subs:
                for rep in subs[c]:
                    typos.add(name[:i]+rep+name[i+1:]+"."+tld)
        for i in range(len(name)): typos.add(name[:i]+name[i+1:]+"."+tld)
        for i,c in enumerate(name): typos.add(name[:i]+c+c+name[i:]+"."+tld)
        for i in range(len(name)-1):
            typos.add(name[:i]+name[i+1]+name[i]+name[i+2:]+"."+tld)
        for alt in [".com",".net",".org",".co",".io",".biz",".info"]:
            if "."+tld!=alt: typos.add(name+alt)
        for fix in ["www","my","get","app","login","secure","account"]:
            typos.add(fix+name+"."+tld); typos.add(name+fix+"."+tld)
        for i in range(1,len(name)): typos.add(name[:i]+"-"+name[i:]+"."+tld)
        return sorted(typos)[:80]

    @staticmethod
    def run(domain):
        sec("TYPOSQUATTING GENERATOR & CHECKER", "🦆")
        if not is_domain(domain): err("Invalid domain"); return
        typos=TyposquatChecker.generate(domain)
        inf("Base Domain",domain,2); inf("Variants Generated",str(len(typos)),2)
        def check(typo):
            try:
                return (typo, socket.gethostbyname(typo))
            except:
                return None

        active=[]
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(check, t): t for t in typos}
            for i, fut in enumerate(as_completed(futures), 1):
                bar(i,len(typos),"Checking")
                result = fut.result()
                if result: active.append(result)
        print()

        if active:
            sub(f"⚠️  {len(active)} ACTIVE Typosquats Found!")
            th(["Domain","IP","Risk"])
            for typo,ip in sorted(active):
                risk="HIGH" if any(w in typo for w in ["login","secure","account","update"]) else "MED"
                tr([typo,ip,risk],"found")
        else: ok(f"No active typosquats among {len(typos)} variants")

        sub("📋 All Generated Variants (first 30)")
        for typo in typos[:30]:
            st=f"{C.BGREEN}ACTIVE{C.R}" if any(t==typo for t,_ in active) else f"{C.GRAY}inactive{C.R}"
            print(f"    {C.GRAY}•{C.R} {C.BWHITE}{typo:<40}{C.R} {st}")
        if len(typos)>30: print(f"    {C.GRAY}... and {len(typos)-30} more{C.R}")
        ok(f"Typosquat check done — {len(active)}/{len(typos)} active")
