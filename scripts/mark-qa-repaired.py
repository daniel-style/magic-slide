#!/usr/bin/env python3
"""
mark-qa-repaired.py - mark saved QA revision notes as repaired and awaiting
user confirmation.

Usage:
    python3 scripts/mark-qa-repaired.py deck/sources/qa/visual-issues.json
    python3 scripts/mark-qa-repaired.py deck/sources/qa/visual-issues.json --slides 2,5 --changed-files deck/sources/slide-02.html deck/sources/style.css
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

PENDING_STATUS = "fixed_pending_confirmation"
PENDING_ALIASES = {
    PENDING_STATUS,
    "awaiting_confirmation",
    "pending_confirmation",
    "repaired_pending_confirmation",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_slides(value: str) -> Set[int]:
    slides = set()
    if not value:
        return slides
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            slide = int(part)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid slide number: {part}") from exc
        if slide < 1:
            raise argparse.ArgumentTypeError(f"slide numbers must be positive: {part}")
        slides.add(slide)
    return slides


def load_issues(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("issues"), list):
        raise ValueError("visual-issues.json must contain an issues array")
    if not isinstance(data.get("schemaVersion"), int):
        data["schemaVersion"] = 1
    if not isinstance(data.get("qaRevision"), int):
        data["qaRevision"] = 0
    return data


def should_mark(issue: dict, slide_filter: Set[int]) -> bool:
    if not isinstance(issue, dict) or issue.get("resolved") is True:
        return False
    try:
        slide = int(issue.get("slide"))
    except (TypeError, ValueError):
        slide = 0
    if slide_filter and slide not in slide_filter:
        return False
    status = str(issue.get("status") or "").strip()
    return status not in PENDING_ALIASES


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="Path to sources/qa/visual-issues.json")
    parser.add_argument("--slides", type=parse_slides, default=set(), help="Comma-separated slide numbers to mark")
    parser.add_argument("--summary", default="Repaired by agent; awaiting user confirmation")
    parser.add_argument("--changed-files", nargs="*", default=[])
    args = parser.parse_args()

    path = args.path
    data = load_issues(path)
    timestamp = now_iso()
    data["qaRevision"] += 1
    revision = data["qaRevision"]
    data["updatedAt"] = timestamp
    changed_files = sorted({str(file) for file in args.changed_files if str(file)})

    marked = 0
    for issue in data["issues"]:
        if not should_mark(issue, args.slides):
            continue
        issue["resolved"] = False
        issue["status"] = PENDING_STATUS
        issue["updatedAt"] = timestamp
        issue["repairedAt"] = timestamp
        issue["repairedInRevision"] = revision
        issue["repairSummary"] = args.summary
        issue["confirmationRequestedAt"] = timestamp
        issue["confirmedAt"] = None
        issue["resolvedAt"] = None
        issue["resolvedInRevision"] = None
        issue["resolution"] = None
        if changed_files:
            existing = issue.get("changedFiles") if isinstance(issue.get("changedFiles"), list) else []
            merged_changed_files = {str(file) for file in existing if str(file)}
            merged_changed_files.update(changed_files)
            issue["changedFiles"] = sorted(merged_changed_files)
        marked += 1

    if marked == 0:
        print("No open QA issues matched.", file=sys.stderr)
        return 1

    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    print(f"Marked {marked} QA issue(s) as fixed_pending_confirmation in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
