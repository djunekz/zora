import ipaddress

from zora.core import C, bar, err, inf, is_cidr, ok, port_open, reverse_dns, sec, sub, th, tr, warn


class CIDRScanner:
    @staticmethod
    def run(cidr):
        sec("CIDR / NETWORK SCANNER", "🔗")
        if not is_cidr(cidr):
            err("Invalid CIDR notation"); return
        net=ipaddress.ip_network(cidr,strict=False)
        inf("Network",   str(net.network_address),2)
        inf("Broadcast", str(net.broadcast_address),2)
        inf("Mask",      str(net.netmask),2)
        inf("Hosts",     str(max(net.num_addresses-2, 0)),2)

        hosts=list(net.hosts())
        if len(hosts)>254:
            warn(f"Large network ({len(hosts)} hosts). Scanning first 100.")
            hosts=hosts[:100]

        sub(f"🔍 Live Host Discovery ({len(hosts)} hosts)")
        alive=[]
        for i,h in enumerate(hosts,1):
            bar(i,len(hosts),"Probing")
            ip=str(h)
            if port_open(ip,80,0.3) or port_open(ip,22,0.3) or port_open(ip,443,0.3):
                rdns_=reverse_dns(ip)
                alive.append((ip,rdns_ or "-"))

        if alive:
            print(f"\n  {C.BGREEN}{len(alive)} live hosts:{C.R}")
            th(["IP","Reverse DNS"])
            for ip,rdns_ in alive: tr([ip,rdns_],"found")
        else: warn("No live hosts found")
        ok(f"CIDR scan done — {len(alive)} alive")
