"""Figures 1-2 of the paper from the annotated files.

Usage: python make_figures.py results/annotated_llama.csv results/annotated_qwen.csv
Writes fig_cats.pdf and fig_rates.pdf in figures/.
"""
import sys, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analyze import load, wilson, paired   # same normalisation as the tables

NAMES = {"llama": "Llama 3.2 3B", "qwen": "Qwen2.5 3B"}
data = {}
for path in sys.argv[1:]:
    tag = path.split("annotated_")[-1].replace(".csv", "")
    data[tag] = load(path)

def counts(rows, verdict, cond):
    ids, by = paired(rows, verdict)
    return collections.Counter(by[i][cond]["L"] for i in ids), len(ids)

plt.rcParams.update({"font.size": 8, "font.family": "serif"})

# Figure 1: reply categories, false claims (counts)
fig, ax = plt.subplots(figsize=(3.2, 2.0))
labels, rows_ = [], []
for tag in data:
    for cond, nm in (("assistant", "assistant-origin"), ("user", "user-origin")):
        c, n = counts(data[tag], "FAUX", cond)
        labels.append(f"{NAMES[tag].split()[0]}, {nm}")
        rows_.append(c)
y = list(range(len(labels)))[::-1]
for yi, c in zip(y, rows_):
    left = 0
    for cat, color, hatch, txt in (("correction", "#4c72b0", "//", "Correction"),
                                   ("maintien", "#dd8452", "", "Maintenance"),
                                   ("autre/mixte", "#bbbbbb", "..", "Other/mixed")):
        v = c.get(cat, 0)
        if v:
            ax.barh(yi, v, left=left, color=color, hatch=hatch, edgecolor="black", linewidth=0.6,
                    label=txt)
            ax.text(left + v / 2, yi, str(v), ha="center", va="center", fontsize=7,
                    color="white" if cat == "correction" else "black")
        left += v
ax.set_yticks(y); ax.set_yticklabels(labels)
ax.set_xlim(0, 21); ax.set_xlabel("Replies to the 21 false claims")
h, l = ax.get_legend_handles_labels()
uniq = dict(zip(l, h))
fig.legend(uniq.values(), uniq.keys(), fontsize=6, frameon=False, ncol=3, loc="upper center")
fig.tight_layout(rect=[0, 0, 1, 0.9]); fig.savefig("figures/fig_cats.pdf"); plt.close(fig)

# Figure 2: correction rate (false) and false-rejection rate (true), Wilson 95% CI
fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.2), sharey=True)
for ax, verdict, title in ((axes[0], "FAUX", "False claims: correction rate"),
                           (axes[1], "VRAI", "True claims: false-rejection rate")):
    for j, tag in enumerate(data):
        for k, (cond, hatch, color) in enumerate((("assistant", "//", "#4c72b0"),
                                                  ("user", "", "#dd8452"))):
            c, n = counts(data[tag], verdict, cond)
            kk = c.get("correction", 0)
            lo, hi = wilson(kk, n)
            x = j + (k - 0.5) * 0.38
            ax.bar(x, 100 * kk / n, 0.36, color=color, hatch=hatch, edgecolor="black", linewidth=0.6,
                   label="Assistant-origin" if k == 0 else "User-origin")
            ax.errorbar(x, 100 * kk / n, yerr=[[100 * kk / n - 100 * lo], [100 * hi - 100 * kk / n]],
                        color="black", capsize=2, linewidth=0.8)
            ax.text(x, 100 * hi + 2, f"{100 * kk / n:.0f}%", ha="center", fontsize=7)
    ax.set_xticks(range(len(data))); ax.set_xticklabels([NAMES[t] for t in data])
    ax.set_title(title, fontsize=8); ax.set_ylim(0, 110)
axes[0].set_ylabel("% (Wilson 95% CI)")
h, l = axes[0].get_legend_handles_labels()
axes[0].legend(dict(zip(l, h)).values(), dict(zip(l, h)).keys(), fontsize=6, frameon=False,
               loc="upper right")
fig.tight_layout(); fig.savefig("figures/fig_rates.pdf"); plt.close(fig)
print("wrote figures/fig_cats.pdf, figures/fig_rates.pdf")
