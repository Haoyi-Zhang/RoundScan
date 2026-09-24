#!/usr/bin/env python3
"""Recollect task JSON files, rebuild CSV summaries, and audit campaign totals."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from run_campaign import collect_split

EXPECTED = {
    "frozen": {"rows": 360, "instances": 72},
    "stress": {"rows": 80, "instances": 16},
}


def main() -> int:
    report: dict[str, object] = {"status": "PASS", "splits": {}}
    for split, expected in EXPECTED.items():
        rows = collect_split(split)
        instances = len({row["case"] for row in rows})
        ok = len(rows) == expected["rows"] and instances == expected["instances"]
        report["splits"][split] = {
            "rows": len(rows),
            "instances": instances,
            "expected_rows": expected["rows"],
            "expected_instances": expected["instances"],
            "ok": ok,
        }
        if not ok:
            report["status"] = "FAIL"
    out = ROOT / "results" / "analysis-audit.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
