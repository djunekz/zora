import re
import socket
import ssl
import json
import time
import base64
import hashlib
import threading
import ipaddress
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

from zora.core import *


class CMSScanner:
    @staticmethod
    def run(domain):
        sec("CMS VULNERABILITY SCANNER", "🔎")
        dots("Detecting CMS")
        html_src = req_text(f"https://{domain}") or req_text(f"http://{domain}")
        hl = html_src.lower() if html_src else ""

        cms = "Unknown"
        if "wp-content" in hl or "wp-includes" in hl: cms="WordPress"
        elif "joomla" in hl or "option=com_" in hl:   cms="Joomla"
        elif "drupal" in hl or "sites/default" in hl:  cms="Drupal"
        elif "shopify" in hl:  cms="Shopify"
        elif "magento" in hl:  cms="Magento"
        elif "typo3"   in hl:  cms="TYPO3"
        res("Detected CMS", cms, "info")

        if cms=="WordPress":
            sub("🔵 WordPress Checks")
            ver_m = re.search(r'content="WordPress ([\d.]+)"', html_src or "")
            if ver_m: res("WP Version", ver_m.group(1), "warning")
            th(["Path","Status","Risk"])
            for path, label in [
                ("/wp-login.php","Login Page"),("/wp-admin/","Admin Panel"),
                ("/xmlrpc.php","XML-RPC (attack surface)"),("/wp-json/","REST API"),
                ("/wp-config.php.bak","Config Backup!"),("/.env",".env File!"),
                ("/wp-content/debug.log","Debug Log!"),("/readme.html","Readme (version leak)"),
                ("/wp-cron.php","WP-Cron"),
            ]:
                _, code = req_headers(f"https://{domain}{path}")
                if code==200:
                    risk = "HIGH" if "!" in label else "MED"
                else:
                    risk = "OK"
                tr([path, str(code), f"{risk} — {label}"], "found" if code==200 else "")

            plugins = list(set(re.findall(r'/wp-content/plugins/([a-z0-9\-]+)/', html_src or "", re.I)))
            if plugins:
                sub("🔌 Detected Plugins")
                for p in plugins[:15]: print(f"    {C.BCYAN}•{C.R} {p}")
            theme_m = re.search(r'/wp-content/themes/([a-z0-9\-]+)/', html_src or "", re.I)
            if theme_m: res("Active Theme", theme_m.group(1), "info")

        elif cms=="Joomla":
            sub("🟠 Joomla Checks")
            for path, label in [("/administrator/","Admin"),("/configuration.php","Config"),("/cache/","Cache"),("/tmp/","Tmp")]:
                _, code = req_headers(f"https://{domain}{path}")
                res(label, str(code), "warning" if code==200 else "info")

        elif cms=="Drupal":
            sub("🟢 Drupal Checks")
            for path, label in [("/user/login","Login"),("/admin","Admin"),("/CHANGELOG.txt","Changelog"),("/install.php","Installer")]:
                _, code = req_headers(f"https://{domain}{path}")
                res(label, str(code), "warning" if code==200 else "info")

        sub("⚠️  Generic Sensitive Paths")
        exposed = []
        for path in ["/.git/HEAD","/.git/config","/.env","/.htaccess","/backup.zip",
                     "/backup.sql","/db.sql","/admin","/phpmyadmin","/.DS_Store",
                     "/config.json","/config.yml","/web.config"]:
            _, code = req_headers(f"https://{domain}{path}")
            if code==200:
                exposed.append(path); warn(f"EXPOSED: {path} (HTTP 200)")
        if not exposed: ok("No generic sensitive paths exposed")
        ok(f"CMS Scan done — {cms}, {len(exposed)} exposed paths")
