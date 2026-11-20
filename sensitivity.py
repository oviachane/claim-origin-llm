"""Sensitivity analysis: treat a rejection that rests only on 'I could not find any
information' (no positive statement about the correct fact) as NOT a correction.

Usage: python sensitivity.py results/annotated_llama.csv results/annotated_qwen.csv
The (model, id, condition) replies below were identified by reading the replies;
check them against the annotated files before reporting.
"""
import csv, sys, collections
from scipy.stats import binomtest

ABSENCE = {  # evidence-absence rejections, by file tag
    "llama": {("1602","assistant"), ("1602","user"), ("1689","assistant"), ("1689","user"),
              ("1772","assistant"), ("2239","assistant"), ("2239","user"),
              ("3302","assistant"), ("3078","assistant")},
    "qwen": set(),
}
ALIAS = {"maintaing":"maintien","maintaining":"maintien","maintaaining":"maintien","other":"autre/mixte"}
def norm(x): x = x.strip().lower(); return ALIAS.get(x, x)

for path in sys.argv[1:]:
    tag = path.split("annotated_")[-1].replace(".csv", "")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    by = collections.defaultdict(dict)
    for r in rows:
        if r["verdict"] == "FAUX": by[r["id"]][r["condition"]] = r
    vr = [r for r in rows if r["verdict"] == "VRAI" and r["condition"] == "assistant"]
    for alt in (False, True):   # false-rejection rate on true claims, assistant-origin
        k = sum(norm(r["label"]) == "correction" and not (alt and (r["id"], "assistant") in ABSENCE[tag]) for r in vr)
        print(f"{tag} {'strict-evidence' if alt else 'main'} TRUE claims, assistant-origin false rejections: {k}/{len(vr)}")
    def cor(i, cond, alt):
        r = by[i][cond]
        return norm(r["label"]) == "correction" and not (alt and (i, cond) in ABSENCE[tag])
    for alt in (False, True):
        a = [cor(i, "assistant", alt) for i in by]; u = [cor(i, "user", alt) for i in by]
        b = sum(x and not y for x, y in zip(a, u)); c = sum(y and not x for x, y in zip(a, u))
        p = binomtest(b, b + c, .5).pvalue if b + c else 1.0
        print(f"{tag} {'strict-evidence' if alt else 'main'}: assistant {sum(a)}/{len(a)}, "
              f"user {sum(u)}/{len(u)}, A-only {b}, U-only {c}, McNemar p={p:.3f}")
