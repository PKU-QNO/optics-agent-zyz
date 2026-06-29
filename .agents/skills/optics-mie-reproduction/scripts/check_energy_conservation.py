"""Layer 1.1 verifier: energy conservation C_ext = C_sca + C_abs.

Imports from reproduction_test/mie/code/. Fails with a clear message if the
implementation is not yet present. Exits 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import sys
import numpy as np

CODE_DIR = "reproduction_test/mie/code"
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

TOL_REL = 1e-10


def main() -> int:
    try:
        from scattering import compute_cross_sections  # type: ignore
    except ImportError as e:
        print(f"FAIL: implementation not found ({e}). Run after stage 1 code is written.")
        return 2

    # Sweep a representative parameter range: dielectric and metal, small and large x.
    test_cases = [
        {"m": 1.5 + 0.0j, "x": 1.0, "label": "dielectric x=1"},
        {"m": 1.5 + 0.1j, "x": 1.0, "label": "lossy dielectric x=1"},
        {"m": 0.05 + 3.0j, "x": 2.0, "label": "metal x=2"},
        {"m": 1.5 + 0.0j, "x": 20.0, "label": "dielectric x=20"},
    ]

    max_err = 0.0
    worst = ""
    for c in test_cases:
        try:
            cext, csca, cabs = compute_cross_sections(m=c["m"], x=c["x"])
        except Exception as e:
            print(f"FAIL: compute_cross_sections raised {e} for {c['label']}")
            return 1
        err = abs(cext - (csca + cabs))
        rel = err / max(abs(cext), 1e-30)
        if rel > max_err:
            max_err = rel
            worst = c["label"]

    if max_err < TOL_REL:
        print(f"PASS energy_conservation: max relative error {max_err:.3e} (worst: {worst})")
        return 0
    print(f"FAIL energy_conservation: max relative error {max_err:.3e} (worst: {worst}), tol {TOL_REL:.0e}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
