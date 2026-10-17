"""Figure 3.1 (evaluation pipeline) and the rendered log excerpts used in Appendix E.

The Appendix E images are rendered from saved output files (logs and CSV results). They are not screen captures.
"""
import csv, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "terragoat"
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"]})


# ---------------- Figure 3.1 ----------------
def box(ax, x, y, w, h, n, title, body, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec="#34495e", lw=1.1))
    ax.add_patch(plt.Circle((x + 0.18, y + h - 0.2), 0.14, fc="#34495e", ec="none"))
    ax.text(x + 0.18, y + h - 0.2, str(n), color="white", ha="center", va="center", fontsize=8, fontweight="bold")
    ax.text(x + 0.42, y + h - 0.2, title, ha="left", va="center", fontsize=8.6, fontweight="bold", color="#1b2631")
    ax.text(x + 0.12, y + h - 0.45, body, ha="left", va="top", fontsize=7.4, color="#1b2631", linespacing=1.25)


def arrow(ax, p, q, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=10, lw=1.2, color="#34495e", connectionstyle=f"arc3,rad={rad}"))


fig, ax = plt.subplots(figsize=(7.2, 5.0))
ax.set_xlim(0, 10.2); ax.set_ylim(0, 6.4); ax.axis("off")
W, H = 3.0, 1.55
box(ax, 0.1, 4.65, W, H, 1, "Datasets", "TerraGoat AWS: 14 files\nGitHub sample: 30 files\nRegistry modules: 16 files", "#e8f1fa")
box(ax, 3.55, 4.65, W, H, 2, "Static analysis", "Checkov v3.3.9 and Trivy 0.73.0\nrun on every file\n(findings per resource)", "#e8f1fa")
box(ax, 7.0, 4.65, 3.1, H, 3, "Reference set", "Crosswalk of 41 Trivy to Checkov\npolicies; same file and resource\nConsensus: 75 / 21; all: 223 / 135", "#e8f1fa")
box(ax, 0.1, 2.5, W, H, 4, "Model runs", "Claude Sonnet 4.6, GPT-5.4,\nAmazon Nova Pro via Bedrock\nzero-shot and few-shot; JSON out", "#fdf2e3")
box(ax, 3.55, 2.5, W, H, 5, "Matching judge", "Blinded judge maps each model\nfinding to tool findings\n(strict and lenient hits)", "#fdf2e3")
box(ax, 7.0, 2.5, 3.1, H, 6, "Detection metrics", "Precision, recall, F1, coverage,\ncategory recall, exact tests\nanswers RQ1 and RQ2", "#e6f4ea")
box(ax, 3.55, 0.35, W, H, 7, "Remediation scoring", "Two blinded judges, 0 to 2 rubric,\nweighted kappa between judges\nanswers RQ3", "#e6f4ea")
box(ax, 7.0, 0.35, 3.1, H, 8, "Validity check", "Judge labels unmatched findings\nvalid, arguable or invalid\n(exploratory; qualifies precision)", "#f3e8f7")
arrow(ax, (3.15, 5.42), (3.5, 5.42)); arrow(ax, (6.6, 5.42), (6.95, 5.42))
arrow(ax, (1.6, 4.62), (1.6, 4.1))
arrow(ax, (3.15, 3.27), (3.5, 3.27)); arrow(ax, (6.6, 3.27), (6.95, 3.27))
arrow(ax, (8.55, 4.62), (6.6, 4.05), rad=0.15)
arrow(ax, (5.05, 2.47), (5.05, 1.93))
arrow(ax, (6.6, 2.7), (6.95, 1.95), rad=-0.15)
ax.text(8.55, 4.3, "scores model findings\nagainst this set", fontsize=6.6, ha="center", color="#566573", style="italic")
fig.tight_layout(pad=0.3)
fig.savefig(OUT / "figure_3_1_methodology_pipeline_v2.png", dpi=300)
plt.close(fig)


# ---------------- Appendix E renders ----------------
def terminal(lines, title, path, width=7.0):
    h = 0.45 + 0.19 * len(lines)
    fig, ax = plt.subplots(figsize=(width, h))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.patch.set_facecolor("#1e2430")
    ax.text(0.01, 0.98, title, color="#9fb3c8", fontsize=7.5, va="top", family="monospace", fontweight="bold")
    for i, ln in enumerate(lines):
        ax.text(0.01, 0.98 - (i + 1.6) / (len(lines) + 2.2), ln[:118], color="#e6edf3", fontsize=6.3, va="top", family="monospace")
    fig.savefig(path, dpi=250, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def head_tail(path, head=0, tail=0, grep=None):
    ls = [l.rstrip() for l in open(ROOT / path, encoding="utf-8", errors="replace") if l.strip()]
    if grep:
        return [l for l in ls if grep in l][:1]
    return ls[:head] + ([ "..." ] if head and tail else []) + (ls[-tail:] if tail else [])


ev1 = head_tail("eval_run.log", head=5) + ["..."] + head_tail("eval_run.log", grep="retry nova zeroshot") + head_tail("eval_nova.log", tail=3)
terminal([l.replace("An error occurred (ValidationException) when calling the Converse operation:", "ValidationException:") for l in ev1],
         "E.1  python llm_evaluation.py   (TerraGoat run, excerpt of saved log)", OUT / "evidence_E1_run_log.png")
terminal(open(ROOT / "bedrock_access_check.txt", encoding="utf-8").read().splitlines(),
         "E.2  python bedrock_access_check.py   (model access test, saved output)", OUT / "evidence_E2_access_check.png")
rows = list(csv.reader(open(ROOT / "scored_summary.csv", encoding="utf-8")))
fmt = lambda r: f"{r[0]:16s}{r[1]:>9s}{r[2]:>8s}{r[3]:>8s}{r[4]:>9s}{r[5]:>10s}{r[6]:>10s}{r[7]:>8s}{r[8]:>10s}{r[9]:>10s}"
hdr = ["run", "findings", "strict", "lenient", "covered", "P strict", "P lenient", "recall", "F1 strict", "F1 len."]
terminal([fmt(hdr)] + [fmt(r) for r in rows[1:]], "E.3  python score_results.py   (contents of scored_summary.csv, TerraGoat)", OUT / "evidence_E3_scores.png")
ev4 = head_tail("corpus_run.log", head=2) + ["..."] + head_tail("corpus_run.log", tail=6)
terminal(ev4, "E.4  bash run_corpus_eval.sh   (second dataset, excerpt of saved log)", OUT / "evidence_E4_corpus_log.png")
print("ok")
