import re
import os
import json
from datetime import datetime

from zora.core import C, err, get_session_log, ok, sec, warn


class ReportExporter:
    @staticmethod
    def quick_save(target, data_dict=None):
        session = get_session_log()

        sec("REPORT EXPORTER", "💾")
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        safe=re.sub(r'[^\w\-]','_',target)
        fname=f"zora_report_{safe}_{ts}.json"

        if not session and not data_dict:
            warn("No scan results recorded yet this session — run some modules before exporting, "
                 "or this report will be empty.")

        report={
            "tool":"ZORA v2.0.0",
            "target":target,
            "timestamp":datetime.now().isoformat(),
            "session_entries": len(session),
            "session_log": session,
            "data":data_dict or {},
        }
        try:
            with open(fname,"w") as f: json.dump(report,f,indent=2,default=str)
            ok(f"Report saved: {fname} ({len(session)} logged entries from this session)")
            print(f"    {C.GRAY}Location: {os.path.abspath(fname)}{C.R}")
        except Exception as e: err(f"Save failed: {e}")
