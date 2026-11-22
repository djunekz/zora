import os
import re
import sys

CHANGELOG_PATH = "CHANGELOG.md"


def normalize(v):
    return v.strip().lstrip("vV")


def find_section(text, heading_pattern):
    match = re.search(heading_pattern, text, re.MULTILINE)
    if not match:
        return None
    start = match.end()
    next_heading = re.search(r"^## \[", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def main():
    tag = os.environ.get("RELEASE_TAG", "").strip()
    if not tag:
        print("::error::RELEASE_TAG environment variable is not set", file=sys.stderr)
        sys.exit(1)

    version = normalize(tag)

    if not os.path.isfile(CHANGELOG_PATH):
        print("::error::CHANGELOG.md not found", file=sys.stderr)
        sys.exit(1)

    with open(CHANGELOG_PATH, encoding="utf-8") as f:
        text = f.read()

    escaped = re.escape(version)
    versioned_pattern = rf"^## \[v?{escaped}\][^\n]*$"
    body = find_section(text, versioned_pattern)
    source = f"[{version}]"

    if body is None:
        body = find_section(text, r"^## \[Unreleased\][^\n]*$")
        source = "[Unreleased] (no section named for this tag was found yet)"

    if not body:
        body = (
            f"No changelog entry found for `{tag}`. "
            f"See the [full changelog](../../blob/main/CHANGELOG.md) for details."
        )
        source = "fallback"

    print(f"::notice::Changelog section used: {source}", file=sys.stderr)

    out_path = os.environ.get("RELEASE_NOTES_PATH", "RELEASE_NOTES.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(body + "\n")

    print(f"Wrote release notes to {out_path} ({len(body)} chars) from {source}")


if __name__ == "__main__":
    main()
