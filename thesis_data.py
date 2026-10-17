"""Load every result file used in the dissertation text, so numbers in the prose come from the data."""
import csv, json, pathlib, collections

ROOT = pathlib.Path(__file__).parent
RUNS = ["claude_zeroshot", "claude_fewshot", "gpt_zeroshot", "gpt_fewshot", "nova_zeroshot", "nova_fewshot"]
NAME = {"claude": "Claude Sonnet 4.6", "gpt": "GPT-5.4", "nova": "Amazon Nova Pro"}
STRAT = {"zeroshot": "Zero-shot", "fewshot": "Few-shot"}


def rd(name):
    return list(csv.DictReader(open(ROOT / name, encoding="utf-8-sig")))


S = {r["run"]: r for r in rd("scored_summary.csv")}
CV = {r["run"]: r for r in rd("coverage_summary.csv")}
VAL = {r["run"]: r for r in rd("validity_summary.csv")}
REM = {r["run"]: r for r in rd("remediation_summary.csv")}
PT = {(r["run_a"], r["run_b"]): r for r in rd("paired_tests.csv")}
CATROWS = rd("scored_by_category.csv")
CATSUM = rd("terragoat/consensus_category_summary.csv")
CATS = [c["category"] for c in CATSUM]
AGREE = json.load(open(ROOT / "remediation_agreement.json"))
FULL = rd("terragoat/full_tool_comparison.csv")
N_CONS = sum(r["status"] == "CONSENSUS" for r in FULL)
N_ALL = len(FULL)
N_CHK_ONLY = sum(r["status"] == "CHECKOV ONLY" for r in FULL)
N_TRV_ONLY = sum(r["status"] == "TRIVY ONLY" for r in FULL)


def cat(run, c, key):
    return float(next(x for x in CATROWS if x["run"] == run and x["category"] == c)[key])


def gt_n(c):
    return int(next(x for x in CATROWS if x["category"] == c)["gt_rows"])


def label(run):
    m, s = run.split("_")
    return f"{NAME[m]}, {STRAT[s].lower()}"


# recall without rds.tf, and rds.tf coverage per run
_cons = {f"c{i}": r for i, r in enumerate(FULL) if r["status"] == "CONSENSUS"}
RDS_TOTAL = sum(r["file"] == "rds.tf" for r in _cons.values())
RDS_COV, NORDS_RECALL, FINDINGS_RDS = {}, {}, {}
for run in RUNS:
    s = set()
    for f in (ROOT / "judgments" / run).glob("*.tf.json"):
        j = json.load(open(f, encoding="utf-8"))
        if j["file"] == "rds.tf":
            FINDINGS_RDS[run] = len(j["findings"])
        for x in j["matches"]:
            s |= set(x["candidates"]) & set(_cons)
    RDS_COV[run] = sum(_cons[k]["file"] == "rds.tf" for k in s)
    NORDS_RECALL[run] = (len(s) - RDS_COV[run]) / (len(_cons) - RDS_TOTAL)

# remediation score distribution (first judge)
REM_DIST = {}
for run in RUNS:
    c = collections.Counter()
    for f in (ROOT / "remediation_scores" / AGREE["judges"][0] / run).glob("*.json"):
        for s in json.load(open(f, encoding="utf-8"))["scores"]:
            c[int(s["score"])] += 1
    REM_DIST[run] = c

# response time stamps and size
STAMPS = []
for run in RUNS:
    for f in (ROOT / "responses" / run).glob("*.tf.json"):
        STAMPS.append(json.load(open(f, encoding="utf-8"))["timestamp"])
FIRST, LAST = min(STAMPS), max(STAMPS)


def f2(x):
    return f"{float(x):.2f}"


def pc(x):
    return f"{100 * float(x):.0f}%"


# ---------------- generalisation dataset (corpus_eval) ----------------
CE = ROOT / "corpus_eval"


def rdc(name):
    return list(csv.DictReader(open(CE / name, encoding="utf-8-sig")))


CRUNS = ["claude_zeroshot", "gpt_zeroshot", "nova_zeroshot"]
CS = {r["run"]: r for r in rdc("scored_summary.csv")}
CCV = {r["run"]: r for r in rdc("coverage_summary.csv")}
CVAL = {r["run"]: r for r in rdc("validity_summary.csv")}
CREM = {r["run"]: r for r in rdc("remediation_summary.csv")}
CPT = {(r["run_a"], r["run_b"]): r for r in rdc("paired_tests.csv")}
CAGREE = json.load(open(CE / "remediation_agreement.json"))
CFULL = rdc("terragoat/full_tool_comparison.csv")
CMAN = list(csv.DictReader(open(ROOT / "corpus_manifest.csv", encoding="utf-8")))
C_N_FILES = len(CMAN)
C_N_GH = sum(r["source"] == "github" for r in CMAN)
C_N_REG = sum(r["source"] == "registry" for r in CMAN)
C_N_CONS = sum(r["status"] == "CONSENSUS" for r in CFULL)
C_N_ALL = len(CFULL)
C_N_CHK = sum(r["status"] == "CHECKOV ONLY" for r in CFULL)
C_N_TRV = sum(r["status"] == "TRIVY ONLY" for r in CFULL)
C_CONS_FILES = len({r["file"] for r in CFULL if r["status"] == "CONSENSUS"})
C_FILES_PER = {}
for _r in CRUNS:
    _n = [len(json.load(open(f, encoding="utf-8"))["findings"]) for f in (CE / "judgments" / _r).glob("*.tf.json")]
    C_FILES_PER[_r] = (sum(_n) / len(_n), sum(1 for x in _n if x == 0))
_ck = json.load(open(CE / "terragoat" / "checkov_results.json", encoding="utf-8"))
_ck = _ck if isinstance(_ck, list) else [_ck]
C_RAW_CK = sum(len(g.get("results", {}).get("failed_checks", [])) for g in _ck)
C_RAW_TV = sum(len(r.get("Misconfigurations") or []) for r in json.load(open(CE / "terragoat" / "trivy_results.json", encoding="utf-8")).get("Results", []))
C_NET = sum(1 for r in CFULL if r["status"] == "CONSENSUS" and any(k in (r["checkov_names"]).upper() for k in ("SECURITY GROUP", "VPC", "INGRESS", "EGRESS")))
