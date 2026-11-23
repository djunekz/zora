import socket

from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.query
import dns.zone
import dns.exception

from zora.core import C, bar, dns_query, inf, ok, res, reverse_dns, sec, sub, th, tr, warn

MAX_WORKERS = 60


BIG_WORDLIST=[
    "www","mail","ftp","smtp","pop","pop3","imap","webmail","admin","administrator",
    "blog","forum","shop","store","api","dev","development","test","testing","stage",
    "staging","demo","beta","alpha","cdn","static","assets","img","images","js","css",
    "media","files","download","downloads","upload","uploads","remote","vpn","portal",
    "gateway","proxy","ns","ns1","ns2","ns3","ns4","dns","dns1","dns2","help","support",
    "docs","documentation","git","svn","repo","hg","mobile","m","wap","secure","ssl",
    "cloud","backup","old","new","v2","v3","v4","app","dashboard","console","panel",
    "login","auth","status","monitor","monitoring","bot","ci","jenkins","jira",
    "confluence","wiki","kb","intranet","extranet","db","database","mysql","postgres",
    "redis","cache","queue","worker","api2","api3","rest","graphql","ws","chat",
    "pay","payment","billing","search","analytics","metrics","stats","data",
    "email","crm","erp","security","waf","vpn2","nginx","apache","grpc",
]

class SubdomainAdvanced:
    @staticmethod
    def run(domain):
        sec("ADVANCED SUBDOMAIN SCANNER", "🔎")
        inf("Target",   domain,2)
        inf("Wordlist", f"{len(BIG_WORDLIST)} entries",2)

        def probe(sub_):
            fd=f"{sub_}.{domain}"
            try:
                return (fd, socket.gethostbyname(fd))
            except:
                return None

        found=[]
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(probe, s): s for s in BIG_WORDLIST}
            for i, fut in enumerate(as_completed(futures), 1):
                bar(i,len(BIG_WORDLIST),"Scanning")
                result = fut.result()
                if result: found.append(result)
        print()

        if found:
            found.sort(key=lambda x:x[0])
            sub(f"✅ Found {len(found)} Subdomains")
            th(["Subdomain","IP","Reverse DNS"])
            for sd,ip4 in found:
                rdns_=reverse_dns(ip4) or "-"
                tr([sd,ip4,rdns_[:30]],"found")
        else: warn("No subdomains found")

        sub("⚡ Zone Transfer Attempt (AXFR)")
        ns_recs=dns_query(domain,"NS")
        if not ns_recs:
            warn("Could not resolve nameservers for this domain — skipping AXFR check")
        for ns_host in ns_recs[:2]:
            ns_host=ns_host.rstrip('.')
            try:
                zone = dns.zone.from_xfr(dns.query.xfr(ns_host, domain, timeout=10, lifetime=10))
                names = sorted(str(n) for n in zone.nodes.keys())
                warn(f"Zone transfer SUCCEEDED from {ns_host}! ({len(names)} records exposed)")
                for n in names[:30]:
                    print(f"    {C.BRED}• {n}.{domain}{C.R}")
            except (dns.exception.FormError, ConnectionRefusedError, OSError):
                res(f"AXFR @{ns_host}","Refused (good)","success")
            except Exception as e:
                res(f"AXFR @{ns_host}", f"Could not test ({type(e).__name__})", "warning")

        ok(f"Subdomain scan done — {len(found)} found")
