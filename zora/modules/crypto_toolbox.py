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


class CryptoToolbox:
    @staticmethod
    def analyze(text):
        sec("HASH & CRYPTO TOOLBOX", "🔐")
        b = text.encode()

        sub("🔒 Hash Generation")
        for name,h in [
            ("MD5",    hashlib.md5(b).hexdigest()),
            ("SHA1",   hashlib.sha1(b).hexdigest()),
            ("SHA256", hashlib.sha256(b).hexdigest()),
            ("SHA512", hashlib.sha512(b).hexdigest()),
            ("SHA3-256",hashlib.sha3_256(b).hexdigest()),
            ("BLAKE2b", hashlib.blake2b(b).hexdigest()[:64]),
        ]: res(name, h, "info")

        sub("📝 Encoding / Decoding")
        b64 = base64.b64encode(b).decode()
        b32 = base64.b32encode(b).decode()
        hex_ = b.hex()
        url_ = urllib.parse.quote(text)
        res("Base64",  b64,"info")
        res("Base32",  b32,"info")
        res("Hex",     hex_,"info")
        res("URL-enc", url_,"info")

        sub("🔄 Decode Attempts")
        try:
            dec64=base64.b64decode(text+"==").decode(errors='ignore')
            if dec64.isprintable(): res("Base64 Decode", dec64[:80],"success")
        except: pass
        try:
            dechex=bytes.fromhex(text).decode(errors='ignore')
            if dechex.isprintable(): res("Hex Decode", dechex[:80],"success")
        except: pass

        sub("🔑 Caesar Cipher (ROT brute force)")
        for shift in [1,3,13,25]:
            rot=''.join(chr((ord(c)-65+shift)%26+65) if c.isupper()
                       else chr((ord(c)-97+shift)%26+97) if c.islower()
                       else c for c in text)
            res(f"ROT{shift}", rot[:60],"info")

        ok("Crypto Toolbox done")
