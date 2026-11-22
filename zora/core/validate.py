import re
import ipaddress


def is_ip(s):
    try: ipaddress.ip_address(s); return True
    except: return False

def is_ipv6(s):
    try: ipaddress.IPv6Address(s); return True
    except: return False

def is_domain(s):
    return bool(re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', s))

def is_email(s):
    return bool(re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', s))

def is_user(s):
    return bool(re.match(r'^[a-zA-Z0-9_\-\.]{2,40}$', s))

def is_phone(s):
    return bool(re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', s))

def is_cidr(s):
    try: ipaddress.ip_network(s, strict=False); return True
    except: return False
