"""Summarise validity/<run>/*.json with scored_summary.csv into validity_summary.csv."""
import csv, glob, json, collections, pathlib

ROOT = pathlib.Path(__file__).parent
tot = collections.defaultdict(collections.Counter)
for f in glob.glob(str(ROOT / "validity" / "*" / "*.json")):
    run = pathlib.Path(f).parent.name
    for l in json.load(open(f, encoding="utf-8"))["labels"]:
        tot[run][l["label"]] += 1
rows = []
for r in csv.DictReader(open(ROOT / "scored_summary.csv")):
    c, n, lh = tot[r["run"]], int(r["findings"]), int(r["lenient_hits"])
    rows.append([r["run"], n, lh, sum(c.values()), c["VALID"], c["DEBATABLE"], c["INVALID"], round((lh + c["VALID"]) / n, 3) if n else 0])
with open(ROOT / "validity_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["run", "findings", "matched_any_tool_row", "unmatched", "valid", "debatable", "invalid", "adjusted_precision_valid"])
    w.writerows(rows)
print(*rows, sep="\n")
