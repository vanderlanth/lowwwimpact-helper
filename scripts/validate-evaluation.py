#!/usr/bin/env python3
"""Validate an evaluation JSON against the output contract.

The contract is references/valid-example.json. A structural mismatch is a failed run,
regardless of how good the findings are.

Usage:
    python3 scripts/validate-evaluation.py workspace/lowwwimpact-evaluation.json
    python3 scripts/validate-evaluation.py            # defaults to the path above

Exit code 0 = valid, 1 = contract violation, 2 = could not read input.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "references" / "valid-example.json"

META_KEYS = {
    "url", "urls", "date", "lighthouse", "criteria_version",
    "total_criteria", "evaluated", "skipped_subjective", "na",
}
CRITERION_KEYS = {"id", "type", "question", "answer", "note"}
PAGE_KEYS = {
    "url", "title", "performance", "accessibility",
    "best_practices", "seo", "initial_weight_kb", "deferred_weight_kb",
}
JOURNEY_PAGE_KEYS = {"url", "name", "kb"}

errors = []


def err(msg):
    errors.append(msg)


def check(doc):
    contract = json.loads(CONTRACT.read_text())

    # Top level
    expected = set(contract)
    actual = set(doc)
    if missing := expected - actual:
        err(f"missing top-level key(s): {sorted(missing)}")
    if extra := actual - expected:
        err(f"unexpected top-level key(s): {sorted(extra)}")

    # meta
    meta = doc.get("meta")
    if not isinstance(meta, dict):
        err("meta: must be an object")
    else:
        if missing := META_KEYS - set(meta):
            err(f"meta: missing {sorted(missing)}")
        if not isinstance(meta.get("urls"), list):
            err("meta.urls: must be an array")

    # evaluation — a real array
    ev = doc.get("evaluation")
    if not isinstance(ev, list):
        err("evaluation: must be an ARRAY")
    else:
        if len(ev) != 27:
            err(f"evaluation: expected 27 entries, found {len(ev)}")
        for i, e in enumerate(ev):
            if not isinstance(e, dict):
                err(f"evaluation[{i}]: must be an object")
                continue
            if missing := CRITERION_KEYS - set(e):
                err(f"evaluation[{i}] (id={e.get('id')!r}): missing {sorted(missing)}")

    # pages — an OBJECT keyed page-N, not an array
    pages = doc.get("pages")
    if isinstance(pages, list):
        err("pages: must be an OBJECT keyed 'page-1', 'page-2', … — found an array")
    elif not isinstance(pages, dict):
        err("pages: must be an object")
    else:
        for k, p in pages.items():
            if not re.fullmatch(r"page-\d+", k):
                err(f"pages: key {k!r} must match 'page-N'")
            if not isinstance(p, dict):
                err(f"pages[{k}]: must be an object")
                continue
            if missing := PAGE_KEYS - set(p):
                err(f"pages[{k}]: missing {sorted(missing)}")
            if extra := set(p) - PAGE_KEYS:
                err(f"pages[{k}]: unexpected field(s) {sorted(extra)} — exactly 8 keys allowed")

    # lighthouse_recap
    lr = doc.get("lighthouse_recap", ...)
    if lr is ...:
        err("lighthouse_recap: required top-level key is absent")
    elif lr is not None and not isinstance(lr, str):
        err("lighthouse_recap: must be a string (or null)")

    # recommendations
    rec = doc.get("recommendations")
    if not isinstance(rec, dict):
        err("recommendations: required, must be an object")
    else:
        if "executive_summary" not in rec:
            err("recommendations: missing executive_summary")
        top5 = rec.get("top_5")
        if not isinstance(top5, list):
            err("recommendations.top_5: must be an array")
        elif len(top5) > 5:
            err(f"recommendations.top_5: at most 5 entries, found {len(top5)}")

    # journeys — an OBJECT keyed journey-N; may be omitted entirely
    if "journeys" in doc:
        j = doc["journeys"]
        if isinstance(j, list):
            err("journeys: must be an OBJECT keyed 'journey-1', … — found an array")
        elif not isinstance(j, dict):
            err("journeys: must be an object")
        else:
            for k, entry in j.items():
                if not re.fullmatch(r"journey-\d+", k):
                    err(f"journeys: key {k!r} must match 'journey-N'")
                if not isinstance(entry, dict):
                    err(f"journeys[{k}]: must be an object")
                    continue
                if "description" not in entry:
                    err(f"journeys[{k}]: missing description")
                jp = entry.get("pages")
                if not isinstance(jp, list):
                    err(f"journeys[{k}].pages: must be an array")
                else:
                    for i, p in enumerate(jp):
                        if not isinstance(p, dict) or JOURNEY_PAGE_KEYS - set(p):
                            err(f"journeys[{k}].pages[{i}]: needs exactly {sorted(JOURNEY_PAGE_KEYS)}")


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("workspace/lowwwimpact-evaluation.json")
    if not target.exists():
        print(f"cannot read {target}", file=sys.stderr)
        return 2
    if not CONTRACT.exists():
        print(f"contract missing: {CONTRACT}", file=sys.stderr)
        return 2
    try:
        doc = json.loads(target.read_text())
    except json.JSONDecodeError as e:
        print(f"{target}: not valid JSON — {e}", file=sys.stderr)
        return 1

    check(doc)

    if errors:
        print(f"CONTRACT VIOLATION — {len(errors)} problem(s) in {target}:\n")
        for e in errors:
            print(f"  - {e}")
        print(f"\nContract: {CONTRACT.relative_to(ROOT)}")
        return 1

    print(f"OK — {target} matches the output contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
