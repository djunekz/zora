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


class WebTechProfiler:
    @staticmethod
    def run(domain):
        sec("WEB TECHNOLOGY PROFILER", "⚙️")
        dots("Fetching page")

        html_src=req_text(f"https://{domain}") or req_text(f"http://{domain}")
        if not html_src:
            err("Could not fetch page"); return
        hl=html_src.lower()

        TECH_SIGS={
            "WordPress":    ["wp-content","wp-includes"],
            "Joomla":       ["joomla","option=com_"],
            "Drupal":       ["drupal","sites/default"],
            "Shopify":      ["shopify","cdn.shopify"],
            "React":        ["react","reactid"],
            "Vue.js":       ["vue.js","v-bind","__vue"],
            "Angular":      ["ng-version","angular"],
            "Next.js":      ["_next/","__next"],
            "Nuxt.js":      ["_nuxt/","__nuxt"],
            "Bootstrap":    ["bootstrap.css","bootstrap.min"],
            "Tailwind":     ["tailwind"],
            "jQuery":       ["jquery.js","jquery.min"],
            "Google Analytics":     ["gtag(","google-analytics"],
            "Google Tag Manager":   ["googletagmanager"],
            "Cloudflare":           ["cloudflare","cf-ray"],
            "Vercel":               ["vercel","x-vercel"],
            "Netlify":              ["netlify"],
            "Stripe":               ["stripe.com","stripe.js"],
        }

        sub("🔍 Detected Technologies")
        tech_found=[]
        for name,sigs in TECH_SIGS.items():
            if any(s in hl for s in sigs):
                tech_found.append(name)
                print(f"    {C.BGREEN}✓{C.R} {C.BOLD}{name}{C.R}")

        if not tech_found: warn("No known tech detected")

        sub("🖥️  Server Headers")
        headers,status=req_headers(f"https://{domain}")
        for h in ["Server","X-Powered-By","X-Generator","CF-Ray","X-Vercel-Id"]:
            if h in headers: res(h,headers[h],"info")

        sub("🤖 Robots.txt")
        robots=req_text(f"https://{domain}/robots.txt")
        if robots and "User-agent" in robots:
            lines=[l for l in robots.splitlines() if l.strip()][:15]
            for l in lines: print(f"    {C.GRAY}{l}{C.R}")
        else: warn("No robots.txt")

        sub("🗺️  Sitemap")
        sitemap=req_text(f"https://{domain}/sitemap.xml")
        if sitemap and "<url" in sitemap:
            urls=re.findall(r'<loc>(.*?)</loc>',sitemap)
            res("Sitemap URLs",str(len(urls)),"info")
            for u in urls[:5]: print(f"    {C.GRAY}•{C.R} {C.BWHITE}{u[:80]}{C.R}")
        else: warn("No sitemap.xml")

        ok(f"Web Tech Profiler done — {len(tech_found)} technologies")
