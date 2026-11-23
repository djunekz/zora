import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zora.core import C, VERSION, tw, print_banner, err
from zora.modules import (
    IPIntel, DomainIntel, EmailIntel, UsernameOSINT, PhoneIntel,
    PortScanner, CIDRScanner, DNSAnalyzer, SubdomainAdvanced, BGPLookup,
    GeoTraceroute, NetUtils, IPv6Scanner, BannerGrabber, NetworkDiag,
    LocalNetScanner, WebTechProfiler, SSLAnalyzer, MetadataExtractor,
    WHOISHistory, URLAnalyzer, WAFDetector, CVELookup, HeaderAuditor,
    CMSScanner, RedirectTester, DirBrute, TakeoverChecker, APIFinder,
    ProxyChecker, ShodanFree, PeopleOSINT, DarkWebMonitor, CTMonitor,
    TyposquatChecker, PassiveDNS, DorkGenerator, SocMINT, BreachResources,
    CryptoToolbox, BulkWhois, ReportExporter, UpdateChecker,
)

def print_menu():
    w=tw()
    print(f"""
{C.BCYAN}{C.BOLD}┌─ CORE OSINT{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 1{C.R}  {C.BOLD}IP Intelligence{C.R}              {C.GRAY}Multi-source IP + Shodan + BGP + ports{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 2{C.R}  {C.BOLD}Domain Intelligence{C.R}          {C.GRAY}WHOIS, DNS, SSL, subdomains, headers, tech{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 3{C.R}  {C.BOLD}Email Intelligence{C.R}           {C.GRAY}MX, SPF, DMARC, DKIM, disposable, SMTP{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 4{C.R}  {C.BOLD}Username OSINT{C.R}               {C.GRAY}50+ platforms + GitHub deep + NPM + PyPI{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 5{C.R}  {C.BOLD}Phone Intelligence{C.R}           {C.GRAY}Country, carrier, format, lookups{C.R}
{C.BCYAN}│{C.R}
{C.BCYAN}├─ NETWORK & INFRA{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 6{C.R}  {C.BOLD}Advanced Port Scanner{C.R}        {C.GRAY}Threaded, with banner grabbing{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 7{C.R}  {C.BOLD}CIDR / Network Scan{C.R}          {C.GRAY}Live host discovery on IP range{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 8{C.R}  {C.BOLD}DNS Full Analyzer{C.R}            {C.GRAY}All record types + propagation + DNSSEC{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 9{C.R}  {C.BOLD}Subdomain Scanner{C.R}            {C.GRAY}100+ wordlist + zone transfer attempt{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}10{C.R}  {C.BOLD}BGP / ASN Lookup{C.R}             {C.GRAY}ASN details, prefixes, routing{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}11{C.R}  {C.BOLD}Traceroute + Geo{C.R}             {C.GRAY}Hop-by-hop with geolocation{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}12{C.R}  {C.BOLD}Network Utilities{C.R}            {C.GRAY}My IP, local net, IPv6, latency{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}13{C.R}  {C.BOLD}IPv6 Deep Scanner{C.R}            {C.GRAY}AAAA records, IPv6 ports, connectivity{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}14{C.R}  {C.BOLD}Advanced Banner Grabber{C.R}      {C.GRAY}Multi-protocol banners + SSL fingerprint{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}15{C.R}  {C.BOLD}Network Diagnostics{C.R}          {C.GRAY}Ping stats, TCP timing, jitter, PTR{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}16{C.R}  {C.BOLD}Local Network Scanner{C.R}        {C.GRAY}Interfaces, ARP, WiFi, gateway ports{C.R}
{C.BCYAN}│{C.R}
{C.BCYAN}├─ WEB & ANALYSIS{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}17{C.R}  {C.BOLD}Web Tech Profiler{C.R}            {C.GRAY}50+ tech signatures + robots + sitemap{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}18{C.R}  {C.BOLD}SSL/TLS Deep Analyzer{C.R}        {C.GRAY}Cert, CT logs, ciphers, expiry{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}19{C.R}  {C.BOLD}URL Metadata Extractor{C.R}       {C.GRAY}OG tags, meta, scripts, comments{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}20{C.R}  {C.BOLD}WHOIS + Domain History{C.R}       {C.GRAY}Full WHOIS + Wayback + crt.sh{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}21{C.R}  {C.BOLD}URL / Link Deep Analyzer{C.R}     {C.GRAY}Decompose, detect patterns, reputation{C.R}
{C.BCYAN}│{C.R}
{C.BCYAN}├─ SECURITY & VULN{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}22{C.R}  {C.BOLD}WAF / CDN Detector{C.R}           {C.GRAY}13 WAF signatures + CDN fingerprint{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}23{C.R}  {C.BOLD}CVE / Vuln Lookup{C.R}            {C.GRAY}NVD database + Exploit-DB + OSV links{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}24{C.R}  {C.BOLD}HTTP Header Auditor{C.R}          {C.GRAY}9 headers + grade + cookie check{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}25{C.R}  {C.BOLD}CMS Vulnerability Scanner{C.R}    {C.GRAY}WP/Joomla/Drupal paths + exposed files{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}26{C.R}  {C.BOLD}Open Redirect & SSRF Tester{C.R}  {C.GRAY}Redirect chain + payload generator{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}27{C.R}  {C.BOLD}Directory Brute Forcer{C.R}       {C.GRAY}70+ wordlist, threaded, status codes{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}28{C.R}  {C.BOLD}DNS Takeover Checker{C.R}         {C.GRAY}CNAME dangling + 8 service signatures{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}29{C.R}  {C.BOLD}API Endpoint Finder{C.R}          {C.GRAY}40+ paths + GraphQL introspection{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}30{C.R}  {C.BOLD}Tor/Proxy/VPN Checker{C.R}        {C.GRAY}Tor DNS + DNSBL + ip-api reputation{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}31{C.R}  {C.BOLD}Shodan Alternatives{C.R}          {C.GRAY}InternetDB, GreyNoise, Censys, FOFA{C.R}
{C.BCYAN}│{C.R}
{C.BCYAN}├─ PEOPLE & IDENTITY OSINT{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}32{C.R}  {C.BOLD}People / Identity OSINT{C.R}      {C.GRAY}People search + face search + email perms{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}33{C.R}  {C.BOLD}Dark Web & Paste Monitor{C.R}     {C.GRAY}Paste sites + breach DBs + HIBP check{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}34{C.R}  {C.BOLD}Certificate Transparency{C.R}     {C.GRAY}crt.sh monitor + sensitive subdomain detect{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}35{C.R}  {C.BOLD}Typosquatting Checker{C.R}        {C.GRAY}80 variants generated + live check{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}36{C.R}  {C.BOLD}Passive DNS History{C.R}          {C.GRAY}CT history + Wayback + ViewDNS links{C.R}
{C.BCYAN}│{C.R}
{C.BCYAN}├─ ADVANCED TOOLS{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}37{C.R}  {C.BOLD}Google Dork Generator{C.R}        {C.GRAY}16 custom dorks for target{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}38{C.R}  {C.BOLD}SOCMINT{C.R}                      {C.GRAY}Social media + OSINT engine links{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}39{C.R}  {C.BOLD}Breach Resources{C.R}             {C.GRAY}Breach DBs + dark web + paste sites{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}40{C.R}  {C.BOLD}Hash & Crypto Toolbox{C.R}        {C.GRAY}Hashes, encode/decode, Caesar{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}41{C.R}  {C.BOLD}Bulk WHOIS Checker{C.R}           {C.GRAY}Multiple domains, expiry alert{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}42{C.R}  {C.BOLD}Report Exporter{C.R}              {C.GRAY}Save scan results as JSON report{C.R}
{C.BCYAN}│{C.R}
{C.BCYAN}├─ SYSTEM{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE}43{C.R}  {C.BOLD}Check for Updates{C.R}           {C.GRAY}Compare your version against the latest GitHub release{C.R}
{C.BCYAN}│{C.R}  {C.BWHITE} 0{C.R}  {C.BOLD}Exit{C.R}
{C.BCYAN}└{'─'*(w-2)}{C.R}""")

