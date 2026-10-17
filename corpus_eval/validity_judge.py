"""Exploratory check of findings that matched no Checkov/Trivy row.

A blinded judge reads the Terraform source and labels each unmatched finding VALID (a genuine security weakness
in that resource), INVALID (the weakness is not present or the claim is wrong) or DEBATABLE (best-practice or
context-dependent). Output: validity/<run>/<file>.json
"""
import json, pathlib, re
from concurrent.futures import ThreadPoolExecutor
import boto3

ROOT = pathlib.Path(__file__).parent
REGION = "ap-southeast-2"
MODEL = "global.openai.gpt-5.4"
PROMPT = """You are an expert AWS and Terraform security reviewer. Below is a Terraform file and a list of FINDINGS
that a reviewer reported about it. For each finding decide, using only the source:
  VALID     = the weakness genuinely exists in the named resource and is a real security concern
  INVALID   = the weakness is not present, the resource does not exist, or the claim is wrong
  DEBATABLE = a best-practice or context-dependent point rather than a clear weakness
Return ONLY JSON: {{"labels": [{{"finding": <index>, "label": "VALID|INVALID|DEBATABLE"}}, ...]}}

TERRAFORM SOURCE ({file}):
{source}

FINDINGS:
{items}
"""


def job(args):
    run, f = args
    j = json.load(open(f, encoding="utf-8"))
    matched = {x["finding"] for x in j["matches"] if x["candidates"]}
    items = [(i, x) for i, x in enumerate(j["findings"]) if i not in matched]
    out = ROOT / "validity" / run.name / f.name
    if out.exists():
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    if not items:
        out.write_text(json.dumps({"labels": []}), encoding="utf-8")
        return
    src = (ROOT / "terragoat" / "terraform" / "aws" / j["file"]).read_text(encoding="utf-8")
    txt = "\n".join(f'{i}. resource={x.get("resource")} | issue={x.get("issue")} | risk={x.get("risk")}' for i, x in items)
    client = boto3.client("bedrock-runtime", region_name=REGION)
    for _ in range(3):
        try:
            r = client.converse(modelId=MODEL, messages=[{"role": "user", "content": [{"text": PROMPT.format(file=j["file"], source=src, items=txt)}]}],
                                inferenceConfig={"maxTokens": 16000})
            t = "".join(b["text"] for b in r["output"]["message"]["content"] if "text" in b)
            data = json.loads(re.search(r"\{.*\}", t, re.S).group(0))
            break
        except Exception as e:
            print("retry", run.name, f.name, str(e)[:80])
    else:
        out.unlink(missing_ok=True)
        return
    out.write_text(json.dumps({"labels": data["labels"], "findings": {str(i): x for i, x in items}}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    jobs = [(d, f) for d in sorted((ROOT / "judgments").iterdir()) if d.is_dir() for f in sorted(d.glob("*.tf.json"))]
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(job, jobs))
