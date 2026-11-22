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


class WAFDetector:
    WAF_SIGNATURES = {
        "Cloudflare":        ["cloudflare","cf-ray","__cfduid","cf-cache-status"],
        "Akamai":            ["akamai","x-check-cacheable","x-akamai-transformed"],
        "AWS WAF":           ["awswaf","x-amzn-requestid","x-amz-cf-id"],
        "Sucuri":            ["sucuri","x-sucuri-id","x-sucuri-cache"],
        "Imperva/Incapsula": ["incapsula","x-iinfo","visid_incap"],
        "F5 BIG-IP":         ["bigipserver","x-cnection","f5-bigip"],
        "ModSecurity":       ["mod_security","modsec","x-modsecurity"],
        "Wordfence":         ["wordfence","wf_"],
        "Fastly":            ["fastly","x-fastly-request-id","x-served-by"],
        "Varnish":           ["x-varnish","via varnish"],
        "Wallarm":           ["wallarm"],
        "DDoS-Guard":        ["ddos-guard"],
        "Radware":           ["x-sl-compstate","rdwr"],
    }

    @staticmethod
    def run(domain):
        sec("WAF / CDN DETECTOR", "🛡️")
        dots("Probing WAF signatures")
        headers, status = req_headers(f"https://{domain}")
        html_src = req_text(f"https://{domain}")
        all_text = " ".join([k.lower()+" "+v.lower() for k,v in headers.items()]) + " " + html_src.lower()[:2000]

        sub("🔍 WAF Detection")
        detected = []
        for waf, sigs in WAFDetector.WAF_SIGNATURES.items():
            if any(s in all_text for s in sigs):
                detected.append(waf)
                ok(f"Detected: {waf}")
        if not detected:
            warn("No known WAF detected (or WAF is well-hidden)")

        sub("📋 Security-Related Headers")
        for h in ["CF-Ray","X-Cache","Via","X-Powered-By","Server","X-Sucuri-ID","X-Fastly-Request-ID"]:
            if h in headers: res(h, headers[h][:80], "info")

        sub("🌐 CDN Fingerprint")
        cdn_map = {"cloudflare":"Cloudflare","akamai":"Akamai","fastly":"Fastly",
                   "cloudfront":"AWS CloudFront","vercel":"Vercel","netlify":"Netlify",
                   "azureedge":"Azure CDN","bunnycdn":"BunnyCDN"}
        srv = headers.get("Server","").lower()+headers.get("Via","").lower()
        cdn_found = [name for key,name in cdn_map.items() if key in srv or key in all_text[:500]]
        res("CDN", ", ".join(cdn_found) if cdn_found else "None detected", "info" if cdn_found else "warning")

        sub("🔥 WAF Bypass Hints")
        for tip in ["Try: X-Forwarded-For: 127.0.0.1","Try: X-Originating-IP: 127.0.0.1",
                    "Try encoding payloads: %00, %0a, double URL encode",
                    "Try case variations: <ScRiPt>, <IMG/src=x>",
                    "Try alternate HTTP methods: PUT, PATCH, OPTIONS"]:
            print(f"    {C.GRAY}•{C.R} {C.DIM}{tip}{C.R}")
        ok(f"WAF Detection done — {len(detected)} WAF(s) found")
