# Lab · Fit a particle-physics cross-section, grow a nervous system

Hands-on track of the deck **Agents: From Amoeba to Nervous System**
(Raymundus Llullus program).

One physics problem, four organisms. Each state is a **git tag** — the full
session history *is* the curriculum.

| Tag | Organism | What's new |
|-----|----------|-----------|
| `v1-amoeba` | blob | vibe-coded fit: no tests, no memory |
| `v2-nerve-net` | jellyfish | handlers with roles — still no memory |
| `v3-head` | head | brain (log-space fit) + spine (`verify()`) + reflex + `results.json` |
| `v4-cns` | engineered agent | loop, judge-of-done, episodic + semantic memory, budget |
| `v5-dreamer` | the night shift | offline replay → lessons the awake loop **reads back** → prune → relapse → re-learn |

## The physics

`e⁺e⁻ → μ⁺μ⁻` cross section follows `σ(E) = A / E²`.
You have 8 noisy measurements; fit `A` (truth: 860 pb·GeV²).
The *fit* is trivial — the *point* is watching what code with organs does
differently from code that is a blob.

## Requirements

- Python 3.10+ (stdlib only — no pip install needed)
- git
- **opencode** — any agentic CLI works (opencode, Claude Code, Codex CLI,
  Cursor agent); instructions assume opencode. No git? See
  "No git? The fallback" below.

## Get the lab

```bash
git clone https://github.com/uzzielperez/raymundus-llullus-lab.git
cd raymundus-llullus-lab
git tag -l          # v1-amoeba  v2-nerve-net  v3-head  v4-cns
```

## The session (≈60–90 min)

### Act 1 — the amoeba (10 min)

```bash
git checkout v1-amoeba
python3 fit_xsec.py
```

Ask your agent (opencode): *"make this fit better."*
Watch it rewrite the whole file, change the architecture, forget your
constraint from two messages ago. **This is the baseline. Feel it.**

### Act 2 — the nerve net (15 min)

```bash
git checkout v2-nerve-net
git diff v1-amoeba v2-nerve-net
```

Roles exist (`read_data` / `fit_a` / `report`) — but run it twice:
identical output, nothing learned. Prompt-stuffing "remember your last run!"
into the file changes nothing. There is no organ for it.

### Act 3 — grow the head (25 min, hands-on)

```bash
git checkout v3-head
rm -f results.json
python3 fit_xsec.py        # first run: memory=none
python3 fit_xsec.py        # second run: memory=read → tighter calibration
cat results.json
```

Now **you** do it with the agent, from the v2 state:

1. **BRAIN** — prompt: *"replace the unweighted mean with a log-space fit;
   justify why for 1/E² data."* (The agent must explain — that's your
   attention-budget check.)
2. **SPINE** — prompt: *"add a deterministic verify(A) against the known
   truth, ±10%. No LLM judgment in this function."*
3. **REFLEX** — prompt: *"if verify fails, apply a correction factor
   sqrt(A_true/A) — no re-planning."*
4. **MEMORY** — prompt: *"write results.json with runs, last_A, lesson.
   On startup, if it exists, tighten the noise model."*

Run it twice. The second run is measurably closer to truth.
**The code improved because it remembered — not because the model changed.**

### Act 4 — the CNS (20 min, hands-on)

```bash
git checkout v4-cns
rm -f results.json lessons.md
python3 fit_xsec.py && python3 fit_xsec.py
cat lessons.md
```

Note the two memories with different lifetimes (`results.json` episodic,
`lessons.md` semantic) and the `judge()` that the fitting code cannot bribe.

**Final exercise:** from `v3-head`, prompt your agent to reach `v4-cns`
*without* being told the design — only the checklist from the deck
(loop / spine / reflexes / organs / proprioception / judge). Compare its
solution to `git diff v3-head v4-cns`. Differences are the discussion.

### Act 5 — the dreamer (20 min, the finale)

```bash
git checkout v5-dreamer
rm -f results.json lessons.md
python3 fit_xsec.py        # x3 — all FAIL: an uncalibrated low-E bin biases A
python3 fit_xsec.py --dream
python3 fit_xsec.py        # passes on iteration 1 — the dream is now a sense organ
```

The dream (`--dream`) never touches the data: it replays failures,
**consolidates** a recurring error tag into an evidence-backed lesson,
and the next awake run *reads that lesson and guards the bad bin*.
Then the long game:

```bash
for i in $(seq 12); do python3 fit_xsec.py > /dev/null; done
python3 fit_xsec.py --dream     # prune: lesson quiet for 12 episodes → retired
python3 fit_xsec.py             # RELAPSE — the bias is back
python3 fit_xsec.py --dream     # the dream re-learns, from fresh evidence
```

That relapse is the point: memory hygiene is not free, and the
dreamer is not a one-time patch — it is a **metabolism**.
Note what the dreamer can never edit: `judge()`. The spine sits
outside the dream, on purpose (deck Act 8, honesty slide).

## No git? The fallback

- **GitHub Desktop / GitLab** — same thing with buttons.
- **No git at all:** the four states are also plain files:
  `states/v1.py states/v2.py states/v3.py states/v4.py`.
  Copy one to `fit_xsec.py`, diff by eye or with `diff -u`.
- **No terminal agent:** use any chat agent with copy-paste —
  you are the spinal cord; it's slower but the lesson survives.

## Honesty box

- `A_TRUE` is used by the *verifier* — in research you'd verify against
  control channels or a second detector, not truth. Same organ, different signal.
- The "learning" in v3/v4 is scripted calibration tightening, not magic —
  that's the point: **memory + loop + verifier = improvement, no retraining.**
- `random.seed(42)` keeps the workshop deterministic. Remove it and watch
  the reflex actually earn its keep.
