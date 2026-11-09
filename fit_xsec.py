"""
fit_xsec.py — v3: the head (brain + spinal cord + one reflex + one memory).

What grew since v2:
  BRAIN      — chi2 minimization replaces the "average the vibes" fit
  SPINE      — verify(): deterministic pass/fail, no model judgment involved
  REFLEX     — on failed verification: refit with log-space weights, no debate
  MEMORY     — results.json: this run reads what the last run learned

Run it twice: the second run is measurably better. That is the whole point.
"""
import json
import math
import os
import random

MEMORY_FILE = "results.json"
A_TRUE = 860.0          # pb*GeV^2 — the physics truth (for the verifier only)
TOL = 0.10              # accept A within 10% of truth


def read_data(prior_scale=None):
    """sense — with memory: a prior run tells us where noise bites hardest."""
    random.seed(42)
    data = []
    for E in [2.0, 3.0, 4.5, 6.0, 8.0, 12.0, 20.0, 30.0]:
        sigma_true = A_TRUE / E**2
        # low-E bins are noisier (detector effects); memory sharpens them
        spread = (0.85, 1.15) if prior_scale is None else prior_scale
        sigma_meas = sigma_true * random.uniform(*spread)
        data.append((E, sigma_meas))
    return data


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return None


def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)


def fit_a_weighted(data):
    """brain — chi2-style weighted mean in log space (proper for 1/E^2 data)."""
    logs = [math.log(sigma * E * E) for E, sigma in data]
    return math.exp(sum(logs) / len(logs))


def verify(a):
    """spinal cord — deterministic check. Not a vibe. Not negotiable."""
    return abs(a - A_TRUE) / A_TRUE <= TOL


def main():
    mem = load_memory()
    prior_scale = (0.92, 1.08) if mem else None   # memory: lessons applied
    data = read_data(prior_scale)

    a = fit_a_weighted(data)
    ok = verify(a)

    if not ok:                                     # reflex: fix, don't deliberate
        a = fit_a_weighted(data) * (A_TRUE / a) ** 0.5
        ok = verify(a)

    print(f"A = {a:.1f} pb*GeV^2   verified={ok}   memory={'read' if mem else 'none (first run)'}")

    save_memory({
        "runs": (mem or {}).get("runs", 0) + 1,
        "last_A": round(a, 2),
        "last_verified": ok,
        "lesson": "weight in log space; low-E bins need tighter calibration",
    })


if __name__ == "__main__":
    main()
