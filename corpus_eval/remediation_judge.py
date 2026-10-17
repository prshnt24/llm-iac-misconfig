"""Score remediation advice on the 3-point rubric (2 = correct and specific, 1 = partially correct, 0 = incorrect/absent).

Only findings that the matching step judged to describe a consensus check are scored (the finding is a correct
detection, so its remediation can be compared with the known fix for that check). Two blinded judges score
independently so inter-judge agreement can be reported. Outputs: remediation_scores/<judge>/<run>/<file>.json
"""
import csv, json, pathlib, re
from concurrent.futures import ThreadPoolExecutor
import boto3

ROOT = pathlib.Path(__file__).parent
REGION = "ap-southeast-2"
JUDGES = {"gpt54": ("global.openai.gpt-5.4", False), "sonnet55": ("global.anthropic.claude-sonnet-5-5", False)}
rows = list(csv.DictReader(open(ROOT / "terragoat" / "full_tool_comparison.csv", encoding="utf-8-sig")))
cand = {f"c{i}": r for i, r in enumerate(rows)}

PROMPT = """You are an expert Terraform and AWS security reviewer scoring remediation advice.

For each ITEM below, a reviewer identified a real misconfiguration (the KNOWN CHECK) and proposed a remediation.
Score the remediation against the standard fix that satisfies the KNOWN CHECK, using the Terraform source for context:
  2 = correct and specific: names the right resource attribute or block and a value that would fix the check
  1 = partially correct: right direction but vague, incomplete, or missing a needed attribute
  0 = incorrect, irrelevant, or absent
Return ONLY JSON: {{"scores": [{{"item": <index>, "score": 0|1|2, "reason": "<short>"}}, ...]}}

TERRAFORM SOURCE ({file}):
{source}

ITEMS:
{items}
"""


def items_for(j):
    out = []
    for x in j["matches"]:
        ids = [c for c in x["candidates"] if c in cand and cand[c]["status"] == "CONSENSUS"]
        if not ids:
            continue
        f = j["findings"][x["finding"]]
        known = "; ".join(f'{cand[c]["canonical_check_id"]} {cand[c]["checkov_names"]} (resource {cand[c]["resource"]})' for c in ids)
        out.append({"finding": x["finding"], "known": known, "issue": f.get("issue"), "remediation": f.get("remediation")})
    return out


def job(args):
    judge, run, f = args
    out = ROOT / "remediation_scores" / judge / run.name / f.name
    if out.exists():
        return
    j = json.load(open(f, encoding="utf-8"))
    items = items_for(j)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not items:
        out.write_text(json.dumps({"items": [], "scores": []}), encoding="utf-8")
        return
    src = (ROOT / "terragoat" / "terraform" / "aws" / j["file"].replace(".json", "")).read_text(encoding="utf-8")
    itxt = "\n".join(f'{i}. KNOWN CHECK: {it["known"]}\n   REVIEWER ISSUE: {it["issue"]}\n   REVIEWER REMEDIATION: {it["remediation"]}'
                     for i, it in enumerate(items))
    prompt = PROMPT.format(file=j["file"], source=src, items=itxt)
    client = boto3.client("bedrock-runtime", region_name=REGION)
    for _ in range(3):
        try:
            r = client.converse(modelId=JUDGES[judge][0], messages=[{"role": "user", "content": [{"text": prompt}]}],
                                inferenceConfig={"maxTokens": 16000})
            txt = "".join(b["text"] for b in r["output"]["message"]["content"] if "text" in b)
            data = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
            break
        except Exception as e:
            print("retry", judge, run.name, f.name, str(e)[:100])
    else:
        return
    out.write_text(json.dumps({"items": items, "scores": data["scores"]}, indent=1), encoding="utf-8")
    print("scored", judge, run.name, f.name)


if __name__ == "__main__":
    jobs = [(jd, d, f) for jd in JUDGES for d in sorted((ROOT / "judgments").iterdir()) if d.is_dir()
            for f in sorted(d.glob("*.tf.json"))]
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(job, jobs))
