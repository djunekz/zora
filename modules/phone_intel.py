import re
import urllib.request
import urllib.parse
import urllib.error

import phonenumbers
from phonenumbers import geocoder, carrier, timezone as pn_timezone, PhoneNumberFormat, PhoneNumberType, number_type

from zora.core import *


CURRENCY_BY_REGION = {
    "US":"USD","CA":"CAD","GB":"GBP","IE":"EUR","FR":"EUR","DE":"EUR","ES":"EUR","IT":"EUR",
    "NL":"EUR","BE":"EUR","PT":"EUR","AT":"EUR","CH":"CHF","GR":"EUR","PL":"PLN","SE":"SEK",
    "NO":"NOK","DK":"DKK","FI":"EUR","RU":"RUB","TR":"TRY","EG":"EGP","ZA":"ZAR","NG":"NGN",
    "KE":"KES","MA":"MAD","ID":"IDR","MY":"MYR","SG":"SGD","TH":"THB","VN":"VND","PH":"PHP",
    "JP":"JPY","KR":"KRW","CN":"CNY","IN":"INR","PK":"PKR","BD":"BDT","AU":"AUD","NZ":"NZD",
    "BR":"BRL","MX":"MXN","AR":"ARS","CL":"CLP","CO":"COP","PE":"PEN","VE":"VES","SA":"SAR",
    "AE":"AED","QA":"QAR","KW":"KWD","BH":"BHD","OM":"OMR","IL":"ILS","JO":"JOD","LB":"LBP",
    "IQ":"IQD","IR":"IRR","PK":"PKR","LK":"LKR","MM":"MMK","KH":"KHR","LA":"LAK","HK":"HKD",
    "TW":"TWD","MO":"MOP",
}

NUMBER_TYPE_LABELS = {
    PhoneNumberType.FIXED_LINE: "Fixed Line",
    PhoneNumberType.MOBILE: "Mobile",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
    PhoneNumberType.TOLL_FREE: "Toll-Free",
    PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    PhoneNumberType.SHARED_COST: "Shared Cost",
    PhoneNumberType.VOIP: "VoIP",
    PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
    PhoneNumberType.PAGER: "Pager",
    PhoneNumberType.UAN: "Universal Access Number",
    PhoneNumberType.VOICEMAIL: "Voicemail",
    PhoneNumberType.UNKNOWN: "Unknown",
}

DEFAULT_REGION = "ID"


