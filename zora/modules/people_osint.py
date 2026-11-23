import urllib.request
import urllib.parse
import urllib.error

from zora.core import C, ok, sec, sub, th, tr, warn


class PeopleOSINT:
    @staticmethod
    def run(name):
        sec("PEOPLE & IDENTITY OSINT", "👤")
        q = urllib.parse.quote(name); qp = urllib.parse.quote_plus(name)

        sub("🔍 People Search Engines")
        th(["Source","URL"])
        for nm,url in [
            ("Spokeo",          f"https://www.spokeo.com/search?q={qp}"),
            ("Whitepages",      f"https://www.whitepages.com/name/{q.replace('%20','-')}"),
            ("FastPeopleSearch",f"https://www.fastpeoplesearch.com/name/{q.replace('%20','-')}"),
            ("TruePeopleSearch",f"https://www.truepeoplesearch.com/results?name={qp}"),
            ("BeenVerified",    f"https://www.beenverified.com/people/{qp}"),
            ("Intelius",        f"https://www.intelius.com/search/?firstName={q}"),
            ("That'sThem",      f"https://thatsthem.com/name/{q.replace('%20','-')}"),
        ]: tr([nm, url[:70]], "found")

        sub("📸 Reverse Face / Image Search")
        for nm,url in [
            ("PimEyes",       "https://pimeyes.com/en"),
            ("FaceCheck.ID",  "https://facecheck.id/"),
            ("TinEye",        "https://tineye.com/"),
            ("Yandex Images", f"https://yandex.com/images/search?text={qp}"),
            ("Google Images", f"https://www.google.com/search?q={qp}&tbm=isch"),
            ("Bing Visual",   f"https://www.bing.com/images/search?q={qp}"),
        ]: print(f"    {C.BMAGENTA}•{C.R} {C.BOLD}{nm:<18}{C.R} {C.GRAY}{url[:70]}{C.R}")

        sub("🕵️  Deep OSINT Links")
        for nm,url in [
            ("IntelX",      f"https://intelx.io/?s={qp}"),
            ("Webmii",      f"https://webmii.com/people?n={qp}"),
            ("Pipl",        f"https://pipl.com/search/?q={qp}"),
            ("Hunter.io",   "https://hunter.io/"),
            ("Clearbit",    "https://clearbit.com/"),
        ]: print(f"    {C.BYELLOW}•{C.R} {C.BOLD}{nm:<18}{C.R} {C.GRAY}{url[:70]}{C.R}")

        sub("📧 Email Permutation Generator")
        parts = name.lower().split()
        if len(parts)>=2:
            fn,ln=parts[0],parts[-1]
            for p in [f"{fn}.{ln}@[domain]",f"{fn}{ln}@[domain]",f"{fn[0]}{ln}@[domain]",
                      f"{fn}.{ln[0]}@[domain]",f"{ln}.{fn}@[domain]",f"{fn}_{ln}@[domain]",
                      f"{fn[0]}.{ln}@[domain]",f"{ln}{fn[0]}@[domain]"]:
                print(f"    {C.GRAY}•{C.R} {C.BWHITE}{p}{C.R}")
        else:
            warn("Need both first and last name (separated by a space) to generate email permutations")
        ok("People OSINT done")
