import difflib
import urllib.request
import urllib.parse
import urllib.error

from concurrent.futures import ThreadPoolExecutor, as_completed

from zora.core import C, USER_AGENT, bar, err, inf, is_user, ok, req_json, res, sec, sub, th, tr

MAX_WORKERS = 25
PROBE_USERNAME = "zzq9xf3knotarealuser00112233"
BODY_SAMPLE_BYTES = 12000
SIMILARITY_THRESHOLD = 0.92


PLATFORMS = {
    "GitHub":"https://github.com/{}",
    "GitLab":"https://gitlab.com/{}",
    "Twitter/X":"https://twitter.com/{}",
    "Instagram":"https://instagram.com/{}",
    "Facebook":"https://facebook.com/{}",
    "LinkedIn":"https://linkedin.com/in/{}",
    "Reddit":"https://reddit.com/user/{}",
    "TikTok":"https://tiktok.com/@{}",
    "YouTube":"https://youtube.com/@{}",
    "Twitch":"https://twitch.tv/{}",
    "Pinterest":"https://pinterest.com/{}",
    "Tumblr":"https://{}.tumblr.com",
    "Stack Overflow":"https://stackoverflow.com/users/{}",
    "HackerNews":"https://news.ycombinator.com/user?id={}",
    "Dev.to":"https://dev.to/{}",
    "Medium":"https://medium.com/@{}",
    "CodePen":"https://codepen.io/{}",
    "Dribbble":"https://dribbble.com/{}",
    "Behance":"https://behance.net/{}",
    "Telegram":"https://t.me/{}",
    "Spotify":"https://open.spotify.com/user/{}",
    "SoundCloud":"https://soundcloud.com/{}",
    "Steam":"https://steamcommunity.com/id/{}",
    "Xbox":"https://xboxgamertag.com/search/{}",
    "PlayStation":"https://psnprofiles.com/{}",
    "AngelList":"https://angel.co/{}",
    "ProductHunt":"https://producthunt.com/@{}",
    "Patreon":"https://patreon.com/{}",
    "Ko-fi":"https://ko-fi.com/{}",
    "About.me":"https://about.me/{}",
    "Linktree":"https://linktr.ee/{}",
    "Keybase":"https://keybase.io/{}",
    "Mastodon":"https://mastodon.social/@{}",
    "HackerOne":"https://hackerone.com/{}",
    "Bugcrowd":"https://bugcrowd.com/{}",
    "Quora":"https://quora.com/profile/{}",
    "SlideShare":"https://slideshare.net/{}",
    "Vimeo":"https://vimeo.com/{}",
    "Flickr":"https://flickr.com/people/{}",
    "Imgur":"https://imgur.com/user/{}",
    "DockerHub":"https://hub.docker.com/u/{}",
    "NPM":"https://npmjs.com/~{}",
    "PyPI":"https://pypi.org/user/{}",
    "Replit":"https://replit.com/@{}",
    "Hashnode":"https://hashnode.com/@{}",
    "Substack":"https://{}.substack.com",
    "GitBook":"https://{}.gitbook.io",
    "Notion":"https://notion.so/@{}",
    "Trello":"https://trello.com/{}",
    "Gravatar":"https://gravatar.com/{}",
    "Last.fm":"https://last.fm/user/{}",
    "Goodreads":"https://goodreads.com/{}",
}

