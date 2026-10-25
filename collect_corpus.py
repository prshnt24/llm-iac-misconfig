"""Collect the GitHub corpus and Terraform Registry modules for the generalisation check.

GitHub: repositories found with the GitHub search API (topic terraform, language HCL, >= 5 stars, pushed after
2023-01-01, AWS in name or description), excluding the terraform-aws-modules organisation and vulnerable-by-design
projects. One AWS .tf file per repository is chosen with a fixed random seed.
Registry: root modules of the terraform-aws-modules organisation (the most used AWS modules on the Registry).
Registry files are drawn in two passes: the first accepts root files of 800 to 10,000 bytes, and because most module root
files are larger, a second pass (supplement_registry) accepts files up to 20,000 bytes for modules not yet sampled, until 16
registry files are reached. Both passes were run to build the dataset used in the dissertation.
Each file is copied to corpus_eval/terragoat/terraform/aws/<id>.tf (a layout the existing scripts already read) and
described in corpus_manifest.csv with repository, commit and licence so the sample can be reproduced.
"""
import csv, json, pathlib, random, re, shutil, subprocess, sys, time
import requests

ROOT = pathlib.Path(__file__).parent
WORK = ROOT / "corpus_work"            # shallow clones (not committed)
DEST = ROOT / "corpus_eval" / "terragoat" / "terraform" / "aws"
random.seed(2026)
N_GH, N_REG = 30, 20
REG = ["vpc", "s3-bucket", "iam", "ec2-instance", "rds", "eks", "security-group", "lambda", "alb", "kms", "sns", "sqs",
       "dynamodb-table", "ecr", "elasticache", "efs", "cloudwatch", "autoscaling", "apigateway-v2", "acm", "route53",
       "cloudfront", "ebs", "eventbridge", "step-functions", "sqs", "secrets-manager", "key-pair", "rds-aurora", "msk-kafka"]
BAD = re.compile(r"goat|vuln|damn|insecure|kubernetes-goat|cloudgoat|sadcloud", re.I)


def run(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=300)


def clone(url, name):
    d = WORK / name
    if not d.exists():
        r = run("git", "-c", "core.longpaths=true", "clone", "--depth", "1", "--quiet", url, str(d))
        if r.returncode:
            return None
    sha = run("git", "rev-parse", "HEAD", cwd=d).stdout.strip()
    return d, sha


def candidates(d):
    out = []
    for p in d.rglob("*.tf"):
        rel = p.relative_to(d).as_posix()
        if any(x in rel.split("/") for x in (".terraform", ".git", "test", "tests", ".github")):
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        n_res = len(re.findall(r'resource\s+"aws_', txt))
        if 800 <= len(txt.encode()) <= 10000 and n_res >= 2:
            out.append((p, rel, n_res))
    return out


def main():
    WORK.mkdir(exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)
    rows = []
    # ---- GitHub sample
    repos = []
    for page in (1, 2):
        q = "terraform aws in:name,description topic:terraform language:HCL stars:>=5 pushed:>=2023-01-01"
        r = requests.get("https://api.github.com/search/repositories", params={"q": q, "sort": "stars", "per_page": 100, "page": page},
                         headers={"Accept": "application/vnd.github+json"}, timeout=60)
        r.raise_for_status()
        repos += r.json()["items"]
        time.sleep(7)
    repos = [x for x in repos if x["owner"]["login"].lower() != "terraform-aws-modules" and not BAD.search(x["name"]) and not x["fork"] and not x["archived"]]
    random.shuffle(repos)
    n = 0
    for x in repos:
        if n >= N_GH:
            break
        c = clone(x["clone_url"], "gh_" + x["name"])
        if not c:
            continue
        d, sha = c
        cand = candidates(d)
        if not cand:
            continue
        p, rel, nres = random.choice(cand)
        n += 1
        fid = f"gh{n:02d}"
        shutil.copy(p, DEST / f"{fid}.tf")
        rows.append([fid, "github", x["full_name"], x["html_url"], sha, rel, p.stat().st_size, x["stargazers_count"], x["pushed_at"][:10], (x["license"] or {}).get("spdx_id", "none")])
        print("gh", fid, x["full_name"], rel)
    # ---- Registry modules
    m = 0
    for name in dict.fromkeys(REG):
        if m >= N_REG:
            break
        url = f"https://github.com/terraform-aws-modules/terraform-aws-{name}"
        c = clone(url, "reg_" + name)
        if not c:
            continue
        d, sha = c
        root = [(p, p.name, len(re.findall(r'resource\s+"aws_', p.read_text(encoding="utf-8")))) for p in d.glob("*.tf")
                if 800 <= p.stat().st_size <= 10000]
        root = [t for t in root if t[2] >= 2]
        if not root:
            continue
        p, rel, _ = max(root, key=lambda t: t[2])
        m += 1
        fid = f"reg{m:02d}"
        shutil.copy(p, DEST / f"{fid}.tf")
        rows.append([fid, "registry", f"terraform-aws-modules/terraform-aws-{name}", url, sha, rel, p.stat().st_size, "", "", "Apache-2.0"])
        print("reg", fid, name, rel)
    with open(ROOT / "corpus_manifest.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "source", "repository", "url", "commit", "original_path", "bytes", "stars", "last_push", "licence"])
        w.writerows(rows)
    print("files:", len(rows))


def supplement_registry(target=16, max_bytes=20000):
    """Second registry pass: larger root files for modules that the first pass skipped."""
    man = list(csv.reader(open(ROOT / "corpus_manifest.csv", encoding="utf-8")))
    have = {r[2] for r in man[1:]}
    m = sum(1 for r in man[1:] if r[1] == "registry")
    for d in sorted(WORK.glob("reg_*")):
        repo = f"terraform-aws-modules/terraform-aws-{d.name[4:]}"
        if repo in have or m >= target:
            continue
        cand = [(p, len(re.findall(r'resource\s+"aws_', p.read_text(encoding="utf-8")))) for p in d.glob("*.tf") if 800 <= p.stat().st_size <= max_bytes]
        cand = [x for x in cand if x[1] >= 2]
        if not cand:
            continue
        p, _ = max(cand, key=lambda x: x[1])
        m += 1
        fid = f"reg{m:02d}"
        shutil.copy(p, DEST / f"{fid}.tf")
        sha = run("git", "rev-parse", "HEAD", cwd=d).stdout.strip()
        man.append([fid, "registry", repo, f"https://github.com/{repo}", sha, p.name, p.stat().st_size, "", "", "Apache-2.0"])
        print("reg", fid, d.name[4:], p.name)
    with open(ROOT / "corpus_manifest.csv", "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(man)


if __name__ == "__main__":
    main()
    supplement_registry()
