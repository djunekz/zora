import socket
import ipaddress

from zora.core import dns_query, ok, req_json, req_text, res, sec, sub, warn


class IPv6Scanner:
    @staticmethod
    def run(domain):
        sec("IPv6 DEEP SCANNER", "🔵")
        sub("🌐 IPv6 Address Lookup")
        aaaa = dns_query(domain,"AAAA")
        if aaaa:
            for addr in aaaa:
                res("IPv6 Address", addr, "info")
                try:
                    obj = ipaddress.IPv6Address(addr)
                    res("Compressed",  str(obj.compressed),"info")
                    res("Is Global",   str(obj.is_global),"info")
                    res("Is Private",  str(obj.is_private),"info")
                    res("IPv4 Mapped", str(obj.ipv4_mapped) if obj.ipv4_mapped else "No","info")
                except: pass
        else:
            warn("No AAAA records — domain may not support IPv6")

        sub("🔌 IPv6 Port Check")
        if aaaa:
            for port in [80,443,22,25,8080,8443]:
                try:
                    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                    s.settimeout(1)
                    result = s.connect_ex((aaaa[0],port,0,0))
                    s.close()
                    res(f"Port {port}","OPEN" if result==0 else "closed","success" if result==0 else "info")
                except: res(f"Port {port}","error","warning")

        sub("🌍 My IPv6 Address")
        myv6 = req_text("https://api6.ipify.org")
        if myv6 and myv6.strip():
            res("Your IPv6", myv6.strip(), "success")
            geo = req_json(f"https://ipinfo.io/{myv6.strip()}/json")
            if geo:
                res("Location", f"{geo.get('city','?')}, {geo.get('country','?')}", "info")
                res("ISP", geo.get("org","?"), "info")
        else:
            warn("No IPv6 connectivity on your connection")
        ok("IPv6 Deep Scan done")
