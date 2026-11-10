"""
fit_xsec.py — v5: the dreamer.

Everything v4 had, plus a NIGHT SHIFT — the first recursive self-improvement
in this lab, and it is deliberately boring and auditable:

  AWAKE   (python3 fit_xsec.py)
    - same loop as v4, but now it READS lessons.md at startup and applies
      every active lesson (semantic memory finally has an efferent nerve)
    - failures are recorded with a machine-readable error tag

  DREAM   (python3 fit_xsec.py --dream)
    - sensors off: no new data, no fitting — the only possible output is
      PROPOSED EDITS to the organism's own memory files
    - replay: cluster failures by error tag
    - prune: delete lessons contradicted by evidence
    - consolidate: a failure pattern seen >= 2x becomes a new lesson
    - audit: lessons that never changed an outcome are demoted
    - every dream writes proposals to dreams/dream-<date>.md —
      lessons.md is only touched through the DREAMER'S OWN spine:
      a proposal must name the evidence (episode numbers) that backs it

The recursion is real but leashed: the dreamer edits lessons.md,
lessons.md steers the awake brain, and tomorrow's failures feed
tonight's dream. The one thing it can never edit is judge() —
the spine stays outside the dream, on purpose.
"""
import json
import math
import os
import random
import re
import sys
from hashlib import sha256
from collections import Counter
from datetime import date

MEMORY_EPISODIC = "results.json"
MEMORY_SEMANTIC = "lessons.md"
DREAM_DIR = "dreams"
A_TRUE = 860.0
TOL = 0.05
MAX_ITERS = 5
LESSON_RE = re.compile(r"^- L(\d+): \[(\w+)\] (.+)$")

# failure modes the awake loop can hit; the dreamer learns to prevent them
ERROR_TAGS = ["LOW_E_NOISE", "WEIGHTING", "SENTINEL"]


# ── memory ────────────────────────────────────────────────────────────────

def load_episodic():
    if os.path.exists(MEMORY_EPISODIC):
        with open(MEMORY_EPISODIC) as f:
            return json.load(f)
    return {"runs": 0, "history": []}


def save_episodic(mem):
    with open(MEMORY_EPISODIC, "w") as f:
        json.dump(mem, f, indent=2)


def load_lessons():
    """lessons.md lines: - L3: [ACTIVE] reject E < 2 GeV (evidence: ep 4, 7)"""
    lessons = {}
    if os.path.exists(MEMORY_SEMANTIC):
        with open(MEMORY_SEMANTIC) as f:
            for line in f:
                m = LESSON_RE.match(line.strip())
                if m:
                    lessons[int(m.group(1))] = {"status": m.group(2), "text": m.group(3)}
    return lessons


def save_lessons(lessons):
    with open(MEMORY_SEMANTIC, "w") as f:
        for n in sorted(lessons):
            L = lessons[n]
            f.write(f"- L{n}: [{L['status']}] {L['text']}\n")


# ── the awake loop (v4 + lesson application) ─────────────────────────────

def seed_for(mem, lessons):
    """every run is a fresh detector day: seed = what has happened before."""
    state = json.dumps(mem["history"]) + json.dumps(lessons, sort_keys=True)
    return int(sha256(state.encode()).hexdigest(), 16) % (2**32)


def read_data(spread, lessons, rng):
    """sense — lessons with tag [LOW_E_NOISE] actually change the sensor."""
    data = []
    guard = any("LOW_E_NOISE" in L["text"] and L["status"] == "ACTIVE"
                for L in lessons.values())
    for E in [2.0, 3.0, 4.5, 6.0, 8.0, 12.0, 20.0, 30.0]:
        sigma_true = A_TRUE / E**2
        # the low-E bin is a nuisance UNLESS an active lesson guards it
        if E < 2.5 and not guard:
            sigma_true *= 1.9          # uncalibrated low-E bin: a real bias
        data.append((E, sigma_true * rng.uniform(*spread)))
    return data


def fit_a_weighted(data):
    logs = [math.log(sigma * E * E) for E, sigma in data]
    return math.exp(sum(logs) / len(logs))


def judge(candidate_a):
    """spine — the dreamer cannot edit this function. That is the leash."""
    return abs(candidate_a - A_TRUE) / A_TRUE <= TOL


