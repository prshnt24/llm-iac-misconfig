"""Run zero-shot and few-shot Terraform security reviews on the TerraGoat AWS files.

All models are called through Amazon Bedrock (Converse API). The key is read from the
AWS_BEARER_TOKEN_BEDROCK environment variable (never hard-code it); region defaults to ap-southeast-2.
Usage:
  python llm_evaluation.py --dry-run                 # no API calls, writes prompts only
  python llm_evaluation.py --models claude nova     # run a subset
Raw responses are saved to responses/<model>_<strategy>/<file>.json (Appendix D evidence).
"""
import argparse, json, os, pathlib, time

ROOT = pathlib.Path(__file__).parent
TF_DIR = ROOT / "terragoat" / "terraform" / "aws"
OUT = ROOT / "responses"
REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
MODELS = {"claude": "au.anthropic.claude-sonnet-4-6", "gpt": "global.openai.gpt-5.4",
          "nova": "apac.amazon.nova-pro-v1:0"}
NO_TEMPERATURE = {"gpt"}  # GPT-5.x on Bedrock rejects the temperature field

TASK = ("You are a cloud security expert specialising in Terraform Infrastructure as Code. "
        "Review the following Terraform configuration and identify all security misconfigurations. "
        "For each issue found give: the Terraform resource address (e.g. aws_s3_bucket.data), the name of the "
        "misconfiguration, the security risk it creates, and a specific remediation including the attribute or "
        "resource block to change. Return ONLY a JSON array of objects with keys "
        '"resource", "issue", "risk", "remediation". If none are found return [].')

FEW_SHOT = """Examples of the expected analysis:

Example 1 (IAM over-permissioning)
Resource: aws_iam_policy with Action=["s3:*"] and Resource="*"
Finding: {"resource": "aws_iam_policy.example", "issue": "Overly broad IAM permissions", "risk": "Wildcard grants unrestricted S3 access if the role is compromised", "remediation": "Replace Resource=\\"*\\" with the specific bucket ARN and s3:* with only the required S3 actions"}

Example 2 (missing S3 public access block)
Resource: aws_s3_bucket with no aws_s3_bucket_public_access_block
Finding: {"resource": "aws_s3_bucket.example", "issue": "Missing S3 Block Public Access", "risk": "Bucket could be exposed to the public internet via ACL or policy", "remediation": "Add an aws_s3_bucket_public_access_block resource with all four blocking settings set to true"}
"""


def build_prompt(strategy, tf_text):
    parts = [TASK]
    if strategy == "fewshot":
        parts.append(FEW_SHOT)
    parts.append("--- TERRAFORM CONFIGURATION ---\n" + tf_text)
    return "\n\n".join(parts)


def call(model, prompt):
    import boto3
    cfg = {"maxTokens": 9000 if model == "nova" else 16000}
    if model not in NO_TEMPERATURE:
        cfg["temperature"] = 0
    r = boto3.client("bedrock-runtime", region_name=REGION).converse(
        modelId=MODELS[model], messages=[{"role": "user", "content": [{"text": prompt}]}], inferenceConfig=cfg)
    return "".join(b["text"] for b in r["output"]["message"]["content"] if "text" in b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=list(MODELS), choices=list(MODELS))
    ap.add_argument("--strategies", nargs="+", default=["zeroshot", "fewshot"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    files = sorted(TF_DIR.glob("*.tf"))
    print(f"{len(files)} files x {len(a.models)} models x {len(a.strategies)} strategies")
    for m in a.models:
        for s in a.strategies:
            d = OUT / f"{m}_{s}"
            d.mkdir(parents=True, exist_ok=True)
            for f in files:
                dest = d / f"{f.name}.json"
                if dest.exists():
                    continue  # resume support
                prompt = build_prompt(s, f.read_text(encoding="utf-8"))
                if a.dry_run:
                    (d / f"{f.name}.prompt.txt").write_text(prompt, encoding="utf-8")
                    continue
                for attempt in range(3):
                    try:
                        text = call(m, prompt)
                        break
                    except Exception as e:
                        print("retry", m, s, f.name, e)
                        time.sleep(5 * (attempt + 1))
                else:
                    continue
                dest.write_text(json.dumps({"model": MODELS[m], "strategy": s, "file": f.name,
                                            "temperature": None if m in NO_TEMPERATURE else 0, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                            "response": text}, indent=2), encoding="utf-8")
                print("saved", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
