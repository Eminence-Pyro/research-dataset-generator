"""
research_engine/generators/sample_size.py
Stage 3 / Stage 4 — Research Configuration Engine

Sample size calculators for descriptive research.

Three formulas are provided — each is the standard for a different
research context:

    cochran(p, e, z)         — infinite population (Cochran 1977)
    yamane(N, e)              — finite population (Yamane 1967)
    krejcie_morgan(N)         — lookup table approximation (Krejcie & Morgan 1970)
    finite_correction(n, N)  — apply finite population correction to a Cochran n

All functions return an integer (the recommended minimum sample size).

Example
-------
    >>> from research_engine.generators.sample_size import cochran, yamane
    >>> cochran()              # default p=0.5, e=0.05, z=1.96
    385
    >>> yamane(500)            # finite population of 500
    222
    >>> cochran(p=0.5, e=0.05, finite_n=1200)   # with finite correction
    291
"""
from __future__ import annotations
import math


def cochran(
    p:        float = 0.5,
    e:        float = 0.05,
    z:        float = 1.96,
    finite_n: int   | None = None,
) -> int:
    """
    Cochran (1977) sample size formula for proportions.

    n = (Z² × p × q) / e²

    Parameters
    ----------
    p        : estimated proportion of attribute (0.5 = maximum variance, most conservative)
    e        : acceptable margin of error (0.05 = ±5%)
    z        : z-score for desired confidence level (1.96 = 95%, 2.576 = 99%)
    finite_n : if the population is finite, apply finite population correction

    Returns
    -------
    int — minimum required sample size
    """
    if not (0 < p < 1):
        raise ValueError(f"p must be between 0 and 1 (exclusive). Got {p}")
    if not (0 < e < 1):
        raise ValueError(f"e must be between 0 and 1 (exclusive). Got {e}")
    q = 1 - p
    n = (z ** 2 * p * q) / (e ** 2)
    if finite_n:
        n = finite_correction(math.ceil(n), finite_n)
    return math.ceil(n)


def yamane(N: int, e: float = 0.05) -> int:
    """
    Yamane (1967) simplified formula for finite populations.

    n = N / (1 + N × e²)

    Parameters
    ----------
    N : total population size
    e : acceptable margin of error (0.05 = ±5%)

    Returns
    -------
    int — minimum required sample size
    """
    if N <= 0:
        raise ValueError(f"N must be a positive integer. Got {N}")
    if not (0 < e < 1):
        raise ValueError(f"e must be between 0 and 1 (exclusive). Got {e}")
    n = N / (1 + N * (e ** 2))
    return math.ceil(n)


def krejcie_morgan(N: int) -> int:
    """
    Krejcie & Morgan (1970) sample size table approximation.

    Uses the formula underlying the original published table:
    n = χ²Np(1-p) / (d²(N-1) + χ²p(1-p))

    where χ²=3.841 (df=1, α=0.05), p=0.5, d=0.05

    Parameters
    ----------
    N : population size

    Returns
    -------
    int — recommended sample size
    """
    if N <= 0:
        raise ValueError(f"N must be a positive integer. Got {N}")
    chi2 = 3.841    # chi-square for df=1, α=0.05
    p    = 0.5
    d    = 0.05
    n    = (chi2 * N * p * (1 - p)) / (d**2 * (N - 1) + chi2 * p * (1 - p))
    return math.ceil(n)


def finite_correction(n: int, N: int) -> int:
    """
    Apply the finite population correction factor to a Cochran sample size.

    n_adj = n / (1 + (n - 1) / N)

    Parameters
    ----------
    n : initial (infinite population) sample size
    N : total population size

    Returns
    -------
    int — adjusted sample size
    """
    if N <= 0 or n <= 0:
        raise ValueError("Both n and N must be positive integers.")
    if n >= N:
        return N
    n_adj = n / (1 + (n - 1) / N)
    return math.ceil(n_adj)


def recommend(
    N:          int | None = None,
    p:          float      = 0.5,
    e:          float      = 0.05,
    confidence: float      = 0.95,
) -> dict:
    """
    Run all applicable formulas and return a comparison dict.

    Parameters
    ----------
    N          : population size (None = infinite/unknown)
    p          : estimated proportion (default 0.5, most conservative)
    e          : margin of error (default 0.05 = ±5%)
    confidence : confidence level (0.90, 0.95, or 0.99)

    Returns
    -------
    dict with keys: cochran, yamane (if N known), krejcie_morgan (if N known),
                    recommended, formula_used, parameters
    """
    z_map = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_map.get(confidence, 1.96)

    result: dict = {
        "parameters": {"N": N, "p": p, "e": e, "confidence": confidence, "z": z}
    }

    n_cochran = cochran(p=p, e=e, z=z, finite_n=N)
    result["cochran"] = n_cochran

    if N:
        result["yamane"]         = yamane(N, e)
        result["krejcie_morgan"] = krejcie_morgan(N)
        result["recommended"]    = result["yamane"]
        result["formula_used"]   = "Yamane (1967) — finite population"
    else:
        result["recommended"]  = n_cochran
        result["formula_used"] = "Cochran (1977) — infinite / unknown population"

    return result
