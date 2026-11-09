"""
fit_xsec.py — v2: the nerve net (router + handlers), still no memory.

Same task. Now the code is split into small sharp handlers (sense / fit / report)
— like the jellyfish nerve net: roles exist, but there is still no head,
no plan, and nothing written down between runs.
"""
import math
import random

random.seed(42)


def read_data():
    """handler: sense — produce the dataset (truth A = 860 pb*GeV^2 + noise)."""
    data = []
    for E in [2.0, 3.0, 4.5, 6.0, 8.0, 12.0, 20.0, 30.0]:
        sigma_true = 860.0 / E**2
        sigma_meas = sigma_true * random.uniform(0.85, 1.15)
        data.append((E, sigma_meas))
    return data


def fit_a(data):
    """handler: decide — unweighted mean of A_i (still a vibe fit)."""
    vals = [sigma * E * E for E, sigma in data]
    return sum(vals) / len(vals)


def report(a):
    """handler: act — print. Nothing is kept."""
    print("A =", a)


def main():
    data = read_data()
    a = fit_a(data)
    report(a)


if __name__ == "__main__":
    main()
