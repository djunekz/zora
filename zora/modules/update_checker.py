from zora.core import C, VERSION, dots, inf, ok, req_json, res, sec, sub, warn

GITHUB_REPO = "djunekz/zora"


def _parse_version(v):
    v = v.strip().lstrip("vV")
    parts = []
    for p in v.split("."):
        digits = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


class UpdateChecker:
    @staticmethod
    def run():
        sec("CHECK FOR UPDATES", "🔄")
        inf("Current version", VERSION, 2)
        inf("Repository", f"github.com/{GITHUB_REPO}", 2)

        dots("Checking GitHub for the latest release")
        data = req_json(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=8)

        if not data or "tag_name" not in data:
            warn("Could not reach GitHub, or no release has been published yet.")
            res("Manual check", f"https://github.com/{GITHUB_REPO}/releases", "info")
            return

        remote_tag = data.get("tag_name", "")
        remote_ver = _parse_version(remote_tag)
        local_ver = _parse_version(VERSION)

        sub("📦 Release Info")
        res("Latest tag", remote_tag, "info")
        if data.get("published_at"):
            res("Published", data["published_at"][:10], "info")
        if data.get("html_url"):
            res("URL", data["html_url"], "info")

        if remote_ver > local_ver:
            warn(f"A newer version is available: {remote_tag} (you have v{VERSION})")
            body = (data.get("body") or "").strip()
            if body:
                sub("📝 Release Notes")
                for line in body.splitlines()[:15]:
                    if line.strip():
                        print(f"    {C.GRAY}{line.strip()}{C.R}")
            res("Update", f"git pull && ./install.sh   (or download: {data.get('html_url','')})", "info")
        elif remote_ver < local_ver:
            ok(f"You are running v{VERSION}, ahead of the latest published release ({remote_tag}).")
        else:
            ok(f"You are up to date (v{VERSION}).")
