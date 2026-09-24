#!/usr/bin/env python3
"""Reproduction entry point.

The default verification path is deterministic and does not rerun timed
performance measurements. ``--rerun-campaign`` deletes and rebuilds all raw
campaign results with the documented one-worker resource caps; timings will
naturally vary across machines.
"""
from __future__ import annotations
import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT / "src")


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, env=ENV, check=True)


def compare_generated_cases() -> dict[str, object]:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "cases"
        code = (
            "from pathlib import Path; "
            "from fixedscan.generate import write_collections; "
            f"write_collections(Path({str(target)!r}))"
        )
        subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=ENV, check=True)
        mismatches: list[str] = []
        for expected in sorted((ROOT / "cases").rglob("*.json")):
            relative = expected.relative_to(ROOT / "cases")
            regenerated = target / relative
            if not regenerated.exists() or not filecmp.cmp(expected, regenerated, shallow=False):
                mismatches.append(str(relative))
        extra = [str(p.relative_to(target)) for p in target.rglob("*.json")
                 if not (ROOT / "cases" / p.relative_to(target)).exists()]
        return {"matched": not mismatches and not extra, "mismatches": mismatches, "extra": extra}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerun-campaign", action="store_true")
    args = parser.parse_args()
    if args.rerun_campaign:
        for name in ("raw", "certificates"):
            shutil.rmtree(ROOT / "results" / name, ignore_errors=True)
        run("scripts/run_campaign.py", "--split", "all")
    run("scripts/analyze_results.py")
    run("scripts/audit_references.py")
    cases = compare_generated_cases()
    if not cases["matched"]:
        print(json.dumps({"status": "FAIL", "case_regeneration": cases}, indent=2))
        return 1
    run("tests/run_all.py")
    report = {
        "status": "PASS",
        "case_regeneration": cases,
        "campaign_mode": "rerun" if args.rerun_campaign else "recorded-results-rechecked",
        "commands": [
            "python scripts/analyze_results.py",
            "python scripts/audit_references.py",
            "python tests/run_all.py",
        ],
    }
    path = ROOT / "results" / "reproduction.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
