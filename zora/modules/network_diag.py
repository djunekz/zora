import re
import socket
import time

from zora.core import cmd, ok, res, reverse_dns, sec, sub, warn


class NetworkDiag:
    @staticmethod
    def run(target):
        sec("NETWORK DIAGNOSTICS", "📡")

        sub("🏓 Ping Statistics (10 packets)")
        ping_out=cmd(["ping","-c","10","-i","0.2",target])
        times=[float(t) for t in re.findall(r'time=([\d.]+)',ping_out)]
        if times:
            avg=sum(times)/len(times)
            res("Received",   str(len(times))+"/10","success" if len(times)==10 else "warning")
            res("Packet Loss",f"{10-len(times)}/10 lost","success" if len(times)==10 else "error")
            res("Min/Avg/Max", f"{min(times):.1f}/{avg:.1f}/{max(times):.1f} ms","info")
            jitter=max(times)-min(times)
            res("Jitter",     f"{jitter:.1f} ms","success" if jitter<20 else "warning")
        else: warn("Target unreachable or ICMP blocked")

        sub("🔌 TCP Handshake Timing")
        for port in [80,443,22]:
            try:
                t0=time.time()
                s=socket.socket(); s.settimeout(5)
                result=s.connect_ex((target,port))
                ms=(time.time()-t0)*1000; s.close()
                if result==0: res(f"TCP:{port}",f"{ms:.1f} ms","success" if ms<100 else "warning")
                else: res(f"TCP:{port}","closed/filtered","info")
            except Exception as e: res(f"TCP:{port}",f"error: {e}","warning")

        sub("🔄 Reverse DNS")
        rdns=reverse_dns(target)
        res("PTR Record",rdns or "No PTR","info" if rdns else "warning")
        ok("Network Diagnostics done")
