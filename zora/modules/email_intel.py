import re

from zora.core import C, dns_query, dots, err, is_email, ok, port_open, res, sec, sub, warn


class EmailIntel:
    @staticmethod
    def run(email):
        sec("EMAIL INTELLIGENCE", "📧")
        if not is_email(email):
            err("Invalid email"); return

        user, domain = email.split("@",1)
        res("Email",    email,"info")
        res("Username", user, "info")
        res("Domain",   domain,"info")
        res("Length",   f"{len(user)} chars","info")

        sub("🗑️  Disposable Email Check")
        disposable_domains = {
            "mailinator.com","guerrillamail.com","10minutemail.com","throwam.com",
            "yopmail.com","sharklasers.com","guerrillamailblock.com","trashmail.me",
            "dispostable.com","maildrop.cc","spamgourmet.com","fakeinbox.com",
            "mailnull.com","spamex.com","jetable.fr.nf","trashmail.at",
            "spamfree24.org","spamcorpse.com","spam4.me","bccto.me"
        }
        is_disp = domain.lower() in disposable_domains
        res("Disposable", "YES — Throwaway" if is_disp else "No", "warning" if is_disp else "success")

        sub("📮 Mail Server (MX Records)")
        dots("Checking MX records")
        mxrecs = dns_query(domain,"MX")
        if mxrecs:
            ok(f"{len(mxrecs)} MX record(s)")
            for i,mx in enumerate(mxrecs[:5],1):
                parts=mx.split(None,1)
                pri,srv=(parts[0],parts[1]) if len(parts)>1 else ("?",mx)
                print(f"      {C.GRAY}{i}.{C.R} {C.BWHITE}{srv.rstrip('.')}{C.R} {C.GRAY}(pri:{pri}){C.R}")
            mx_str=" ".join(mxrecs).lower()
            provider="Unknown"
            if "google" in mx_str: provider="Google Workspace"
            elif "outlook" in mx_str or "microsoft" in mx_str: provider="Microsoft 365"
            elif "protonmail" in mx_str: provider="ProtonMail"
            elif "mimecast" in mx_str: provider="Mimecast"
            elif "mailgun" in mx_str: provider="Mailgun"
            elif "sendgrid" in mx_str: provider="SendGrid"
            elif "amazonses" in mx_str: provider="AWS SES"
            elif "zoho" in mx_str: provider="Zoho Mail"
            res("Provider", provider, "info")
        else: warn("No MX records")

        sub("🔐 Email Authentication")
        txts    = "\n".join(dns_query(domain,"TXT"))
        dmarc_t = "\n".join(dns_query(f"_dmarc.{domain}","TXT"))
        dkim_t  = "\n".join(dns_query(f"default._domainkey.{domain}","TXT"))
        res("SPF",   "Present" if "v=spf1" in txts else "Missing",  "success" if "v=spf1" in txts else "warning")
        res("DMARC", "Present" if "v=DMARC1" in dmarc_t else "Missing","success" if "v=DMARC1" in dmarc_t else "warning")
        res("DKIM",  "Present" if "v=DKIM1" in dkim_t else "Not Found","success" if "v=DKIM1" in dkim_t else "info")

        sub("📬 SMTP Connectivity Test")
        mx_host = mxrecs[0].split()[-1].rstrip('.') if mxrecs else domain
        for port,name in [(25,"SMTP"),(587,"Submission"),(465,"SMTPS"),(2525,"Alt-SMTP")]:
            status = port_open(mx_host,port,timeout=3)
            res(f"Port {port} ({name})", "OPEN" if status else "closed",
                "success" if status else "info")

        sub("🔍 Username Pattern Analysis")
        patterns=[]
        if re.match(r'^[a-z]+\.[a-z]+$', user): patterns.append("firstname.lastname")
        if re.match(r'^[a-z][a-z]+$', user): patterns.append("firstnamelastname")
        if re.match(r'^[a-z]+[0-9]+$', user): patterns.append("name+numbers")
        if re.match(r'^[a-z]+_[a-z]+$', user): patterns.append("first_last")
        res("Pattern", ", ".join(patterns) if patterns else "Custom", "info")

        sub("🔄 Common Email Permutations")
        parts = re.split(r'[\._\-]', user)
        if len(parts)>=2:
            fn,ln=parts[0],parts[-1]
            perms=[
                f"{fn}.{ln}@{domain}", f"{fn}_{ln}@{domain}",
                f"{fn[0]}{ln}@{domain}", f"{fn}{ln[0]}@{domain}",
                f"{ln}.{fn}@{domain}", f"{fn}@{domain}",
            ]
            for p in perms[:6]: print(f"    {C.GRAY}•{C.R} {C.BWHITE}{p}{C.R}")
        else:
            warn("Username has no separator (., _, -) — cannot derive firstname/lastname permutations")

        sub("🚨 Breach Check Resources")
        links=[
            ("HaveIBeenPwned","https://haveibeenpwned.com/"),
            ("DeHashed","https://dehashed.com/"),
            ("LeakCheck","https://leakcheck.io/"),
            ("IntelX","https://intelx.io/"),
            ("Snusbase","https://snusbase.com/"),
        ]
        for name,url in links: print(f"    {C.BCYAN}•{C.R} {C.BOLD}{name}:{C.R} {C.GRAY}{url}{C.R}")

        ok("Email Intelligence done")
