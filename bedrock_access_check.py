"""Record that each evaluated model can be invoked through Amazon Bedrock with the settings used in the study."""
import time, boto3
import llm_evaluation as ev

c = boto3.client("bedrock-runtime", region_name=ev.REGION)
lines = [f"region: {ev.REGION}   checked: {time.strftime('%Y-%m-%d %H:%M:%S')}"]
for k, mid in ev.MODELS.items():
    cfg = {"maxTokens": 200}
    if k not in ev.NO_TEMPERATURE:
        cfg["temperature"] = 0
    t0 = time.time()
    try:
        r = c.converse(modelId=mid, messages=[{"role": "user", "content": [{"text": "Reply with the single word: ready"}]}], inferenceConfig=cfg)
        txt = "".join(b["text"] for b in r["output"]["message"]["content"] if "text" in b).strip().replace("\n", " ")[:40]
        u = r.get("usage", {})
        lines.append(f"OK   {mid:38s} temp={'default' if k in ev.NO_TEMPERATURE else 0}  in={u.get('inputTokens')} out={u.get('outputTokens')}  {time.time()-t0:.1f}s  -> {txt}")
    except Exception as e:
        lines.append(f"FAIL {mid:38s} {str(e)[:90]}")
open("bedrock_access_check.txt", "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