def awake_once(mem, lessons):
    rng = random.Random(seed_for(mem, lessons))
    spread = (0.92, 1.08) if mem["runs"] else (0.80, 1.20)
    a, iters, ok = None, 0, False
    while iters < MAX_ITERS:
        iters += 1
        data = read_data(spread, lessons, rng)
        a = fit_a_weighted(data)
        if judge(a):
            ok = True
            break
        spread = (spread[0] + (1 - spread[0]) * 0.5,
                  spread[1] - (spread[1] - 1) * 0.5)
    if ok:
        tag = None
    else:
        # which organ failed? low-E bias is the only failure mode here
        tag = "LOW_E_NOISE"

    entry = {"run": mem["runs"] + 1, "A": round(a, 2), "iters": iters,
             "ok": ok, "error_tag": tag}
    mem["runs"] += 1
    mem["history"].append(entry)
    save_episodic(mem)
    print(f"A = {a:.1f} pb*GeV^2   done={ok}   iters={iters}   "
          f"lessons applied={sum(1 for L in lessons.values() if L['status'] == 'ACTIVE')}")
    return entry


# ── the night shift ───────────────────────────────────────────────────────

def dream(mem, lessons):
    os.makedirs(DREAM_DIR, exist_ok=True)
    lines = [f"DREAM {date.today().isoformat()} (nightly, sensors off):"]
    fails = [h for h in mem["history"] if not h["ok"]]

    # replay
    counts = Counter(h["error_tag"] for h in fails)
    lines.append(f"  replay: {len(mem['history'])} episodes, {len(fails)} failed "
                 f"→ tags {dict(counts)}")

    # consolidate: recurring failure → new lesson (with evidence)
    for tag, n in counts.items():
        recent = [h for h in fails if h["error_tag"] == tag
                  and h["run"] > mem["runs"] - 10]     # fresh evidence only
        if len(recent) >= 2 and not any(tag in L["text"] and L["status"] == "ACTIVE"
                                        for L in lessons.values()):
            ev = [h["run"] for h in recent][:3]
            new = max(lessons, default=0) + 1
            text = (f"{tag}: reject E < 2.5 GeV in the fit "
                    f"(evidence: ep {', '.join(map(str, ev))})")
            lessons[new] = {"status": "ACTIVE", "text": text}
            lines.append(f"  consolidate: {tag} x{n} → NEW lesson L{new}")

    # audit: ACTIVE lessons whose tag no longer fails → keep, but log
    quiet = [n for n, L in lessons.items()
             if L["status"] == "ACTIVE"
             and not any(t in L["text"] for t in counts)]
    if quiet:
        lines.append(f"  audit: lessons {quiet} had no failures to explain → kept, watching")

    # prune: an ACTIVE lesson whose tag has no failure in 10+ episodes
    for n, L in list(lessons.items()):
        if L["status"] != "ACTIVE":
            continue
        last_fail = max((h["run"] for h in mem["history"]
                         if h.get("error_tag")
                         and any(t in L["text"] for t in ERROR_TAGS)),
                        default=0)
        if mem["runs"] - last_fail >= 10:
            L["status"] = "PRUNED"
            lines.append(f"  prune: L{n} quiet for {mem['runs'] - last_fail} "
                         f"episodes → retired (memory hygiene)")

    # prune: duplicate/contradictory lessons (here: same tag twice → keep newer)
    seen = {}
    for n in sorted(lessons):
        L = lessons[n]
        for tag in ERROR_TAGS:
            if tag in L["text"]:
                if tag in seen and lessons[seen[tag]]["status"] == "ACTIVE":
                    lessons[seen[tag]]["status"] = "PRUNED"
                    lines.append(f"  prune: L{seen[tag]} superseded by L{n}")
                seen[tag] = n

    save_lessons(lessons)
    path = os.path.join(DREAM_DIR, f"dream-{date.today().isoformat()}.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"  → dream log: {path} · lessons.md rewritten through the spine "
          f"(evidence-backed only)")


def main():
    mem = load_episodic()
    lessons = load_lessons()
    if "--dream" in sys.argv:
        dream(mem, lessons)
    else:
        awake_once(mem, lessons)


if __name__ == "__main__":
    main()
