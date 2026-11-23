import re

from zora.core import C, err, ok, req_headers, res, sec, sub, warn


class HeaderAuditor:
    HDRS = {
        "Strict-Transport-Security": {"desc":"HSTS",        "tip":"max-age=31536000; includeSubDomains; preload",
            "good": lambda v: bool(re.search(r'max-age=(\d+)',v)) and int((re.search(r'max-age=(\d+)',v) or type('',(),{'group':lambda s,x:"0"})()).group(1) or 0)>=31536000},
        "Content-Security-Policy":   {"desc":"CSP",         "tip":"Avoid unsafe-inline, use nonces/hashes",
            "good": lambda v: len(v)>10 and "unsafe-inline" not in v},
        "X-Frame-Options":           {"desc":"Clickjacking","tip":"Set: DENY or SAMEORIGIN",
            "good": lambda v: v.upper() in ("DENY","SAMEORIGIN")},
        "X-Content-Type-Options":    {"desc":"MIME Sniff",  "tip":"Set: nosniff",
            "good": lambda v: v.lower()=="nosniff"},
        "Referrer-Policy":           {"desc":"Referrer",    "tip":"strict-origin-when-cross-origin",
            "good": lambda v: v in ("no-referrer","strict-origin","strict-origin-when-cross-origin")},
        "Permissions-Policy":        {"desc":"Permissions", "tip":"Restrict camera, mic, geolocation",
            "good": lambda v: len(v)>5},
        "X-XSS-Protection":          {"desc":"XSS Filter",  "tip":"1; mode=block",
            "good": lambda v: v.startswith("1")},
        "Cross-Origin-Opener-Policy":{"desc":"COOP",        "tip":"same-origin",
            "good": lambda v: "same-origin" in v},
        "Cross-Origin-Resource-Policy":{"desc":"CORP",      "tip":"same-origin",
            "good": lambda v: v in ("same-origin","same-site")},
    }

    @staticmethod
    def run(domain):
        sec("HTTP SECURITY HEADER AUDITOR", "🔏")
        headers, status = req_headers(f"https://{domain}")
        if not headers:
            headers, status = req_headers(f"http://{domain}")
        if status == 0:
            err("Could not connect to host (unreachable, DNS failure, or timeout)")
            return
        res("HTTP Status", str(status), "success" if status<400 else "warning")

        score = 0; missing = []; weak = []
        sub("📋 Header Analysis")
        for header, cfg in HeaderAuditor.HDRS.items():
            val = str(headers.get(header,"") or "")
            if not val:
                missing.append(header)
                res(f"✗ {cfg['desc']}", "MISSING", "error")
                print(f"      {C.DIM}→ {cfg['tip']}{C.R}")
            else:
                try:    is_good = cfg["good"](val)
                except: is_good = True
                if is_good:
                    score += 1
                    res(f"✓ {cfg['desc']}", val[:60], "success")
                else:
                    weak.append(header); score += 0.5
                    res(f"~ {cfg['desc']}", f"WEAK — {val[:45]}", "warning")
                    print(f"      {C.DIM}→ {cfg['tip']}{C.R}")

        sub("📊 Security Score")
        pct = int((score/len(HeaderAuditor.HDRS))*100)
        grade = "A+" if pct>=95 else "A" if pct>=85 else "B" if pct>=70 else "C" if pct>=55 else "D" if pct>=40 else "F"
        col = C.BGREEN if pct>=70 else C.BYELLOW if pct>=40 else C.BRED
        print(f"    {C.BOLD}Grade: {col}{grade}{C.R}  Score: {col}{pct}/100{C.R}")
        print(f"    Missing: {C.BRED}{len(missing)}{C.R}  Weak: {C.BYELLOW}{len(weak)}{C.R}  Good: {C.BGREEN}{len(HeaderAuditor.HDRS)-len(missing)-len(weak)}{C.R}")

        sub("🔍 Info Disclosure Check")
        for h in ["Server","X-Powered-By","X-AspNet-Version","X-Generator"]:
            if h in headers: warn(f"Disclosure: {h}: {headers[h]}")

        sub("🍪 Cookie Security")
        sc = headers.get("Set-Cookie","")
        if sc:
            res("Secure",   "✓" if "Secure"   in sc else "✗ Missing","success" if "Secure"   in sc else "error")
            res("HttpOnly", "✓" if "HttpOnly" in sc else "✗ Missing","success" if "HttpOnly" in sc else "error")
            res("SameSite", "✓" if "SameSite" in sc else "✗ Missing","success" if "SameSite" in sc else "warning")
        ok(f"Header Audit done — Grade: {grade} ({pct}/100)")
