"""
fit_xsec.py — v4: the CNS (engineered agent).

Everything v3 had, plus:
  PROPRIOCEPTION — the loop senses its own cost: iterations, budget
  JUDGE OF DONE  — a separate deterministic call the actor cannot bribe
  MEMORY LAYERS  — episodic (runs log) + semantic (lessons.md, human-readable)
  LOOP           — sense -> decide -> act -> verify -> remember, until done

This is the state people leave the workshop with: same physics problem,
but the code now has a nervous system.
"""
import json
import math
import os
import random

MEMORY_EPISODIC = "results.json"
MEMORY_SEMANTIC = "lessons.md"
A_TRUE = 860.0
TOL = 0.05
MAX_ITERS = 5


def read_data(prior_scale):
    random.seed(42)
    data = []
    for E in [2.0, 3.0, 4.5, 6.0, 8.0, 12.0, 20.0, 30.0]:
        sigma_true = A_TRUE / E**2
        data.append((E, sigma_true * random.uniform(*prior_scale)))
    return data


def load_episodic():
    if os.path.exists(MEMORY_EPISODIC):
        with open(MEMORY_EPISODIC) as f:
            return json.load(f)
    return {"runs": 0, "history": []}


def append_episodic(mem, entry):
    mem["runs"] += 1
    mem["history"].append(entry)
    with open(MEMORY_EPISODIC, "w") as f:
        json.dump(mem, f, indent=2)


def append_semantic(text):
    with open(MEMORY_SEMANTIC, "a") as f:
        f.write(text + "\n")


def fit_a_weighted(data):
    logs = [math.log(sigma * E * E) for E, sigma in data]
    return math.exp(sum(logs) / len(logs))


def judge(goal_a, candidate_a):
    """judge of done — deterministic, separate from whoever produced candidate_a."""
    return abs(candidate_a - goal_a) / goal_a <= TOL


def main():
    mem = load_episodic()
    spread = (0.92, 1.08) if mem["runs"] else (0.85, 1.15)

    a = None
    iters = 0
    while iters < MAX_ITERS:                      # the loop
        iters += 1
        data = read_data(spread)                  # sense
        a = fit_a_weighted(data)                  # decide (brain)
        if judge(A_TRUE, a):                      # judge (spine, not the actor)
            break
        spread = (                              # reflex: tighten, re-sense
            spread[0] + (1 - spread[0]) * 0.5,
            spread[1] - (spread[1] - 1) * 0.5,
        )

    ok = judge(A_TRUE, a)
    print(f"A = {a:.1f} pb*GeV^2   done={ok}   iters={iters}   "
          f"prior runs={mem['runs']}")

    append_episodic(mem, {"run": mem["runs"] + 1, "A": round(a, 2),
                          "iters": iters, "ok": ok})
    append_semantic(f"- run {mem['runs'] + 1}: A={a:.1f}, iters={iters}, "
                    f"budget used {iters}/{MAX_ITERS}")


if __name__ == "__main__":
    main()
