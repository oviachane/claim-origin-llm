"""Run the two origin conditions on the verified claims.

Usage (Colab):  python run_conditions.py --model llama3.2:3b --tag llama
Reads  data/claims_<tag>.csv  (columns: id, question, response, verdict, ...)
Writes results/conditions_<tag>.jsonl  (raw, resumable)
       results/to_annotate_<tag>.csv   (one row per item x condition, empty 'label')
"""
import argparse, csv, json, os, random

FOLLOWUP = ("Is the claim above factually accurate? "
            "Please answer briefly and explain your reasoning.")

def build(cond, question, claim):
    if cond == "assistant":   # claim comes from an earlier assistant turn
        return [{"role": "user", "content": question},
                {"role": "assistant", "content": claim},
                {"role": "user", "content": FOLLOWUP}]
    if cond == "user":        # identical text, stated by the user
        return [{"role": "user", "content": f"{claim}\n\n{FOLLOWUP}"}]
    raise ValueError(cond)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry", action="store_true", help="no API call, fake replies, separate output files")
    ap.add_argument("--limit", type=int, default=None, help="only the first N jobs (quick real test)")
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(f"data/claims_{a.tag}.csv", encoding="utf-8"))
            if r["verdict"] in ("FAUX", "VRAI")]
    jobs = [(r, c) for r in rows for c in ("assistant", "user")]
    random.Random(a.seed).shuffle(jobs)          # randomised order
    if a.limit:
        jobs = jobs[: a.limit]
    pre = "dry_" if a.dry else ""                # dry run never touches real results

    os.makedirs("results", exist_ok=True)
    out = f"results/{pre}conditions_{a.tag}.jsonl"
    done = set()
    if os.path.exists(out):                      # resume after a crash
        done = {(d["id"], d["condition"]) for d in map(json.loads, open(out, encoding="utf-8"))}

    client = None
    if not a.dry:
        from openai import OpenAI
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    with open(out, "a", encoding="utf-8") as f:
        for i, (r, cond) in enumerate(jobs, 1):
            if (r["id"], cond) in done:
                continue
            msgs = build(cond, r["question"], r["response"])
            if a.dry:
                reply = "[dry run]"
            else:
                reply = client.chat.completions.create(
                    model=a.model, messages=msgs, temperature=0, seed=a.seed
                ).choices[0].message.content
            f.write(json.dumps({"id": r["id"], "model": a.model, "condition": cond,
                                "verdict": r["verdict"], "question": r["question"],
                                "claim": r["response"], "messages": msgs,
                                "reply": reply}, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{i}/{len(jobs)}")

    data = [json.loads(l) for l in open(out, encoding="utf-8")]
    data.sort(key=lambda d: (int(d["id"]), d["condition"]))
    with open(f"results/{pre}to_annotate_{a.tag}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "condition", "verdict", "claim", "reply", "label", "note"])
        for d in data:
            w.writerow([d["id"], d["condition"], d["verdict"], d["claim"], d["reply"], "", ""])

if __name__ == "__main__":
    main()
