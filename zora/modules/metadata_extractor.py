import re

from zora.core import dots, err, ok, req_text, res, sec, sub, warn


class MetadataExtractor:
    @staticmethod
    def run(url):
        sec("URL METADATA EXTRACTOR", "📄")
        if not (url.startswith("https://") or url.startswith("http://")):
            url="https://"+url
        dots("Fetching page metadata")
        html_src=req_text(url)
        if not html_src:
            err("Could not fetch URL"); return

        sub("📋 Open Graph / Social Meta")
        meta_tags = re.findall(r'<meta\b[^>]*>', html_src, re.I)
        og_tags, tw_tags = [], []
        for tag in meta_tags:
            prop_m = re.search(r'(?:property|name)=["\']((?:og|twitter):[^"\']+)["\']', tag, re.I)
            cont_m = re.search(r'content=["\']([^"\']*)["\']', tag, re.I)
            if prop_m and cont_m:
                key = prop_m.group(1)
                val = cont_m.group(1)
                if key.lower().startswith("og:"):
                    og_tags.append((key[3:], val))
                else:
                    tw_tags.append((key[8:], val))
        for k,v in og_tags[:10]: res(f"og:{k}", v[:80],"info")
        for k,v in tw_tags[:5]:  res(f"twitter:{k}", v[:80],"info")

        sub("📊 Page Stats")
        res("Total Size",  f"{len(html_src):,} chars","info")
        res("Images",      str(len(re.findall(r'<img',html_src,re.I))),"info")
        res("Links",       str(len(re.findall(r'<a ',html_src,re.I))),"info")
        res("Forms",       str(len(re.findall(r'<form',html_src,re.I))),"info")

        comments=re.findall(r'<!--(.*?)-->',html_src,re.S)
        juicy=[c.strip() for c in comments if any(w in c.lower() for w in ["todo","fixme","password","secret","key","api","token"])]
        if juicy:
            sub("⚠️  Interesting HTML Comments")
            for c in juicy[:5]: warn(c[:100].strip())

        ok("Metadata Extraction done")
