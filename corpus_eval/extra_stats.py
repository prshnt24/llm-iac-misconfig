"""Union coverage (all Checkov/Trivy rows) and paired sign tests on consensus-row coverage."""
import csv, json, pathlib, itertools, math

ROOT = pathlib.Path(__file__).parent
rows = list(csv.DictReader(open(ROOT / "terragoat" / "full_tool_comparison.csv", encoding="utf-8-sig")))
cons = {f"c{i}" for i, r in enumerate(rows) if r["status"] == "CONSENSUS"}
allc = {f"c{i}" for i in range(len(rows))}
cov_c, cov_a = {}, {}
for d in sorted((ROOT / "judgments").iterdir()):
    c, a = set(), set()
    for f in d.glob("*.tf.json"):
        for x in json.load(open(f, encoding="utf-8"))["matches"]:
            ids = set(x["candidates"]) & allc
            a |= ids
            c |= ids & cons
    cov_c[d.name], cov_a[d.name] = c, a


def sign_p(b, c):  # two-sided exact binomial (McNemar) on discordant pairs
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


out = [["run", "consensus_covered", "all_tool_rows_covered", "of_223", "checkov_only_covered", "trivy_only_covered"]]
for r in cov_c:
    st = lambda s: {i for i in cov_a[r] if rows[int(i[1:])]["status"] == s}
    out.append([r, len(cov_c[r]), len(cov_a[r]), round(len(cov_a[r]) / len(allc), 3), len(st("CHECKOV ONLY")), len(st("TRIVY ONLY"))])
pairs = []
runs = list(cov_c)
for a, b in [("claude_zeroshot", "gpt_zeroshot"), ("claude_zeroshot", "nova_zeroshot"), ("gpt_zeroshot", "nova_zeroshot")]:
    only_a, only_b = len(cov_c[a] - cov_c[b]), len(cov_c[b] - cov_c[a])
    pairs.append([a, b, only_a, only_b, round(sign_p(only_a, only_b), 4)])
with open(ROOT / "coverage_summary.csv", "w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(out)
with open(ROOT / "paired_tests.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["run_a", "run_b", "only_a", "only_b", "p_exact"]); w.writerows(pairs)
print(*out, sep="\n"); print(*pairs, sep="\n")
