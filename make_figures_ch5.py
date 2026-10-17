"""Chapter 5 figures from the scored CSV files."""
import csv, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "terragoat"
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 10})
LABEL = {"claude_zeroshot": "Claude\nzero-shot", "claude_fewshot": "Claude\nfew-shot", "gpt_zeroshot": "GPT-5.4\nzero-shot",
         "gpt_fewshot": "GPT-5.4\nfew-shot", "nova_zeroshot": "Nova Pro\nzero-shot", "nova_fewshot": "Nova Pro\nfew-shot"}
ORDER = list(LABEL)

# Figure 5.2: consensus groups by category
cat = list(csv.DictReader(open(OUT / "consensus_category_summary.csv", encoding="utf-8")))
fig, ax = plt.subplots(figsize=(6.5, 3.4))
names = [c["category"] for c in cat][::-1]
vals = [int(c["consensus_groups"]) for c in cat][::-1]
ax.barh(names, vals, color="#4C78A8")
for i, v in enumerate(vals):
    ax.text(v + 0.3, i, str(v), va="center")
ax.set_xlabel("Consensus groups (n = 75)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "figure_5_2_consensus_categories.png", dpi=300)
plt.close(fig)

# Figure 5.3: precision, recall, F1 by run
S = {r["run"]: r for r in csv.DictReader(open(ROOT / "scored_summary.csv"))}
fig, ax = plt.subplots(figsize=(6.5, 3.6))
x = np.arange(len(ORDER)); w = 0.26
for k, (key, lab, col) in enumerate([("precision_strict", "Precision", "#9ecae1"), ("recall", "Recall", "#3182bd"),
                                     ("f1_strict", "F1-score", "#08306b")]):
    v = [float(S[r][key]) for r in ORDER]
    b = ax.bar(x + (k - 1) * w, v, w, label=lab, color=col)
    for xi, vi in zip(x + (k - 1) * w, v):
        ax.text(xi, vi + 0.012, f"{vi:.2f}", ha="center", fontsize=7)
ax.set_xticks(x); ax.set_xticklabels([LABEL[r] for r in ORDER], fontsize=8)
ax.set_ylim(0, 1.05); ax.set_ylabel("Score (strict, consensus ground truth)")
ax.legend(frameon=False, ncol=3, loc="upper right")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "figure_5_3_model_scores.png", dpi=300)
plt.close(fig)

# Figure 5.4: category recall heat map
C = list(csv.DictReader(open(ROOT / "scored_by_category.csv")))
cats = [c["category"] for c in cat]
M = np.array([[float(next(c for c in C if c["run"] == r and c["category"] == k)["recall"]) for r in ORDER] for k in cats])
n = {c["category"]: c["gt_rows"] for c in C}
fig, ax = plt.subplots(figsize=(6.5, 3.8))
im = ax.imshow(M, cmap="Blues", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(ORDER))); ax.set_xticklabels([LABEL[r] for r in ORDER], fontsize=8)
ax.set_yticks(range(len(cats))); ax.set_yticklabels([f"{k} (n={n[k]})" for k in cats], fontsize=8)
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=8, color="white" if M[i, j] > 0.6 else "black")
fig.colorbar(im, ax=ax, label="Recall")
fig.tight_layout()
fig.savefig(OUT / "figure_5_4_category_recall.png", dpi=300)
print("figures written")
