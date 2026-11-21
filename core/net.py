import json
import socket
import subprocess
import urllib.request
import urllib.error

import dns.resolver
import dns.exception

from zora.core.constants import USER_AGENT

def req_json(url, headers=None, timeout=12):
    h = {"User-Agent": USER_AGENT}
    if headers: h.update(headers)
    try:
        r = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except: return {}

def req_text(url, headers=None, timeout=12):
    h = {"User-Agent": USER_AGENT}
    if headers: h.update(headers)
    try:
        r = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.read().decode(errors='ignore')
    except: return ""

def req_headers(url, timeout=10):
    h = {"User-Agent": USER_AGENT}
    try:
        r = urllib.request.Request(url, headers=h, method="HEAD")
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return dict(resp.headers), resp.status
    except urllib.error.HTTPError as e:
        return dict(e.headers), e.code
    except: return {}, 0

def cmd(args, timeout=30):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.stdout or r.stderr
    except: return ""

def port_open(host, port, timeout=0.5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except: return False

def grab_banner(host, port, timeout=3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = s.recv(1024).decode(errors='ignore').strip()
        s.close()
        return banner[:200]
    except: return ""

def dns_query(domain, rtype="A", nameserver=None, timeout=5):
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        if nameserver:
            resolver.nameservers = [nameserver]
        answers = resolver.resolve(domain, rtype)
        return [str(r).strip('"').rstrip('.') for r in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return []
    except Exception:
        return []


def dns_query_raw(domain, rtype="A", nameserver=None, timeout=5):
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        if nameserver:
            resolver.nameservers = [nameserver]
        answers = resolver.resolve(domain, rtype)
        return [str(r) for r in answers]
    except Exception:
        return []

def reverse_dns(ip):
    try: return socket.gethostbyaddr(ip)[0]
    except: return None


def _whois_raw(server, query, timeout=10):
    with socket.create_connection((server, 43), timeout=timeout) as s:
        s.send((query.strip() + "\r\n").encode())
        chunks = []
        while True:
            data = s.recv(4096)
            if not data:
                break
            chunks.append(data)
        return b"".join(chunks).decode(errors="ignore")


def whois_query(domain, timeout=10):
    domain = domain.strip().lower()
    try:
        iana_resp = _whois_raw("whois.iana.org", domain, timeout)
        refer = None
        for line in iana_resp.splitlines():
            if line.lower().startswith("refer:"):
                refer = line.split(":", 1)[1].strip()
                break
        server = refer or "whois.iana.org"
        resp = _whois_raw(server, domain, timeout)
        if len(resp.strip()) < 20 and refer:
            resp = iana_resp
        return resp
    except Exception:
        return ""
