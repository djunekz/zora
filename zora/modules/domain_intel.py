import re
import socket
import ssl
from datetime import datetime

from zora.core import C, bar, dns_query, dots, err, is_domain, ok, req_headers, req_text, res, sec, sub, th, tr, warn, whois_query


class DomainIntel:
    @staticmethod
    def run(domain):
        sec("DOMAIN INTELLIGENCE", "🌐")
        if not is_domain(domain):
            err("Invalid domain"); return

        sub("📋 WHOIS")
        dots("Querying WHOIS")
        whois = whois_query(domain)
        if not whois:
            warn("WHOIS lookup failed (server unreachable or rate-limited)")
        for key, pat in {
            "Registrar":   r"Registrar:\s*(.+)",
            "Created":     r"Creation Date:\s*(.+)",
            "Expires":     r"Registry Expiry Date:\s*(.+)",
            "Updated":     r"Updated Date:\s*(.+)",
            "Status":      r"Domain Status:\s*(.+)",
            "Registrant":  r"Registrant Organization:\s*(.+)",
            "Name Server": r"Name Server:\s*(.+)",
        }.items():
            m = re.findall(pat, whois, re.I)
            if m:
                if key == "Name Server":
                    uniq = list(dict.fromkeys(x.strip() for x in m))
                    res(key, ", ".join(uniq)[:120], "info")
                else:
                    res(key, m[0][:70], "info")

        sub("🗂️  DNS Records")
        for rt in ["A","AAAA","MX","NS","TXT","CNAME","SOA","CAA","DNSKEY"]:
            recs = dns_query(domain, rt)
            if recs:
                print(f"\n    {C.BCYAN}{C.BOLD}{rt}:{C.R}")
                for r in recs[:4]:
                    print(f"      {C.GRAY}•{C.R} {C.BWHITE}{r[:90]}{C.R}")

        sub("🔐 Email Security")
        txt = "\n".join(dns_query(domain,"TXT"))
        has_spf   = "v=spf1" in txt
        dmarc_txt = "\n".join(dns_query(f"_dmarc.{domain}","TXT"))
        has_dmarc = "v=DMARC1" in dmarc_txt
        bimi      = "\n".join(dns_query(f"default._bimi.{domain}","TXT"))
        res("SPF",   "Present" if has_spf   else "Missing", "success" if has_spf   else "warning")
        res("DMARC", "Present" if has_dmarc else "Missing", "success" if has_dmarc else "warning")
        res("BIMI",  "Present" if bimi      else "Missing", "success" if bimi      else "info")

        sub("🔎 Subdomain Enumeration (60 subs)")
        subs60 = [
            "www","mail","ftp","smtp","pop","imap","webmail","admin","blog","dev",
            "test","api","portal","vpn","remote","secure","shop","store","support",
            "help","m","mobile","cdn","static","assets","img","images","git","svn",
            "ns","ns1","ns2","dns","docs","forum","beta","alpha","stage","staging",
            "demo","backup","old","new","v2","v3","cloud","media","download","upload",
            "app","dashboard","console","panel","login","auth","status","monitor","bot",
            "ci","jenkins","jira","confluence","wiki","kb","intranet"
        ]
        found_subs=[]
        for i,s in enumerate(subs60,1):
            bar(i,len(subs60),"Scanning")
            try:
                ip4=socket.gethostbyname(f"{s}.{domain}")
                found_subs.append((f"{s}.{domain}",ip4))
            except: pass
        if found_subs:
            print(f"\n  {C.BGREEN}{len(found_subs)} subdomains found:{C.R}")
            th(["Subdomain","IP"])
            for sd,ip4 in found_subs: tr([sd,ip4],"found")
        else: warn("No subdomains found")

        sub("🔒 SSL/TLS Certificate")
        dots("Checking SSL")
        try:
            ctx=ssl.create_default_context()
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            with socket.create_connection((domain,443),timeout=5) as sk:
                with ctx.wrap_socket(sk,server_hostname=domain) as ss:
                    cert=ss.getpeercert(); ci=ss.cipher(); ver=ss.version()
                    subj=dict(x[0] for x in cert.get("subject",[]))
                    iss =dict(x[0] for x in cert.get("issuer",[]))
                    res("CN",        subj.get("commonName","N/A"),"info")
                    res("Issuer",    iss.get("organizationName","N/A"),"info")
                    res("Valid From",cert.get("notBefore","N/A"),"info")
                    res("Valid To",  cert.get("notAfter","N/A"),"info")
                    res("TLS",       ver,"success" if "1.3" in ver or "1.2" in ver else "warning")
                    res("Cipher",    ci[0] if ci else "N/A","info")
                    res("Bits",      str(ci[2]) if ci and len(ci)>2 else "N/A","info")
                    sans=cert.get("subjectAltName",[])
                    res("SANs",      str(len(sans))+" entries","info")
                    try:
                        exp=datetime.strptime(cert.get("notAfter",""),"%b %d %H:%M:%S %Y %Z")
                        days=(exp-datetime.utcnow()).days
                        res("Expires In",f"{days} days","success" if days>30 else "error")
                    except: pass
        except Exception as e: warn(f"SSL: {e}")

        sub("🛡️  Security Headers")
        headers,status = req_headers(f"https://{domain}")
        res("HTTP Status", str(status), "success" if status<400 else "warning")
        for h,label in {
            "Strict-Transport-Security":"HSTS",
            "X-Frame-Options":"X-Frame-Options",
            "X-Content-Type-Options":"X-Content-Type-Options",
            "Content-Security-Policy":"CSP",
            "Permissions-Policy":"Permissions-Policy",
            "Referrer-Policy":"Referrer-Policy",
            "X-XSS-Protection":"XSS-Protection",
        }.items():
            val = headers.get(h,"")
            res(label, "✓ Set" if val else "✗ Missing", "success" if val else "warning")

        sub("⚙️  Technology Stack")
        html_src = req_text(f"https://{domain}")
        if html_src:
            hl = html_src.lower()
            techs=[]
            for name,sig in {
                "WordPress":"wp-content","Joomla":"joomla","Drupal":"drupal",
                "Shopify":"shopify","Magento":"magento","React":"react",
                "Vue.js":"vue","Angular":"angular","Next.js":"_next",
                "Nuxt.js":"nuxt","Gatsby":"gatsby","Svelte":"svelte",
                "Bootstrap":"bootstrap","Tailwind":"tailwind","jQuery":"jquery",
                "Google Analytics":"gtag(","GTM":"googletagmanager",
                "Cloudflare":"cloudflare","AWS":"amazonaws","Vercel":"vercel",
                "Netlify":"netlify","HubSpot":"hubspot","Intercom":"intercom",
            }.items():
                if sig in hl: techs.append(name)
            if techs:
                for t in techs: print(f"    {C.BGREEN}✓{C.R} {t}")
            else: warn("No known tech detected")

        sub("📄 Page Metadata")
        if html_src:
            title_m  = re.search(r'<title[^>]*>(.*?)</title>', html_src, re.I|re.S)
            desc_m   = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html_src, re.I|re.S)
            robots_m = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'](.*?)["\']', html_src, re.I|re.S)
            if title_m:  res("Title",       title_m.group(1)[:80].strip(),"info")
            if desc_m:   res("Description", desc_m.group(1)[:100].strip(),"info")
            if robots_m: res("Robots",      robots_m.group(1),"info")
            links = re.findall(r'href=["\']https?://([^/"\']+)', html_src)
            apex = domain.lower()
            ext_domains = set(
                l for l in (h.lower() for h in links)
                if l != apex and not l.endswith("." + apex)
            )
            res("External Links", str(len(ext_domains))+" unique domains", "info")

        ok(f"Domain Intelligence done — {len(found_subs)} subdomains")
