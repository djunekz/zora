import json
import difflib
import urllib.request
import urllib.parse
import urllib.error

from concurrent.futures import ThreadPoolExecutor, as_completed

from zora.core import USER_AGENT, bar, inf, ok, res, sec, sub, th, tr, warn

MAX_WORKERS = 40
PROBE_PATH = "/zzq9xf3knotarealpath00112233"
BODY_SAMPLE_BYTES = 8000
SIMILARITY_THRESHOLD = 0.92


API_PATHS = [
    "/api","/api/v1","/api/v2","/api/v3","/rest","/graphql","/query",
    "/swagger","/swagger.json","/swagger.yaml","/openapi.json","/openapi.yaml",
    "/api-docs","/redoc","/v1","/v2","/v3",
    "/api/users","/api/auth","/api/login","/api/token","/api/health",
    "/api/status","/api/version","/api/info","/api/ping","/api/data",
    "/.well-known/openid-configuration","/.well-known/oauth-authorization-server",
    "/metrics","/health","/healthz","/ready","/readyz","/status","/ping",
    "/actuator","/actuator/health","/actuator/info","/actuator/env",
    "/wp-json","/wp-json/wp/v2","/wp-json/wp/v2/users",
]

class APIFinder:
    @staticmethod
    def _get(url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=6) as resp:
                body = resp.read(BODY_SAMPLE_BYTES).decode(errors="ignore")
                return resp.status, dict(resp.headers), body
        except urllib.error.HTTPError as e:
            try:
                body = e.read(BODY_SAMPLE_BYTES).decode(errors="ignore")
            except Exception:
                body = ""
            return e.code, dict(e.headers), body
        except Exception:
            return None, {}, ""

    @staticmethod
    def run(domain):
        sec("API ENDPOINT FINDER", "🔌")
        inf("Target",domain,2); inf("Wordlist",f"{len(API_PATHS)} paths",2)

        wc_status, _, wc_body = APIFinder._get(f"https://{domain}{PROBE_PATH}")
        wildcard = wc_status in (200,201,400,401,403,405,422)
        if wildcard:
            warn(f"Wildcard response detected (HTTP {wc_status} for a random nonexistent path) — filtering false positives")

        def probe(path):
            status, headers, body = APIFinder._get(f"https://{domain}{path}")
            if status not in (200,201,400,401,403,405,422):
                return None
            if wildcard and status == wc_status:
                similarity = difflib.SequenceMatcher(None, body, wc_body).quick_ratio()
                if similarity >= SIMILARITY_THRESHOLD:
                    return None
            ct = headers.get("Content-Type","")
            is_api = any(t in ct for t in ["json","xml","api","graphql"])
            return (path,status,ct[:40],"✓ API" if is_api else "?")

        found=[]
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(probe, p): p for p in API_PATHS}
            for i, fut in enumerate(as_completed(futures), 1):
                bar(i,len(API_PATHS),"Probing")
                result = fut.result()
                if result: found.append(result)
        print()

        if found:
            found.sort(key=lambda x:x[0])
            sub(f"✅ Found {len(found)} API Endpoints")
            th(["Path","Status","Content-Type","Type"])
            for path,code,ct,typ in found:
                tr([path,str(code),ct,typ],"found" if code in (200,201) else "warn" if code in (401,403) else "")
        else: warn("No API endpoints found")

        sub("🔍 GraphQL Introspection Test")
        for gql_path in ["/graphql","/api/graphql","/query"]:
            try:
                data=json.dumps({"query":"{__schema{types{name}}}"}).encode()
                req_obj=urllib.request.Request(f"https://{domain}{gql_path}",data=data,
                    headers={"User-Agent":USER_AGENT,"Content-Type":"application/json"})
                with urllib.request.urlopen(req_obj,timeout=8) as r:
                    body=r.read().decode(errors='ignore')
                    if "__schema" in body or "types" in body:
                        ok(f"GraphQL introspection ENABLED at {gql_path}!")
                    elif r.status==200:
                        res(gql_path,"HTTP 200 (introspection may be disabled)","warning")
            except: pass
        ok(f"API Finder done — {len(found)} endpoints")
