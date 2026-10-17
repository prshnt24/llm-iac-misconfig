"""Map each LLM finding to the static-analysis checks it describes (blinded judge).

For every (run, file) the judge sees the model's findings (no model name) and the full list of candidate
checks for that file (consensus, Checkov-only and Trivy-only rows of full_tool_comparison.csv, status hidden).
It returns, per finding, the candidate ids describing the same misconfiguration on the same resource.
Judgments are saved to judgments/<run>/<file>.json so they can be audited and spot-checked by hand.
"""
import csv, json, pathlib, re, sys
from concurrent.futures import ThreadPoolExecutor
import boto3

ROOT = pathlib.Path(__file__).parent
JUDGE = "global.openai.gpt-5.4"
REGION = "ap-southeast-2"
cands = {}
for i, r in enumerate(csv.DictReader(open(ROOT / "terragoat" / "full_tool_comparison.csv", encoding="utf-8-sig"))):
    cands.setdefault(r["file"], []).append({"id": f"c{i}", "resource": r["resource"], "check": r["canonical_check_id"],
                                            "name": r["checkov_names"] or r["trivy_names"], "status": r["status"]})

PROMPT = """You are adjudicating the output of a Terraform security review against a list of known checks.

Below are FINDINGS reported by a reviewer for the file {file}, and CANDIDATES (known failed checks for that file).
For each finding, list the ids of every candidate that describes the SAME misconfiguration on the SAME Terraform
resource (the finding's resource address must correspond to the candidate's resource, allowing for trivial
naming differences). A finding about a different resource, or a different weakness, is not a match even if the
topic is similar. If nothing matches return an empty list.

Return ONLY JSON: {{"matches": [{{"finding": <index>, "candidates": ["c1", ...]}}, ...]}} with one entry per finding.

FINDINGS:
{findings}

CANDIDATES:
{cands}
"""


def parse(text):
    m = re.search(r"\[.*\]", text, re.S)
    try:
        return json.loads(m.group(0)) if m else []
    except Exception:
        return []


def judge(job):
    run, f = job
    out = ROOT / "judgments" / run.name / f.name
    if out.exists():
        return
    rec = json.load(open(f, encoding="utf-8"))
    fname = rec["file"]
    findings = parse(rec["response"])
    if not findings:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"file": fname, "findings": [], "matches": []}), encoding="utf-8")
        return
    ftxt = "\n".join(f'{i}. resource={x.get("resource")} | issue={x.get("issue")} | risk={x.get("risk")}'
                     for i, x in enumerate(findings))
    ctxt = "\n".join(f'{c["id"]}: resource={c["resource"]} | {c["name"]}' for c in cands.get(fname, []))
    prompt = PROMPT.format(file=fname, findings=ftxt, cands=ctxt)
    client = boto3.client("bedrock-runtime", region_name=REGION)
    for _ in range(3):
        try:
            r = client.converse(modelId=JUDGE, messages=[{"role": "user", "content": [{"text": prompt}]}],
                                inferenceConfig={"maxTokens": 16000})
            txt = "".join(b["text"] for b in r["output"]["message"]["content"] if "text" in b)
            data = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
            break
        except Exception as e:
            print("retry", run.name, f.name, str(e)[:100])
    else:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"file": fname, "findings": findings, "matches": data["matches"]}, indent=1),
                   encoding="utf-8")
    print("judged", run.name, f.name)


if __name__ == "__main__":
    jobs = [(d, f) for d in sorted((ROOT / "responses").iterdir()) if d.is_dir() for f in sorted(d.glob("*.tf.json"))]
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(judge, jobs))
