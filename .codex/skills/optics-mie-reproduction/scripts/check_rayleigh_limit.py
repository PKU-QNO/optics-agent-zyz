"""Layer 1.4 verifier: Rayleigh limit Q_sca proportional to x^4 at small x.

Fits log-log slope of Q_sca vs x over a small-x range; expects slope = 4.
Imports from reproduction_test/mie/code/. Exits 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import sys
import numpy as np

CODE_DIR = "reproduction_test/mie/code"
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

EXPECTED_SLOPE = 4.0
SLOPE_TOL = 0.01


def main() -> int:
    try:
        from scattering import compute_Q_sca  # type: ignore
    except ImportError as e:
        print(f"FAIL: implementation not found ({e}). Run after stage 1 code is written.")
        return 2

    xs = np.logspace(-3, -1, 20)  # small x regime
    m = 1.5 + 0.0j
    try:
        qsca = np.array([compute_Q_sca(m=m, x=x) for x in xs])
    except Exception as e:
        print(f"FAIL: compute_Q_sca raised {e}")
        return 1

    log_x = np.log10(xs)
    log_q = np.log10(qsca)
    slope, _ = np.polyfit(log_x, log_q, 1)

    if abs(slope - EXPECTED_SLOPE) < SLOPE_TOL:
        print(f"PASS rayleigh_limit: fitted slope {slope:.4f} (expected {EXPECTED_SLOPE}, tol {SLOPE_TOL})")
        return 0
    print(f"FAIL rayleigh_limit: fitted slope {slope:.4f}, expected {EXPECTED_SLOPE} +/- {SLOPE_TOL}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
