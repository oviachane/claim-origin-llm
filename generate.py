import argparse, json, os, random
from datasets import load_dataset
from openai import OpenAI

SYSTEM = "Answer the question in one short, complete factual sentence."

p = argparse.ArgumentParser()
p.add_argument("--model", required=True)
p.add_argument("--base-url", default="http://localhost:11434/v1")
p.add_argument("--n", type=int, default=300)
p.add_argument("--seed", type=int, default=42)
p.add_argument("--out", required=True)
a = p.parse_args()

client = OpenAI(base_url=a.base_url, api_key="ollama")
ds = load_dataset("google-research-datasets/nq_open", split="validation")
idx = list(range(len(ds)))
random.Random(a.seed).shuffle(idx)
idx = idx[: a.n]

done = set()
if os.path.exists(a.out):
    with open(a.out) as f:
        done = {json.loads(l)["id"] for l in f}

with open(a.out, "a") as f:
    for k, i in enumerate(idx):
        if i in done:
            continue
        q = ds[i]["question"].strip()
        if not q.endswith("?"):
            q += "?"
        r = client.chat.completions.create(
            model=a.model,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": q}],
            temperature=0, seed=a.seed, max_tokens=100,
        )
        rec = {"id": i, "model": a.model, "question": q,
               "response": r.choices[0].message.content.strip(),
               "references": ds[i]["answer"],
               "temperature": 0, "seed": a.seed}
        f.write(json.dumps(rec) + "\n")
        f.flush()
        print(k + 1, "/", len(idx), flush=True)
