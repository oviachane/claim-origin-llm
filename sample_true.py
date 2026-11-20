import json, re, string, sys, csv, random

def norm(s):
    s = s.lower()
    s = "".join(c for c in s if c not in string.punctuation)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())

def correct(resp, refs):
    r = norm(resp)
    return any(norm(x) in r for x in refs)

inp, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
rows = [json.loads(l) for l in open(inp)]
ok = [r for r in rows if correct(r["response"], r["references"])]
random.Random(42).shuffle(ok)
ok = ok[:n]
print(f"{len(ok)} vrais tirés sur {len(rows)}")

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "model", "question", "response", "references",
                "verdict", "source", "topic", "rationale"])
    for r in ok:
        w.writerow([r["id"], r["model"], r["question"], r["response"],
                    " | ".join(r["references"]), "", "", "", ""])
