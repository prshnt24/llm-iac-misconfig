"""Score judged LLM findings (judgments/<run>/<file>.json) against the static-analysis ground truth.

Definitions (unit of analysis = Terraform resource block + check):
  Ground truth  = the 75 CONSENSUS rows of terragoat/full_tool_comparison.csv (Checkov and Trivy agree).
  Finding       = one item in a model's JSON answer.
  Strict hit    = finding judged to describe at least one consensus row.
  Lenient hit   = finding judged to describe any row Checkov or Trivy reported (consensus, Checkov-only, Trivy-only).
  Precision     = hit findings / all findings (strict and lenient variants).
  Recall        = distinct consensus rows covered by at least one finding / 75.
  F1            = harmonic mean of precision and recall.
"""
import csv, json, pathlib, collections

ROOT = pathlib.Path(__file__).parent


def categorise(check_id, check_name, filename):
    """Same rules as the Chapter 4 notebook (terragoat/Untitled.ipynb cell 2)."""
    c, n, f = check_id.upper(), check_name.upper(), filename.upper()
    if 'SECRET' in c or ('HARD' in n and 'SECRET' in n):
        return 'Hardcoded Secrets'
    if 'IAM' in f or any(x in n for x in ['IAM POLICY', 'IAM ROLE', 'PRIVILEGE', 'CREDENTIALS EXPOSURE', 'PERMISSION']):
        return 'IAM Over-permissioning'
    if 'S3' in c and any(x in n for x in ['PUBLIC', 'BLOCK', 'ACL']):
        return 'Publicly Exposed Storage'
    if 'S3' in c or 'S3' in f:
        return 'Storage Configuration'
    if any(x in n for x in ['ENCRYPT', 'KMS', 'CMK', 'ENCRYPTED']):
        return 'Encryption at Rest'
    if any(x in n for x in ['INGRESS', 'EGRESS', 'SECURITY GROUP', 'VPC', 'SUBNET', 'PORT 22', 'PORT 80', '0.0.0.0']):
        return 'Network Exposure'
    if any(x in n for x in ['LOG', 'LOGGING', 'MONITORING', 'CLOUDTRAIL', 'CLOUDWATCH', 'AUDIT', 'TRACING']):
        return 'Logging & Monitoring'
    if 'LAMBDA' in f or 'LAMBDA' in n:
        return 'Lambda/Serverless'
    if any(x in n for x in ['BACKUP', 'DELETION PROTECTION', 'MULTI-AZ', 'MINOR UPGRADE']):
        return 'Availability & Resilience'
    if 'DOCKER' in c:
        return 'Container Security'
    return 'Other'


def write(name, header, rows):
    with open(ROOT / name, "w", newline="", encoding="utf-8") as fh:
        c = csv.writer(fh)
        c.writerow(header)
        c.writerows(rows)


def f1(p, r):
    return 2 * p * r / (p + r) if p + r else 0


rows = list(csv.DictReader(open(ROOT / "terragoat" / "full_tool_comparison.csv", encoding="utf-8-sig")))
cand = {}
for i, r in enumerate(rows):
    r["cat"] = categorise(r["canonical_check_id"] + " " + r["resource"].upper(), r["checkov_names"] or r["trivy_names"], r["file"])
    cand[f"c{i}"] = r
consensus = {k for k, r in cand.items() if r["status"] == "CONSENSUS"}
cat_total = collections.Counter(cand[k]["cat"] for k in consensus)

write("terragoat/consensus_category_summary.csv", ["category", "consensus_groups", "percentage"],
      [[k, v, round(100 * v / len(consensus), 1)] for k, v in cat_total.most_common()])

summary, detail, cats = [], [], []
for d in sorted((ROOT / "judgments").iterdir()):
    n = strict = lenient = 0
    covered = set()
    cat_f = collections.defaultdict(lambda: [0, 0])   # category -> [strict-hit findings, findings]
    for f in sorted(d.glob("*.tf.json")):
        j = json.load(open(f, encoding="utf-8"))
        m = {x["finding"]: [c for c in x["candidates"] if c in cand] for x in j["matches"]}
        for i, fd in enumerate(j["findings"]):
            ids = m.get(i, [])
            s = [c for c in ids if c in consensus]
            n += 1
            strict += bool(s)
            lenient += bool(ids)
            covered.update(s)
            cat = cand[(s or ids)[0]]["cat"] if ids else categorise("", str(fd.get("issue", "")), j["file"])
            cat_f[cat][1] += 1
            cat_f[cat][0] += bool(s)
            detail.append([d.name, j["file"], fd.get("resource"), fd.get("issue"), ";".join(s), ";".join(ids),
                           "strict" if s else ("lenient" if ids else "none"), ""])
    ps, pl, r = strict / n if n else 0, lenient / n if n else 0, len(covered) / len(consensus)
    summary.append([d.name, n, strict, lenient, len(covered), round(ps, 3), round(pl, 3), round(r, 3),
                    round(f1(ps, r), 3), round(f1(pl, r), 3)])
    for c in sorted(cat_total):
        cov = len([k for k in covered if cand[k]["cat"] == c])
        p = cat_f[c][0] / cat_f[c][1] if cat_f[c][1] else 0
        rc = cov / cat_total[c]
        cats.append([d.name, c, cat_total[c], cov, round(rc, 3), cat_f[c][1], round(p, 3), round(f1(p, rc), 3)])

write("scored_summary.csv", ["run", "findings", "strict_hits", "lenient_hits", "consensus_covered", "precision_strict",
                             "precision_lenient", "recall", "f1_strict", "f1_lenient"], summary)
write("scored_matches.csv", ["run", "file", "resource", "issue", "consensus_matches", "all_matches", "label",
                             "manual_review"], detail)
write("scored_by_category.csv", ["run", "category", "gt_rows", "covered", "recall", "findings", "precision", "f1"], cats)
print(*summary, sep="\n")