class UsernameOSINT:
    @staticmethod
    def _fetch(url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=6) as resp:
                body = resp.read(BODY_SAMPLE_BYTES).decode(errors="ignore")
                return resp.status, body
        except urllib.error.HTTPError as e:
            try:
                body = e.read(BODY_SAMPLE_BYTES).decode(errors="ignore")
            except Exception:
                body = ""
            return e.code, body
        except Exception:
            return None, ""

    @staticmethod
    def _build_baselines(items):
        baselines = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {
                pool.submit(UsernameOSINT._fetch, tpl.format(PROBE_USERNAME)): name
                for name, tpl in items
            }
            for fut in as_completed(futures):
                baselines[futures[fut]] = fut.result()
        return baselines

    @staticmethod
    def _check_platform(name, url_tpl, username, baseline):
        url = url_tpl.format(username)
        status, body = UsernameOSINT._fetch(url)
        base_status, base_body = baseline

        if status is None:
            return None
        if status in (404, 410):
            return None
        if status == 403:
            return None
        if base_status is None:
            return (name, url)
        if status != base_status:
            return (name, url)

        similarity = difflib.SequenceMatcher(None, body, base_body).quick_ratio()
        if similarity >= SIMILARITY_THRESHOLD:
            return None
        return (name, url)

    @staticmethod
    def run(username):
        sec("USERNAME OSINT (50+ PLATFORMS)", "👤")
        if not is_user(username):
            err("Invalid username format"); return

        inf("Target", username, 2)
        inf("Platforms", f"Checking {len(PLATFORMS)}", 2)

        items = list(PLATFORMS.items())

        sub("🧪 Calibrating per-platform baselines")
        inf("Method", "probing a known-nonexistent username per platform", 2)
        baselines = UsernameOSINT._build_baselines(items)

        sub("🌐 Platform Search")
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {
                pool.submit(
                    UsernameOSINT._check_platform, n, t, username, baselines.get(n, (None, ""))
                ): n
                for n, t in items
            }
            for i, fut in enumerate(as_completed(futures), 1):
                bar(i,len(items),"Scanning")
                r = fut.result()
                if r:
                    results.append(r)
                    print(f"\r  {C.BGREEN}✓{C.R} {r[0]:<22} {C.GRAY}{r[1][:55]}{C.R}")
        print()

        sub("🔬 GitHub Deep Analysis")
        gh=req_json(f"https://api.github.com/users/{username}")
        if gh and "login" in gh:
            for k,v in [("Login",gh.get("login")),("Name",gh.get("name")),
                        ("Bio",str(gh.get("bio",""))[:60]),("Company",gh.get("company")),
                        ("Location",gh.get("location")),("Blog",gh.get("blog")),
                        ("Email",gh.get("email")),("Twitter",gh.get("twitter_username")),
                        ("Public Repos",gh.get("public_repos")),("Gists",gh.get("public_gists")),
                        ("Followers",gh.get("followers")),("Following",gh.get("following")),
                        ("Created",str(gh.get("created_at",""))[:10]),
                        ("Updated",str(gh.get("updated_at",""))[:10]),
                        ("Hireable",gh.get("hireable"))]:
                if v is not None: res(k,str(v),"info")

            repos=req_json(f"https://api.github.com/users/{username}/repos?per_page=5&sort=stars")
            if repos and isinstance(repos,list):
                sub("⭐ Top GitHub Repositories")
                th(["Repo","Stars","Language","Updated"])
                for r in repos[:5]:
                    tr([r.get("name",""),str(r.get("stargazers_count",0)),
                        r.get("language") or "?",str(r.get("updated_at",""))[:10]],"found")

            events=req_json(f"https://api.github.com/users/{username}/events/public?per_page=5")
            if events and isinstance(events,list):
                sub("📅 Recent GitHub Activity")
                for ev in events[:5]:
                    etype=ev.get("type","")
                    repo =ev.get("repo",{}).get("name","")
                    date =str(ev.get("created_at",""))[:10]
                    print(f"    {C.BCYAN}•{C.R} {C.BWHITE}{etype:<30}{C.R} {C.GRAY}{repo:<35}{C.R} {date}")

        npm=req_json(f"https://registry.npmjs.org/-/v1/search?text=author:{username}&size=5")
        if npm and npm.get("objects"):
            sub("📦 NPM Packages")
            for obj in npm["objects"][:5]:
                pkg=obj.get("package",{})
                res(pkg.get("name","?"),pkg.get("description","")[:50],"info")

        sub("📊 Summary")
        inf("Profiles Found", str(len(results)), 4)
        inf("Rate", f"{len(results)/len(PLATFORMS)*100:.1f}%", 4)
        ok(f"Username OSINT done — {len(results)}/{len(PLATFORMS)} found")
