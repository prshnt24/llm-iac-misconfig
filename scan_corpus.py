"""Scan the collected corpus with Checkov and Trivy and align the findings with the existing policy crosswalk.

Each file is copied to scan_work/<id>/main.tf so every file is analysed as its own module. Output is written in the same
layout as the TerraGoat comparison (corpus_eval/terragoat/full_tool_comparison.csv and consensus_ground_truth.csv), so the
unchanged evaluation scripts can be run inside corpus_eval/.
"""
import collections, csv, json, os, pathlib, shutil, subprocess

CHECKOV = shutil.which("checkov") or r"C:\Users\lenovo\anaconda3\Scripts\checkov.exe"
TRIVY = shutil.which("trivy") or r"C:\Users\lenovo\AppData\Local\Microsoft\WinGet\Packages\AquaSecurity.Trivy_Microsoft.Winget.Source_8wekyb3d8bbwe\trivy.exe"

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "corpus_eval" / "terragoat" / "terraform" / "aws"
WORK = ROOT / "scan_work"
OUT = ROOT / "corpus_eval" / "terragoat"
cross = {r["trivy_id"]: r["checkov_id"] for r in csv.DictReader(open(ROOT / "terragoat" / "manual_policy_crosswalk.csv", encoding="utf-8-sig"))}

if WORK.exists():
    shutil.rmtree(WORK)
for f in SRC.glob("*.tf"):
    (WORK / f.stem).mkdir(parents=True)
    shutil.copy(f, WORK / f.stem / "main.tf")
ck_path, tv_path = OUT / "checkov_results.json", OUT / "trivy_results.json"
if not os.environ.get("SKIP_SCAN"):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    with open(ck_path, "w", encoding="utf-8") as fh:
        subprocess.run([CHECKOV, "-d", str(WORK), "--framework", "terraform", "-o", "json", "--quiet"], stdout=fh, stderr=subprocess.DEVNULL, env=env)
    subprocess.run([TRIVY, "config", str(WORK), "--format", "json", "--output", str(tv_path), "--quiet"], capture_output=True)

ck = json.load(open(ck_path, encoding="utf-8"))
tv = json.load(open(tv_path, encoding="utf-8"))
if isinstance(ck, dict):
    ck = [ck]


def fid(path):
    parts = pathlib.PurePath(path.replace("\\", "/")).parts
    for i, p in enumerate(parts):
        if p == "scan_work" and i + 1 < len(parts):
            return parts[i + 1] + ".tf"
    return parts[-2] + ".tf" if len(parts) > 1 else parts[-1]


C, T = [], []
for g in ck:
    for f in g.get("results", {}).get("failed_checks", []):
        p = (f.get("repo_file_path") or f.get("file_path") or "").replace("\\", "/")
        if p.endswith(".tf"):
            C.append(dict(file=fid(p), resource=f.get("resource", ""), id=f.get("check_id", ""), name=f.get("check_name", "")))
for r in tv.get("Results", []):
    if r.get("Type") != "terraform":
        continue
    for f in r.get("Misconfigurations", []) or []:
        if f.get("Status") == "FAIL":
            T.append(dict(file=fid(r["Target"]), resource=(f.get("CauseMetadata") or {}).get("Resource", ""), id=f.get("ID", ""), name=f.get("Title", "")))
comb = collections.defaultdict(lambda: {"ck": [], "tv": []})
for x in C:
    comb[(x["file"], x["resource"].lower(), "CK:" + x["id"])]["ck"].append(x)
for x in T:
    m = cross.get(x["id"])
    comb[(x["file"], x["resource"].lower(), ("CK:" + m) if m else ("TV:" + x["id"]))]["tv"].append(x)
rows = []
for (fl, res, ident), v in sorted(comb.items()):
    c, t = v["ck"], v["tv"]
    a = (c or t)[0]
    rows.append(dict(status="CONSENSUS" if c and t else ("CHECKOV ONLY" if c else "TRIVY ONLY"), file=fl, path="/terraform/aws/" + fl,
                     resource=a["resource"], canonical_check_id=ident[3:], checkov_ids=";".join(sorted({x["id"] for x in c})),
                     trivy_ids=";".join(sorted({x["id"] for x in t})), checkov_names=";".join(sorted({x["name"] for x in c})),
                     trivy_names=";".join(sorted({x["name"] for x in t})), checkov_occurrences=len(c), trivy_occurrences=len(t)))
fields = list(rows[0])
for fn, rs in [("full_tool_comparison.csv", rows), ("consensus_ground_truth.csv", [r for r in rows if r["status"] == "CONSENSUS"])]:
    with open(OUT / fn, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rs)
st = collections.Counter(r["status"] for r in rows)
files_with = collections.Counter(r["file"] for r in rows if r["status"] == "CONSENSUS")
print("raw Checkov", len(C), "raw Trivy", len(T), "groups", len(rows), dict(st), "files with consensus", len(files_with), "of", len(list(SRC.glob('*.tf'))))
