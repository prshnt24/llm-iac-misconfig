"""Aggregate remediation rubric scores per run and report inter-judge agreement."""
import csv, json, pathlib, collections

ROOT = pathlib.Path(__file__).parent
S = ROOT / "remediation_scores"
judges = sorted(p.name for p in S.iterdir())
scores = {j: {} for j in judges}  # judge -> (run, file, finding) -> score
for j in judges:
    for f in (S / j).glob("*/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        for s in d["scores"]:
            item = d["items"][s["item"]]
            scores[j][(f.parent.name, f.name, item["finding"])] = int(s["score"])

keys = sorted(set.intersection(*[set(v) for v in scores.values()]))
a, b = (scores[j] for j in judges[:2])
n = len(keys)
exact = sum(a[k] == b[k] for k in keys) / n
within1 = sum(abs(a[k] - b[k]) <= 1 for k in keys) / n
# quadratic-weighted Cohen's kappa
cats = [0, 1, 2]
obs = collections.Counter((a[k], b[k]) for k in keys)
ma, mb = collections.Counter(a[k] for k in keys), collections.Counter(b[k] for k in keys)
w = lambda i, j: (i - j) ** 2 / 4
num = sum(w(i, j) * obs[(i, j)] / n for i in cats for j in cats)
den = sum(w(i, j) * (ma[i] / n) * (mb[j] / n) for i in cats for j in cats)
kappa = 1 - num / den if den else 1.0

rows = []
for run in sorted({k[0] for k in keys}):
    ks = [k for k in keys if k[0] == run]
    row = [run, len(ks)]
    for j in judges:
        v = [scores[j][k] for k in ks]
        row += [round(sum(v) / len(v), 2), round(sum(x == 2 for x in v) / len(v), 3)]
    avg = [sum(scores[j][k] for j in judges) / len(judges) for k in ks]
    row.append(round(sum(avg) / len(avg), 2))
    rows.append(row)
hdr = ["run", "scored_findings"] + [f"{j}_{m}" for j in judges for m in ("mean", "share_2")] + ["mean_of_judges"]
with open(ROOT / "remediation_summary.csv", "w", newline="", encoding="utf-8") as fh:
    c = csv.writer(fh); c.writerow(hdr); c.writerows(rows)
json.dump({"n": n, "exact": exact, "within1": within1, "kappa": kappa, "judges": judges},
          open(ROOT / "remediation_agreement.json", "w"))
print(hdr); print(*rows, sep="\n")
print(f"judges={judges} n={n} exact={exact:.3f} within1={within1:.3f} weighted_kappa={kappa:.3f}")
