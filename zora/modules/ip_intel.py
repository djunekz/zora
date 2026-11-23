import re

from zora.core import C, COMMON_PORTS, bar, cmd, dots, err, grab_banner, is_ip, is_ipv6, ok, port_open, req_json, res, reverse_dns, sec, sub, th, tr, warn


class IPIntel:
    @staticmethod
    def run(ip):
        sec("IP INTELLIGENCE", "🌐")
        if not is_ip(ip):
            err("Invalid IP address"); return

        dots("Gathering multi-source intelligence")

        d1 = req_json(f"https://ipinfo.io/{ip}/json")
        d2 = req_json(f"http://ip-api.com/json/{ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query")
        d3 = req_json(f"https://ipapi.co/{ip}/json/")

        sub("📊 Basic Information")
        res("IP", ip, "info")
        res("Version", "IPv6" if is_ipv6(ip) else "IPv4", "info")
        rdns = reverse_dns(ip)
        res("Reverse DNS", rdns or "N/A", "info" if rdns else "warning")

        sub("🌍 Geolocation (3 Sources)")
        if d1:
            res("City [IPInfo]",    d1.get("city","N/A"), "info")
            res("Region",           d1.get("region","N/A"), "info")
            res("Country",          d1.get("country","N/A"), "info")
            res("Coordinates",      d1.get("loc","N/A"), "info")
            res("Organization",     d1.get("org","N/A"), "info")
            res("Timezone",         d1.get("timezone","N/A"), "info")
            res("Postal",           d1.get("postal","N/A"), "info")
        if d2 and d2.get("status")=="success":
            res("Continent [IP-API]", d2.get("continent","N/A"), "info")
            res("ISP",              d2.get("isp","N/A"), "info")
            res("AS",               d2.get("as","N/A"), "info")
            res("AS Name",          d2.get("asname","N/A"), "info")
            res("Currency",         d2.get("currency","N/A"), "info")
            res("Mobile Network",   "Yes" if d2.get("mobile") else "No",
                "warning" if d2.get("mobile") else "info")
            res("Proxy/VPN",        "DETECTED" if d2.get("proxy") else "Clean",
                "warning" if d2.get("proxy") else "success")
            res("Hosting/DC",       "Yes" if d2.get("hosting") else "No",
                "warning" if d2.get("hosting") else "info")
        if d3 and not d3.get("error"):
            res("UTC Offset [ipapi]", str(d3.get("utc_offset","N/A")), "info")
            res("Country Capital",  d3.get("country_capital","N/A"), "info")
            res("Country Population", str(d3.get("country_population","N/A")), "info")
            res("Country Area",     str(d3.get("country_area","N/A"))+" km²", "info")
            res("Calling Code",     d3.get("country_calling_code","N/A"), "info")
            res("Languages",        d3.get("languages","N/A"), "info")

        sub("🚨 Abuse & Reputation")
        shodan = req_json(f"https://internetdb.shodan.io/{ip}")
        if shodan and not shodan.get("detail"):
            sub("🔎 Shodan InternetDB (Open Ports & CVEs)")
            ports = shodan.get("ports",[])
            cpes  = shodan.get("cpes",[])
            vulns = shodan.get("vulns",[])
            tags  = shodan.get("tags",[])
            hostnames = shodan.get("hostnames",[])
            res("Open Ports", ", ".join(map(str,ports)) if ports else "None", "warning" if ports else "success")
            res("CPEs",       ", ".join(cpes[:3]) if cpes else "None", "info")
            res("Tags",       ", ".join(tags) if tags else "None", "info")
            res("Hostnames",  ", ".join(hostnames[:3]) if hostnames else "None", "info")
            if vulns:
                res("⚠ CVEs Found", str(len(vulns)), "error")
                for v in vulns[:5]:
                    print(f"      {C.BRED}• {v}{C.R}")

        sub("🔌 Port Scan (Top 40 Common Ports)")
        open_ports = []
        items = list(COMMON_PORTS.items())[:40]
        for i,(port,svc) in enumerate(items,1):
            bar(i,len(items),"Scanning")
            if port_open(ip,port,0.4):
                banner = grab_banner(ip,port)
                open_ports.append((port,svc,banner))
        if open_ports:
            print(f"\n  {C.BGREEN}Found {len(open_ports)} open port(s):{C.R}")
            th(["Port","Service","Banner"])
            for port,svc,ban in open_ports:
                tr([str(port),svc,ban[:40] if ban else "-"],"found")
        else:
            warn("No open ports in common list")

        sub("📡 Connectivity Test")
        ping = cmd(["ping","-c","5","-i","0.2",ip])
        times = re.findall(r'time=([\d.]+)',ping)
        if times:
            tf = [float(t) for t in times]
            avg = sum(tf)/len(tf)
            res("Avg Latency", f"{avg:.2f} ms", "success" if avg<100 else "warning")
            res("Min/Max",     f"{min(tf):.1f}/{max(tf):.1f} ms","info")
            res("Packet Loss", f"{5-len(tf)}/5 lost","success" if len(tf)==5 else "warning")
        else:
            warn("Host unreachable or ping blocked")

        sub("🔗 BGP / ASN Intelligence")
        bgp = req_json(f"https://api.bgpview.io/ip/{ip}")
        if bgp and bgp.get("status")=="ok":
            prefixes = bgp.get("data",{}).get("prefixes",[])
            if prefixes:
                p = prefixes[0]
                res("BGP Prefix",    p.get("prefix","N/A"), "info")
                asn = p.get("asn",{})
                res("ASN",           str(asn.get("asn","N/A")), "info")
                res("ASN Name",      asn.get("name","N/A"), "info")
                res("ASN Country",   asn.get("country_code","N/A"), "info")
                res("Description",   asn.get("description","N/A")[:60], "info")

        sub("🛡️  Risk Assessment")
        risk = len(open_ports)*3 + (30 if d2 and d2.get("proxy") else 0) + (20 if d2 and d2.get("hosting") else 0)
        lvl  = "LOW" if risk<20 else "MEDIUM" if risk<50 else "HIGH"
        col  = C.BGREEN if lvl=="LOW" else C.BYELLOW if lvl=="MEDIUM" else C.BRED
        print(f"    {C.BOLD}Risk Level: {col}{lvl}{C.R} (score {risk}/100)")
        ok(f"IP Intelligence done — {len(open_ports)} services, Risk: {lvl}")
