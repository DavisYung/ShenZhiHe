"""Shared helper for appending new sections to f6chem/data/2b.json.

Existing sections are never modified: the file is loaded, new sections are
appended to data['sections'], and it is written back as UTF-8 with indent=2.
"""
import json
import os
import sys

DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "2b.json"
)


def load():
    with open(DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def save(doc):
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, DATA)


def append(doc, new_sections):
    """Guard against duplicate ids, then append and persist."""
    existing = {s["id"] for s in doc["sections"]}
    fresh = []
    for s in new_sections:
        if s["id"] in existing:
            raise SystemExit("DUPLICATE SECTION ID: " + s["id"])
        fresh.append(s)
    n0 = len(doc["sections"])
    p0 = sum(len(s["points"]) for s in doc["sections"])
    doc["sections"].extend(fresh)
    save(doc)
    n1 = len(doc["sections"])
    p1 = sum(len(s["points"]) for s in doc["sections"])
    pages = sorted({pt["page"] for s in fresh for pt in s["points"]})
    # verify round-trip
    with open(DATA, "r", encoding="utf-8") as f:
        json.load(f)
    print(
        "[batch] +%d sections, +%d points | total %d->%d sections, %d->%d points "
        "| pages %s | json ok"
        % (
            n1 - n0,
            p1 - p0,
            n0,
            n1,
            p0,
            p1,
            ",".join(str(p) for p in pages),
        )
    )
    sys.stdout.flush()