import urllib.request
import urllib.parse
import urllib.error

from zora.core import C, ok, sec, sub


class DorkGenerator:
    @staticmethod
    def run(target):
        sec("GOOGLE DORK GENERATOR", "🔍")
        raw=target

        dorks = [
            (f'site:{raw} filetype:pdf', "PDFs"),
            (f'site:{raw} filetype:sql', "SQL Dumps"),
            (f'site:{raw} filetype:env', ".env Files"),
            (f'site:{raw} filetype:log', "Log Files"),
            (f'site:{raw} inurl:admin', "Admin Pages"),
            (f'site:{raw} inurl:login', "Login Pages"),
            (f'site:{raw} inurl:api', "API Endpoints"),
            (f'site:{raw} inurl:.git', "Git Exposed"),
            (f'site:{raw} intitle:"index of"', "Directory Listing"),
            (f'site:{raw} inurl:wp-admin', "WordPress Admin"),
            (f'site:{raw} inurl:phpmyadmin', "phpMyAdmin"),
            (f'site:{raw} "password"', "Password Mentions"),
            (f'site:{raw} "secret" OR "token" OR "api_key"', "Secrets/Keys"),
            (f'site:*.{raw} -www', "Subdomains"),
            (f'site:github.com {raw}', "GitHub Mentions"),
            (f'site:pastebin.com {raw}', "Pastebin Mentions"),
        ]

        sub(f"📋 Generated {len(dorks)} Dorks for: {C.BWHITE}{raw}{C.R}")
        for dork,desc in dorks:
            url=f"https://www.google.com/search?q={urllib.parse.quote(dork)}"
            print(f"\n  {C.BBLUE}[{desc}]{C.R}")
            print(f"    {C.GRAY}Query:{C.R} {C.BYELLOW}{dork}{C.R}")
            print(f"    {C.GRAY}URL:  {C.R} {C.CYAN}{url[:100]}{C.R}")

        ok(f"Dork Generator done — {len(dorks)} queries generated")
