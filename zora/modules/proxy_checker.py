
from zora.core import C, dns_query, err, is_ip, ok, req_json, res, sec, sub, warn


class ProxyChecker:
    @staticmethod
    def run(ip):
        sec("TOR / PROXY / VPN / BLACKLIST CHECKER", "🎭")
        if not is_ip(ip): err("Invalid IP address"); return

        sub("🧅 Tor Exit Node Check")
        ip_rev = ".".join(reversed(ip.split(".")))
        tor_dns = dns_query(f"{ip_rev}.dnsel.torproject.org", "A")
        is_tor = "127.0.0.2" in tor_dns
        res("Tor Exit Node","YES — Tor exit node!" if is_tor else "Not a known Tor exit",
            "error" if is_tor else "success")

        sub("🕵️  IP Reputation")
        d2=req_json(f"http://ip-api.com/json/{ip}?fields=proxy,hosting,mobile,isp,org")
        if d2:
            res("Proxy",   "DETECTED" if d2.get("proxy")   else "Clean","warning" if d2.get("proxy")   else "success")
            res("Hosting", "YES"       if d2.get("hosting") else "No",   "warning" if d2.get("hosting") else "info")
            res("Mobile",  "YES"       if d2.get("mobile")  else "No",   "info")
            res("ISP",     d2.get("isp","?"),"info")

        sub("🔍 Blacklist Check (DNSBL)")
        dnsbl_list=["zen.spamhaus.org","bl.spamcop.net","dnsbl.sorbs.net",
                    "b.barracudacentral.org","dnsbl-1.uceprotect.net"]
        listed=[]
        for bl in dnsbl_list:
            result=dns_query(f"{ip_rev}.{bl}", "A")
            if result:
                listed.append(bl); res(f"Listed: {bl}",", ".join(result),"error")
            else:
                res(f"Clean:  {bl}","Not listed","success")
        if listed: warn(f"IP listed on {len(listed)} blacklist(s)!")
        else: ok("IP clean on all checked blacklists")

        sub("🌐 Manual Check Links")
        for nm,url in [
            ("IPQualityScore", f"https://www.ipqualityscore.com/free-ip-lookup-proxy-vpn-test/lookup/{ip}"),
            ("AbuseIPDB",      f"https://www.abuseipdb.com/check/{ip}"),
            ("Scamalytics",    f"https://scamalytics.com/ip/{ip}"),
            ("GreyNoise",      f"https://www.greynoise.io/viz/ip/{ip}"),
        ]: print(f"    {C.BCYAN}•{C.R} {C.BOLD}{nm:<18}{C.R} {C.GRAY}{url}{C.R}")
        ok("Proxy/VPN/Tor check done")
