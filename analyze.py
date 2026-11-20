"""Analysis of the annotated origin-condition results.

Usage:  python analyze.py results/annotated_llama.csv results/annotated_qwen.csv
Each CSV: id,condition,verdict,claim,reply,label,note   (condition = assistant|user,
verdict = FAUX|VRAI).  Writes results/tables.md and results/examples.md.
Seed: 42.
"""
import csv, sys, random, collections, math
import numpy as np
from scipy.stats import binomtest

CATS = ["correction", "maintien", "incertitude", "autre/mixte"]
ALIAS = {"maintaing": "maintien", "maintaining": "maintien", "maintaaining": "maintien",
         "maintenance": "maintien", "other": "autre/mixte", "autre": "autre/mixte",
         "mixte": "autre/mixte", "uncertain": "incertitude"}

def norm(x):
    x = x.strip().lower()
    return ALIAS.get(x, x)

def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    bad = [(r["id"], r["condition"], r["label"]) for r in rows if norm(r["label"]) not in CATS]
    if bad:
        sys.exit(f"{path}: labels non valides (corrige-les): {bad}")
    for r in rows:
        r["L"] = norm(r["label"])
    return rows

def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

def paired(rows, verdict):
    by = collections.defaultdict(dict)
    for r in rows:
        if r["verdict"] == verdict:
            by[r["id"]][r["condition"]] = r
    ids = [i for i, d in by.items() if len(d) == 2]
    return ids, by

def boot_ci(diffs, seed=42, B=10000):
    rng = np.random.default_rng(seed)
    d = np.array(diffs, float)
    m = [rng.choice(d, len(d)).mean() for _ in range(B)]
    return np.percentile(m, [2.5, 97.5])

def pct(k, n): return f"{k}/{n} ({100*k/n:.0f}%)" if n else "-"

def main():
    out, ex = [], []
    for path in sys.argv[1:]:
        tag = path.split("annotated_")[-1].replace(".csv", "")
        rows = load(path)
        out.append(f"\n## Modèle: {tag}\n")
        for v in ("FAUX", "VRAI"):
            ids, by = paired(rows, v)
            n = len(ids)
            out.append(f"### Affirmations {v} (n = {n} paires)\n")
            out.append("| Catégorie | assistant | user |\n|---|---|---|")
            for c in CATS:
                a = sum(by[i]["assistant"]["L"] == c for i in ids)
                u = sum(by[i]["user"]["L"] == c for i in ids)
                out.append(f"| {c} | {pct(a,n)} | {pct(u,n)} |")
            ca = [by[i]["assistant"]["L"] == "correction" for i in ids]
            cu = [by[i]["user"]["L"] == "correction" for i in ids]
            la, ha = wilson(sum(ca), n); lu, hu = wilson(sum(cu), n)
            b = sum(x and not y for x, y in zip(ca, cu))   # assistant only
            c_ = sum(y and not x for x, y in zip(ca, cu))  # user only
            diffs = [int(x) - int(y) for x, y in zip(ca, cu)]
            lo, hi = boot_ci(diffs)
            p = binomtest(b, b + c_, 0.5).pvalue if b + c_ else 1.0
            lab = "taux de correction" if v == "FAUX" else "taux de faux rejet"
            out.append(f"\n- {lab}: assistant {100*sum(ca)/n:.0f}% [IC95 Wilson {100*la:.0f}-{100*ha:.0f}], "
                       f"user {100*sum(cu)/n:.0f}% [{100*lu:.0f}-{100*hu:.0f}]")
            out.append(f"- différence assistant − user: {100*np.mean(diffs):+.0f} pts "
                       f"[IC95 bootstrap {100*lo:+.0f}, {100*hi:+.0f}]")
            out.append(f"- paires discordantes: assistant seul = {b}, user seul = {c_}; "
                       f"McNemar exact p = {p:.3f}")
            same = sum(by[i]["assistant"]["L"] == by[i]["user"]["L"] for i in ids)
            out.append(f"- même label dans les deux conditions: {same}/{n} paires")
            pat = collections.Counter((by[i]["assistant"]["L"], by[i]["user"]["L"]) for i in ids)
            out.append("- profils (assistant, user): " +
                       ", ".join(f"{a}/{u}: {k}" for (a, u), k in sorted(pat.items())) + "\n")
        # random examples, FAUX pairs
        rng = random.Random(42)
        ids, by = paired(rows, "FAUX")
        ex.append(f"\n## Exemples aléatoires ({tag}, seed 42)\n")
        for i in rng.sample(sorted(ids), min(5, len(ids))):
            ex.append(f"**id {i}** — claim: {by[i]['assistant']['claim']}")
            for c in ("assistant", "user"):
                r = by[i][c]
                ex.append(f"- *{c}* → **{r['L']}** : {r['reply'].strip()}  \n  note: {r['note'].strip()}")
            ex.append("")
    open("results/tables.md", "w", encoding="utf-8").write("\n".join(out))
    open("results/examples.md", "w", encoding="utf-8").write("\n".join(ex))
    print("\n".join(out)); print("\n-> results/tables.md, results/examples.md")

if __name__ == "__main__":
    main()
