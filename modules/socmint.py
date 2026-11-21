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


class SocMINT:
    @staticmethod
    def run(query):
        sec("SOCIAL MEDIA INTELLIGENCE (SOCMINT)", "📱")
        q=urllib.parse.quote(query)

        sub("🔍 Multi-Platform Search Links")
        platforms=[
            ("Twitter/X",     f"https://twitter.com/search?q={q}"),
            ("Reddit",        f"https://www.reddit.com/search/?q={q}"),
            ("LinkedIn",      f"https://www.linkedin.com/search/results/all/?keywords={q}"),
            ("Facebook",      f"https://www.facebook.com/search/top?q={q}"),
            ("TikTok",        f"https://www.tiktok.com/search?q={q}"),
            ("YouTube",       f"https://www.youtube.com/results?search_query={q}"),
            ("GitHub",        f"https://github.com/search?q={q}"),
            ("Telegram",      f"https://t.me/s/{query}"),
        ]
        for name,url in platforms:
            print(f"  {C.BGREEN}•{C.R} {C.BOLD}{name:<15}{C.R} {C.GRAY}{url[:80]}{C.R}")

        sub("🕵️  OSINT Search Engines")
        osint_engines=[
            ("IntelX",        f"https://intelx.io/?s={q}"),
            ("Spokeo",        f"https://www.spokeo.com/search?q={q}"),
            ("Webmii",        f"https://webmii.com/people?n={q}"),
        ]
        for name,url in osint_engines:
            print(f"  {C.BCYAN}•{C.R} {C.BOLD}{name:<15}{C.R} {C.GRAY}{url[:80]}{C.R}")

        ok("SOCMINT done")