def inp(prompt):
    return input(f"  {C.BMAGENTA}❯{C.R} {C.BOLD}{prompt}:{C.R} ").strip()

def pause():
    input(f"\n  {C.GRAY}Press Enter to continue...{C.R}")
    print("\n" * 2)
    print_banner()

def main():
    print("\n" * 2)
    print_banner()
    while True:
        print_menu()
        try:
            ch=input(f"\n  {C.BMAGENTA}❯{C.R} {C.BOLD}Select [{C.BCYAN}0-43{C.BOLD}]:{C.R} ").strip()
            if ch=="0":
                print(f"\n  {C.BGREEN}Thanks for using ZORA v{VERSION}! 🚀{C.R}\n"); break
            elif ch=="1":  IPIntel.run(inp("Enter IP address")); pause()
            elif ch=="2":  DomainIntel.run(inp("Enter domain")); pause()
            elif ch=="3":  EmailIntel.run(inp("Enter email")); pause()
            elif ch=="4":  UsernameOSINT.run(inp("Enter username")); pause()
            elif ch=="5":  PhoneIntel.run(inp("Enter phone (e.g. +628123456789)")); pause()
            elif ch=="6":
                t=inp("Target (IP/domain)"); p=inp("Ports (e.g. 80 or 1-1000 or 80,443,8080)")
                PortScanner.run(t,p); pause()
            elif ch=="7":  CIDRScanner.run(inp("Enter CIDR (e.g. 192.168.1.0/24)")); pause()
            elif ch=="8":  DNSAnalyzer.run(inp("Enter domain")); pause()
            elif ch=="9":  SubdomainAdvanced.run(inp("Enter domain")); pause()
            elif ch=="10": BGPLookup.run(inp("Enter IP or ASN (e.g. AS13335)")); pause()
            elif ch=="11": GeoTraceroute.run(inp("Enter IP or domain")); pause()
            elif ch=="12": NetUtils.run(); pause()
            elif ch=="13": IPv6Scanner.run(inp("Enter domain")); pause()
            elif ch=="14": BannerGrabber.run(inp("Enter IP or domain")); pause()
            elif ch=="15": NetworkDiag.run(inp("Enter IP or domain")); pause()
            elif ch=="16": LocalNetScanner.run(); pause()
            elif ch=="17": WebTechProfiler.run(inp("Enter domain")); pause()
            elif ch=="18": SSLAnalyzer.run(inp("Enter domain")); pause()
            elif ch=="19": MetadataExtractor.run(inp("Enter URL")); pause()
            elif ch=="20": WHOISHistory.run(inp("Enter domain")); pause()
            elif ch=="21": URLAnalyzer.run(inp("Enter URL")); pause()
            elif ch=="22": WAFDetector.run(inp("Enter domain")); pause()
            elif ch=="23": CVELookup.run(inp("Enter CVE ID or software name")); pause()
            elif ch=="24": HeaderAuditor.run(inp("Enter domain")); pause()
            elif ch=="25": CMSScanner.run(inp("Enter domain")); pause()
            elif ch=="26": RedirectTester.run(inp("Enter domain")); pause()
            elif ch=="27": DirBrute.run(inp("Enter domain")); pause()
            elif ch=="28": TakeoverChecker.run(inp("Enter domain")); pause()
            elif ch=="29": APIFinder.run(inp("Enter domain")); pause()
            elif ch=="30": ProxyChecker.run(inp("Enter IP address")); pause()
            elif ch=="31": ShodanFree.run(inp("Enter IP or keyword")); pause()
            elif ch=="32": PeopleOSINT.run(inp("Enter full name")); pause()
            elif ch=="33": DarkWebMonitor.run(inp("Enter email/username/keyword")); pause()
            elif ch=="34": CTMonitor.run(inp("Enter domain")); pause()
            elif ch=="35": TyposquatChecker.run(inp("Enter domain")); pause()
            elif ch=="36": PassiveDNS.run(inp("Enter domain")); pause()
            elif ch=="37": DorkGenerator.run(inp("Enter domain or keyword")); pause()
            elif ch=="38": SocMINT.run(inp("Enter name/username/keyword")); pause()
            elif ch=="39": BreachResources.run(inp("Enter email/username/keyword")); pause()
            elif ch=="40": CryptoToolbox.analyze(inp("Enter text")); pause()
            elif ch=="41": BulkWhois.run(inp("Enter domains (comma/space separated)")); pause()
            elif ch=="42": ReportExporter.quick_save(inp("Enter target name/description")); pause()
            elif ch=="43": UpdateChecker.run(); pause()
            else:
                err("Invalid option"); time.sleep(1)
                print("\n" * 2); print_banner()
        except KeyboardInterrupt:
            print(f"\n\n  {C.BGREEN}Bye! 🚀{C.R}\n"); break
        except Exception as e:
            err(f"Error: {e}"); pause()

