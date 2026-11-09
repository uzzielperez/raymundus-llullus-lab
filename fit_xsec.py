"""
fit_xsec.py — v1: the amoeba.

Exercise: fit sigma(E) = A / E^2 to noisy e+e- -> mu+mu- cross-section data.
v1 is pure vibe coding: one function, no memory, no tests, no plan.
If it breaks, you re-paste the whole error and hope.
"""
import csv
import math
import random

random.seed(42)

# "measured" data: E [GeV], sigma [pb] — truth is A = 860 pb*GeV^2 + noise
DATA = []
for E in [2.0, 3.0, 4.5, 6.0, 8.0, 12.0, 20.0, 30.0]:
    sigma_true = 860.0 / E**2
    sigma_meas = sigma_true * random.uniform(0.85, 1.15)
    DATA.append((E, sigma_meas))


def fit():
    # "just fit it" — average of A_i = sigma_i * E_i^2
    vals = []
    for E, sigma in DATA:
        vals.append(sigma * E * E)
    A = sum(vals) / len(vals)
    print("A =", A)
    print("done")


if __name__ == "__main__":
    fit()
