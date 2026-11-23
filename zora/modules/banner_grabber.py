import socket
import ssl
import time

from zora.core import ok, req_headers, res, sec, sub, th, tr, warn


class BannerGrabber:
    SERVICE_PROBES = {
        21: (b"",                                    "FTP"),
        22: (b"",                                    "SSH"),
        25: (b"EHLO zora.local\r\n",                "SMTP"),
        80: (b"HEAD / HTTP/1.0\r\nHost: x\r\n\r\n", "HTTP"),
        110:(b"",                                    "POP3"),
        143:(b"",                                    "IMAP"),
        3306:(b"\x00",                               "MySQL"),
        6379:(b"*1\r\n$4\r\nPING\r\n",              "Redis"),
        9200:(b"GET / HTTP/1.0\r\n\r\n",             "Elasticsearch"),
    }

    @staticmethod
    def run(target):
        sec("ADVANCED BANNER GRABBER", "🏷️")
        sub("🔍 Multi-Protocol Banner Grab")
        th(["Port","Service","Banner"])
        for port,(probe,svc) in BannerGrabber.SERVICE_PROBES.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                if s.connect_ex((target,port))==0:
                    if probe: s.send(probe)
                    time.sleep(0.3)
                    try: banner = s.recv(2048).decode(errors='ignore').strip().replace('\r','').replace('\n',' ')
                    except: banner=""
                    s.close()
                    tr([str(port),svc,banner[:70] if banner else "(connected, no banner)"],"found")
                else:
                    tr([str(port),svc,"closed"],"notfound")
            except Exception as e:
                tr([str(port),svc,f"error: {e}"],"notfound")

        sub("🌐 HTTP Server Fingerprint")
        for scheme in ["https","http"]:
            h, status = req_headers(f"{scheme}://{target}")
            if status>0:
                res("Scheme",str(scheme.upper()),"info"); res("Status",str(status),"info")
                for hdr in ["Server","X-Powered-By","X-Generator","Via"]:
                    if hdr in h: res(hdr,h[hdr],"warning")
                break

        sub("🔐 SSL/TLS Fingerprint")
        try:
            ctx = ssl.create_default_context()
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            with socket.create_connection((target,443),timeout=5) as sk:
                with ctx.wrap_socket(sk,server_hostname=target) as ss:
                    ci = ss.cipher()
                    res("TLS Version",ss.version(),"info")
                    res("Cipher",ci[0] if ci else "?","info")
                    res("Bits",str(ci[2]) if ci and len(ci)>2 else "?","info")
        except Exception as e: warn(f"SSL not available: {e}")
        ok("Banner Grab done")
