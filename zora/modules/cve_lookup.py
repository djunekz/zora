import urllib.request
import urllib.parse
import urllib.error

from zora.core import C, dots, ok, req_json, res, sec, sub, th, tr, warn


class CVELookup:
    @staticmethod
    def run(query):
        sec("CVE / VULNERABILITY LOOKUP", "💀")
        dots("Querying NVD & vulnerability DBs")
        encoded = urllib.parse.quote(query)

        sub("🔍 NVD (National Vulnerability Database)")
        nvd = req_json(f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={encoded}&resultsPerPage=10")
        if nvd and nvd.get("vulnerabilities"):
            vulns = nvd["vulnerabilities"]
            res("Total Matches", str(nvd.get("totalResults", len(vulns))), "info")
            th(["CVE ID","Severity","Score","Published"])
            for item in vulns[:10]:
                cve = item.get("cve", {})
                cve_id = cve.get("id","?")
                published = str(cve.get("published","?"))[:10]
                metrics = cve.get("metrics",{})
                score = "N/A"; sev = "N/A"
                for key in ["cvssMetricV31","cvssMetricV30","cvssMetricV2"]:
                    if key in metrics and metrics[key]:
                        m = metrics[key][0].get("cvssData",{})
                        score = str(m.get("baseScore","?"))
                        sev   = m.get("baseSeverity","?")
                        break
                color = "found" if sev in ("CRITICAL","HIGH") else "warn" if sev=="MEDIUM" else ""
                tr([cve_id, sev, score, published], color)
                for d in cve.get("descriptions",[]):
                    if d.get("lang")=="en":
                        print(f"      {C.DIM}{d['value'][:120]}...{C.R}"); break
        else:
            warn("No CVEs found or NVD API unavailable")

        sub("🔗 Additional Resources")
        for name, url in [
            ("NVD Search",   f"https://nvd.nist.gov/vuln/search/results?query={encoded}"),
            ("Exploit-DB",   f"https://www.exploit-db.com/search?q={encoded}"),
            ("Vulhub",       f"https://github.com/vulhub/vulhub/search?q={encoded}"),
            ("Packet Storm", f"https://packetstormsecurity.com/search/?q={encoded}"),
            ("Shodan CVE",   f"https://www.shodan.io/search?query=vuln:{query}"),
            ("OSV.dev",      f"https://osv.dev/list?q={encoded}"),
        ]: print(f"    {C.BRED}•{C.R} {C.BOLD}{name:<18}{C.R} {C.GRAY}{url[:80]}{C.R}")
        ok("CVE Lookup done")
