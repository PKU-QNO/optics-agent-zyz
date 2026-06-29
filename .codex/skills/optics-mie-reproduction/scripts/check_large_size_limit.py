"""Layer 1.5 verifier: large-size extinction paradox Q_ext -> 2 at large x.

Checks Q_ext over a large-x range; expects |Q_ext - 2| < 0.05 for x > 50.
Imports from reproduction_test/mie/code/. Exits 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import sys
import numpy as np

CODE_DIR = "reproduction_test/mie/code"
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

TARGET = 2.0
TOL = 0.05
X_MIN = 50.0


def main() -> int:
    try:
        from scattering import compute_Q_ext  # type: ignore
    except ImportError as e:
        print(f"FAIL: implementation not found ({e}). Run after stage 1 code is written.")
        return 2

    xs = np.array([50.0, 80.0, 120.0, 200.0])
    m = 1.5 + 0.0j
    try:
        qext = np.array([compute_Q_ext(m=m, x=x) for x in xs])
    except Exception as e:
        print(f"FAIL: compute_Q_ext raised {e}")
        return 1

    deviations = np.abs(qext - TARGET)
    max_dev = float(np.max(deviations))
    worst_x = float(xs[int(np.argmax(deviations))])

    if max_dev < TOL:
        print(f"PASS large_size_limit: max |Q_ext - 2| {max_dev:.4f} at x={worst_x} (tol {TOL})")
        return 0
    print(f"FAIL large_size_limit: max |Q_ext - 2| {max_dev:.4f} at x={worst_x}, tol {TOL}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