def run_cli():
    parser = argparse.ArgumentParser(prog="zora", description="ZORA OSINT Framework")
    parser.add_argument("module", nargs="?", help="Module name to run directly (e.g. ip, domain, email)")
    parser.add_argument("target", nargs="?", help="Target value for the module")
    parser.add_argument("extra", nargs="?", help="Extra argument (e.g. ports for port scanner)")
    args = parser.parse_args()

    direct = {
        "ip": lambda: IPIntel.run(args.target),
        "domain": lambda: DomainIntel.run(args.target),
        "email": lambda: EmailIntel.run(args.target),
        "username": lambda: UsernameOSINT.run(args.target),
        "phone": lambda: PhoneIntel.run(args.target),
        "port": lambda: PortScanner.run(args.target, args.extra or "1-1000"),
        "cidr": lambda: CIDRScanner.run(args.target),
        "dns": lambda: DNSAnalyzer.run(args.target),
        "subdomain": lambda: SubdomainAdvanced.run(args.target),
        "ssl": lambda: SSLAnalyzer.run(args.target),
        "whois": lambda: WHOISHistory.run(args.target),
        "waf": lambda: WAFDetector.run(args.target),
        "headers": lambda: HeaderAuditor.run(args.target),
        "cms": lambda: CMSScanner.run(args.target),
        "dirbrute": lambda: DirBrute.run(args.target),
        "typosquat": lambda: TyposquatChecker.run(args.target),
        "update": lambda: UpdateChecker.run(),
    }

    if args.module and args.module in direct:
        print("\n" * 2)
        print_banner()
        direct[args.module]()
        return True
    if args.module:
        err(f"Unknown CLI module: {args.module}")
        print(f"  Available: {', '.join(sorted(direct))}")
        return True
    return False

def cli():
    if not run_cli():
        main()

if __name__ == "__main__":
    cli()
