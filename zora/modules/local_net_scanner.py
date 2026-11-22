import re
import os
import socket
import ssl
import json
import time
import base64
import struct
import hashlib
import shutil
import threading
import ipaddress
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

from zora.core import *


class LocalNetScanner:
    @staticmethod
    def _read_proc_route():
        try:
            with open("/proc/net/route") as f:
                lines = f.readlines()[1:]
        except Exception:
            return None, None
        for line in lines:
            parts = line.split()
            if len(parts) < 3:
                continue
            iface, dest, gateway = parts[0], parts[1], parts[2]
            if dest == "00000000" and gateway != "00000000":
                try:
                    gw_ip = socket.inet_ntoa(struct.pack("<L", int(gateway, 16)))
                    return iface, gw_ip
                except Exception:
                    continue
        return None, None

    @staticmethod
    def _read_proc_arp():
        try:
            with open("/proc/net/arp") as f:
                lines = f.readlines()[1:]
        except Exception:
            return None
        entries = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 6:
                ip_, _hwtype, _flags, mac, _mask, device = parts[:6]
                if mac != "00:00:00:00:00:00":
                    entries.append((ip_, mac, device))
        return entries

    @staticmethod
    def _termux_wifi_info():
        if not shutil.which("termux-wifi-connectioninfo"):
            return None
        raw = cmd(["termux-wifi-connectioninfo"])
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    @staticmethod
    def run():
        sec("LOCAL NETWORK SCANNER", "📶")

        sub("🖥️  Local Interfaces")
        ifconfig=cmd(["ip","addr"]) or cmd(["ifconfig"])
        interfaces=[]
        if ifconfig:
            for iface,ip in re.findall(r'(\w+):\s.*?inet\s([\d.]+)',ifconfig,re.S):
                interfaces.append((iface,ip))
                res(iface,ip,"info")
        else:
            warn("Could not read network interfaces (no 'ip' or 'ifconfig' available)")

        sub("📶 WiFi Info")
        wlan_iface = next((i for i,_ in interfaces if re.match(r'^(wlan|wifi)\d*$', i)), None)
        wlan_ip = next((ip for i,ip in interfaces if i == wlan_iface), None)
        tw = LocalNetScanner._termux_wifi_info()
        if tw:
            if tw.get("ssid"): res("SSID", tw["ssid"], "info")
            if tw.get("bssid"): res("BSSID", tw["bssid"], "info")
            if tw.get("rssi") is not None: res("Signal (RSSI)", f"{tw['rssi']} dBm", "info")
            if tw.get("link_speed") is not None: res("Link Speed", f"{tw['link_speed']} Mbps", "info")
            if tw.get("frequency") is not None: res("Frequency", f"{tw['frequency']} MHz", "info")
        else:
            wifi_info=cmd(["iwconfig"]) or cmd(["nmcli","dev","wifi"])
            ssid_m = re.search(r'ESSID:"([^"]+)"', wifi_info) if wifi_info else None
            if ssid_m:
                res("SSID", ssid_m.group(1), "info")
            elif wlan_iface:
                res("Interface", f"{wlan_iface} active ({wlan_ip})", "info")
                res("SSID", "unavailable — install Termux:API (pkg install termux-api) for SSID/signal detail", "warning")
            else:
                res("WiFi", "No wireless interface detected", "warning")

        sub("🔍 ARP Cache")
        arp=cmd(["arp","-n"]) or cmd(["arp","-a"])
        entries=[]
        if arp:
            entries=re.findall(r'([\d.]+)\s+\S+\s+([0-9a-f:]{17})',arp,re.I)
        if not entries:
            proc_entries = LocalNetScanner._read_proc_arp()
            if proc_entries:
                entries = [(ip_, mac) for ip_, mac, _dev in proc_entries]
        if entries:
            th(["IP","MAC"])
            for ip_,mac in entries[:20]: tr([ip_,mac],"found")
        else:
            warn("ARP cache unavailable on this platform (no 'arp' utility and /proc/net/arp not readable)")

        sub("🌐 Default Gateway")
        route=cmd(["ip","route"]) or cmd(["route","-n"])
        gw_m=re.search(r'default via ([\d.]+)',route) if route else None
        gw = gw_m.group(1) if gw_m else None
        if not gw:
            _iface, gw = LocalNetScanner._read_proc_route()
        if gw:
            res("Default Gateway",gw,"info")
            rdns_=reverse_dns(gw)
            if rdns_: res("Gateway PTR",rdns_,"info")
            sub("📡 Open Ports on Gateway")
            any_open = False
            for port in [80,443,8080,8443,22,23,53]:
                if port_open(gw,port,0.5):
                    any_open = True
                    res(f"Port {port}",f"OPEN ({COMMON_PORTS.get(port,'?')})","warning")
            if not any_open:
                res("Open Ports", "None of the common ports responded", "info")
        else:
            warn("Default gateway unavailable on this platform (no 'ip'/'route' utility and /proc/net/route not readable)")
        ok("Local Network Scan done")