class PhoneIntel:
    @staticmethod
    def _parse(raw):
        cleaned = re.sub(r'[\s\-\.\(\)\/]', '', raw)
        assumed_region = None
        if cleaned.startswith('00'):
            cleaned = '+' + cleaned[2:]
        if cleaned.startswith('+'):
            pn = phonenumbers.parse(cleaned, None)
        else:
            assumed_region = DEFAULT_REGION
            pn = phonenumbers.parse(cleaned, assumed_region)
        return pn, assumed_region

    @staticmethod
    def _check_carrier_api(num):
        results = {}
        nv = req_json(f"http://apilayer.net/api/validate?number={num}")
        if nv and nv.get("carrier"):
            results["carrier"]   = nv.get("carrier","?")
            results["line_type"] = nv.get("line_type","?")
            results["valid"]     = nv.get("valid", False)
            results["local_fmt"] = nv.get("local_format","?")
            results["intl_fmt"]  = nv.get("international_format","?")
            results["location"]  = nv.get("location","?")

        ab = req_json(f"https://phonevalidation.abstractapi.com/v1/?api_key=demo&phone={num}")
        if ab and ab.get("carrier"):
            results.setdefault("carrier",   ab.get("carrier",{}).get("name","?"))
            results.setdefault("line_type", ab.get("type","?"))
            results.setdefault("location",  ab.get("location","?"))

        return results

    @staticmethod
    def run(phone):
        sec("PHONE NUMBER INTELLIGENCE — ULTRA DEEP", "📱")

        try:
            pn, assumed_region = PhoneIntel._parse(phone)
        except phonenumbers.NumberParseException as e:
            err(f"Invalid phone number format — {e}")
            return

        if assumed_region:
            warn(f"No '+' or country code given — assuming region {assumed_region} (Indonesia). "
                 f"If this number is from another country, re-enter it with its country code, e.g. +44...")

        valid    = phonenumbers.is_valid_number(pn)
        possible = phonenumbers.is_possible_number(pn)
        region   = phonenumbers.region_code_for_number(pn) or "?"
        cc       = str(pn.country_code)
        national_digits = phonenumbers.national_significant_number(pn)
        e164         = phonenumbers.format_number(pn, PhoneNumberFormat.E164)
        intl_fmt     = phonenumbers.format_number(pn, PhoneNumberFormat.INTERNATIONAL)
        national_fmt = phonenumbers.format_number(pn, PhoneNumberFormat.NATIONAL)
        rfc3966_fmt  = phonenumbers.format_number(pn, PhoneNumberFormat.RFC3966)
        num = e164.lstrip('+')
        clean = e164

        sub("📋 Number Identity")
        res("E.164 Format",      e164,                                "info")
        res("International",    intl_fmt,                             "info")
        res("National Format",  national_fmt,                         "info")
        res("Country Code",     f"+{cc}",                              "info")
        res("National Number",  national_digits,                      "info")
        res("Digit Count",      f"{len(national_digits)} (country code not included)", "info")

        sub("🌍 Country Intelligence")
        country_name = geocoder.country_name_for_number(pn, "en") or "Unknown"
        currency = CURRENCY_BY_REGION.get(region, "?")
        tz_list = pn_timezone.time_zones_for_number(pn)
        res("Country",    country_name, "info")
        res("ISO Code",   region,       "info")
        res("Timezone",   ", ".join(tz_list) if tz_list else "?", "info")
        res("Currency",   currency,     "info")

        if len(region) == 2:
            flag = "".join(chr(0x1F1E6 + ord(c) - ord('A')) for c in region.upper())
            res("Flag", flag, "info")

        if valid:
            ok("Number is VALID for its country's numbering plan")
        elif possible:
            warn("Number has a plausible length but does not match a real allocated format for its country")
        else:
            res("Validity", "NOT a possible number for the detected region", "error")

        sub("📶 Line Type Analysis")
        ntype = number_type(pn)
        type_label = NUMBER_TYPE_LABELS.get(ntype, "Unknown")
        res("Line Type", type_label, "success" if ntype == PhoneNumberType.MOBILE else "info")

        carrier_name = carrier.name_for_number(pn, "en")
        if carrier_name:
            res("Operator", carrier_name, "success")
        else:
            res("Operator", "Unavailable offline for this country/number range", "warning")

        area_desc = geocoder.description_for_number(pn, "en")
        if area_desc and area_desc != country_name:
            res("Area", area_desc, "info")

        sub("🔗 Live Carrier Lookup")
        dots("Querying carrier APIs")

        carrier_data = {}
        try:
            nv = req_json(f"https://api.veriphone.io/v2/verify?phone={urllib.parse.quote(clean)}")
            if nv and nv.get("carrier"):
                carrier_data = nv
                res("Carrier",          nv.get("carrier","?"),           "success")
                res("Line Type",        nv.get("phone_type","?"),        "info")
                res("Valid",            str(nv.get("phone_valid",False)), "success" if nv.get("phone_valid") else "warning")
                res("Local Format",     nv.get("phone_local","?"),       "info")
                res("Intl Format",      nv.get("phone_national","?"),    "info")
                res("Country",          nv.get("country","?"),           "info")
                res("Country Code",     nv.get("country_code","?"),      "info")
        except Exception:
            pass

        if not carrier_data:
            warn("Live carrier lookup unavailable (no API key configured)")

        sub("🌐 Online Presence & Social Links")

        wa_url = f"https://wa.me/{num}"
        res("WhatsApp", wa_url, "info")

        tg_url = f"https://t.me/+{num}"
        res("Telegram", tg_url, "info")

        try:
            h, code = req_headers(wa_url)
            if code == 200:
                ok("WhatsApp: Number appears to be registered")
            else:
                res("WhatsApp Status", f"HTTP {code} — could not verify", "warning")
        except Exception:
            res("WhatsApp Status", "Could not verify", "warning")

        sub("🔍 Reverse Phone Lookup Sites")
        q = urllib.parse.quote_plus(clean)
        lookup_sites = [
            ("TrueCaller",        f"https://www.truecaller.com/search/global/{num}"),
            ("WhoCalledMe",       f"https://whocalledme.com/PhoneNumber/{num}"),
            ("SpyDialer",         f"https://www.spydialer.com/default.aspx?q={num}"),
            ("CallerIDTest",      "https://www.calleridtest.com/"),
            ("Sync.me",           f"https://sync.me/search/?number={clean}"),
            ("PhoneInfoga",       "https://phoneinfoga.crvx.fr/#/"),
            ("Spokeo",            f"https://www.spokeo.com/reverse-phone-lookup/{num}"),
            ("Whitepages",        f"https://www.whitepages.com/phone/{num}"),
            ("800notes",          f"https://800notes.com/Phone.aspx/{num}"),
            ("CallerSmart",       f"https://www.callersmart.com/search/{num}"),
            ("AnyWho",            f"https://www.anywho.com/reverse-phone/{num}"),
            ("Google Search",     f"https://www.google.com/search?q=%22{q}%22"),
            ("Bing Search",       f"https://www.bing.com/search?q={q}"),
            ("DuckDuckGo",        f"https://duckduckgo.com/?q={q}"),
        ]
        th(["Source", "URL"])
        for name_, url in lookup_sites:
            tr([name_, url[:75]], "found")

        sub("📝 All Format Variants")
        fmts = [e164, intl_fmt, national_fmt, rfc3966_fmt, f"00{num}"]
        if region == "ID":
            fmts.append(f"0{national_digits}")
        fmts = list(dict.fromkeys(f.strip() for f in fmts if f))
        for i, fmt in enumerate(fmts):
            tag = f"{C.BCYAN}[{i+1:02d}]{C.R}"
            print(f"    {tag} {C.BWHITE}{fmt}{C.R}")

        sub("🔎 OSINT Search Dorks")
        dorks = [
            ("Exact number",          f'"{e164}"'),
            ("National format",       f'"{national_fmt}"'),
            ("LinkedIn",              f'site:linkedin.com "{e164}"'),
            ("Facebook",              f'site:facebook.com "{e164}"'),
            ("Instagram",             f'site:instagram.com "{e164}"'),
            ("Twitter",               f'site:twitter.com "{e164}"'),
            ("GitHub",                f'site:github.com "{e164}"'),
            ("Paste sites",           f'site:pastebin.com OR site:ghostbin.com "{e164}"'),
            ("Gov / Edu leaks",       f'site:gov OR site:edu "{e164}"'),
            ("Contract / Invoice",    f'"{e164}" filetype:pdf'),
            ("CSV leaks",             f'"{e164}" filetype:csv'),
            ("All formats",          f'"{e164}" OR "{num}" OR "{national_fmt}"'),
        ]
        for label, dork in dorks:
            encoded = urllib.parse.quote_plus(dork)
            gurl = f"https://www.google.com/search?q={encoded}"
            print(f"    {C.BRED}•{C.R} {C.BOLD}{label:<24}{C.R} {C.DIM}{gurl[:75]}{C.R}")

        sub("🚨 Risk & Anomaly Assessment")

        risk_score = 0
        risk_notes = []

        if not possible:
            risk_score += 3
            risk_notes.append("Not even a possible number length for its country")
        elif not valid:
            risk_score += 2
            risk_notes.append("Fails country-specific validation (not an allocated/dialable range)")

        if re.search(r'(\d)\1{4,}', national_digits):
            risk_score += 1
            risk_notes.append("Contains 5+ repeating digits (unusual)")

        digits = [int(d) for d in national_digits[:8]]
        if len(digits) >= 2 and all(digits[i]+1 == digits[i+1] for i in range(len(digits)-1)):
            risk_score += 1
            risk_notes.append("Sequential digits (could be fake/test number)")

        if national_digits.count('0') == len(national_digits):
            risk_score += 3
            risk_notes.append("All-zero local number (invalid)")

        risk_label = "LOW" if risk_score == 0 else "MEDIUM" if risk_score <= 2 else "HIGH"
        risk_color = C.BGREEN if risk_score == 0 else C.BYELLOW if risk_score <= 2 else C.BRED
        print(f"    {C.BOLD}Risk Level: {risk_color}{risk_label}{C.R} (score: {risk_score})")
        if risk_notes:
            for note in risk_notes:
                print(f"    {C.BYELLOW}⚠{C.R}  {note}")
        else:
            ok("No anomalies detected — number appears legitimate")

        sub("🔢 Neighbor Numbers (±3)")
        try:
            local_int = int(national_digits)
            neighbors = []
            for delta in [-3, -2, -1, 1, 2, 3]:
                neighbor_local = str(local_int + delta).zfill(len(national_digits))
                neighbor_full  = f"+{cc}{neighbor_local}"
                neighbors.append(neighbor_full)
            print(f"    {C.GRAY}" + "  ".join(neighbors) + f"{C.R}")
            print(f"    {C.DIM}(Useful for pattern analysis in leaked datasets){C.R}")
        except Exception:
            pass

        sub("📊 Intelligence Summary")
        print(f"""
    {C.BOLD}┌─ PHONE INTEL REPORT ─────────────────────────────────────┐{C.R}
    {C.BOLD}│{C.R}  Number   : {C.BWHITE}{e164}{C.R}
    {C.BOLD}│{C.R}  Country  : {C.BCYAN}{country_name} (+{cc}){C.R}
    {C.BOLD}│{C.R}  Timezone : {C.BCYAN}{", ".join(tz_list) if tz_list else "?"}{C.R}
    {C.BOLD}│{C.R}  Currency : {C.BCYAN}{currency}{C.R}
    {C.BOLD}│{C.R}  Type     : {C.BCYAN}{type_label}{C.R}
    {C.BOLD}│{C.R}  Valid    : {C.BCYAN}{valid}{C.R}
    {C.BOLD}│{C.R}  Risk     : {risk_color}{risk_label}{C.R}
    {C.BOLD}└──────────────────────────────────────────────────────────┘{C.R}""")

        ok(f"Phone Intelligence done — {len(fmts)} formats, {len(lookup_sites)} lookup sources, {len(dorks)} dorks")
