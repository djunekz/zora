import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from zora.core import bar, err, grab_banner, inf, ok, port_open, sec, sub, th, tr, warn

MAX_WORKERS = 100


class PortScanner:
    @staticmethod
    def _scan_one(target, port):
        if not port_open(target, port, 0.4):
            return None
        try: svc = socket.getservbyport(port)
        except: svc = "Unknown"
        banner = grab_banner(target, port)
        return (port, svc, banner)

    @staticmethod
    def run(target, ports_str):
        sec("ADVANCED PORT SCANNER", "🔌")
        try:
            if '-' in ports_str:
                s,e=map(int,ports_str.split('-'))
                plist=list(range(s,min(e+1,65536)))
            elif ',' in ports_str:
                plist=[int(p.strip()) for p in ports_str.split(',')]
            else:
                plist=[int(ports_str)]
        except: err("Invalid port format"); return

        inf("Target", target, 2)
        inf("Ports",  f"{len(plist)} ports", 2)

        open_ports=[]
        done = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(PortScanner._scan_one, target, p): p for p in plist}
            for fut in as_completed(futures):
                done += 1
                if done % 10 == 0 or done == len(plist):
                    bar(done, len(plist), "Scanning")
                result = fut.result()
                if result: open_ports.append(result)
        bar(len(plist),len(plist),"Scanning")

        if open_ports:
            open_ports.sort(key=lambda x:x[0])
            sub(f"✅ Open Ports ({len(open_ports)})")
            th(["Port","Service","Banner"])
            for port,svc,ban in open_ports:
                tr([str(port),svc,ban[:40] if ban else "-"],"found")
        else: warn("No open ports found")

        ok(f"Port scan done — {len(open_ports)}/{len(plist)} open")
