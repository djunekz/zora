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


class BGPLookup:
    @staticmethod
    def run(target):
        sec("BGP / ASN INTELLIGENCE", "🔗")
        dots("Querying BGP data")

        if re.match(r'^(AS)?[0-9]+$', target, re.I):
            asn=re.sub(r'[^0-9]','',target)
            data=req_json(f"https://api.bgpview.io/asn/{asn}")
            if data and data.get("status")=="ok":
                d=data.get("data",{})
                sub("📊 ASN Details")
                for k,v in [("ASN",d.get("asn")),("Name",d.get("name")),
                            ("Description",d.get("description_short")),
                            ("Country",d.get("country_code")),
                            ("Website",d.get("website"))]:
                    if v: res(str(k),str(v)[:80],"info")

                prefixes=req_json(f"https://api.bgpview.io/asn/{asn}/prefixes")
                if prefixes and prefixes.get("status")=="ok":
                    sub("🌐 IP Prefixes")
                    v4=prefixes["data"].get("ipv4_prefixes",[])
                    res("IPv4 Prefixes",str(len(v4)),"info")
                    th(["Prefix","Name","Description"])
                    for p in v4[:10]:
                        tr([p.get("prefix",""),p.get("name","")[:20],p.get("description","")[:30]],"found")
        else:
            data=req_json(f"https://api.bgpview.io/ip/{target}")
            if data and data.get("status")=="ok":
                sub("🔗 BGP Prefixes for "+target)
                for p in data.get("data",{}).get("prefixes",[]):
                    asn_info=p.get("asn",{})
                    res("Prefix",      p.get("prefix","?"),"info")
                    res("ASN",         str(asn_info.get("asn","?")),"info")
                    res("ASN Name",    asn_info.get("name","?"),"info")
                    res("Country",     asn_info.get("country_code","?"),"info")
                    print()

        ok("BGP Lookup done")
