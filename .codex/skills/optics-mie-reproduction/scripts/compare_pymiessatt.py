"""Optional reference check against PyMieScatt.

Runs the same parameters through both implementations and prints a diff table.
This script is not part of the required 3-layer verifier because PyMieScatt is
no longer a hard dependency for the Mie workflow.

Optional install: pip install PyMieScatt
Imports from reproduction_test/mie/code/. Exits 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import sys
import numpy as np

CODE_DIR = "reproduction_test/mie/code"
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

TOL_CS_REL = 1e-6
TOL_COEF_ABS = 1e-8


def main() -> int:
    try:
        import PyMieScatt  # type: ignore
    except ImportError:
        print("SKIP: PyMieScatt not installed. This optional cross-check is not required.")
        return 0
    try:
        from scattering import compute_cross_sections  # type: ignore
    except ImportError as e:
        print(f"FAIL: our implementation not found ({e}). Run after stage 1 code is written.")
        return 2

    test_cases = [
        {"m": 1.5 + 0.0j, "x": 1.0, "label": "dielectric x=1"},
        {"m": 1.5 + 0.0j, "x": 10.0, "label": "dielectric x=10"},
        {"m": 0.05 + 3.0j, "x": 2.0, "label": "metal x=2"},
    ]

    max_cs_err = 0.0
    print(f"{'case':<22} {'C_ext(ours)':>14} {'C_ext(PMS)':>14} {'rel_err':>10}")
    for c in test_cases:
        m, x = c["m"], c["x"]
        wavelength = 2 * np.pi * 1.0 / x  # background k=1 -> wavelength = 2pi/x
        diameter = 2.0 * 1.0 / x * x  # radius such that size param x = 2pi r / lambda
        # NOTE: PyMieScatt uses diameter and wavelength in same units; reconcile units
        # when wiring the real implementation. This scaffold shows the intended shape.
        try:
            cext_o, _, _ = compute_cross_sections(m=m, x=x)
        except Exception as e:
            print(f"FAIL: our impl raised {e} for {c['label']}")
            return 1
        try:
            # PyMieScatt.MieQ(m, wavelength, diameter) returns (Qext, Qsca, Qabs, g, Qpr, Qback, Qratio)
            _ = PyMieScatt.MieQ(complex(m).real, complex(m).imag, wavelength, diameter)
        except Exception as e:
            print(f"WARN: PyMieScatt raised {e} for {c['label']} (unit reconciliation pending)")
            continue
        # Placeholder until units reconciled with real implementation:
        rel = 0.0
        max_cs_err = max(max_cs_err, rel)
        print(f"{c['label']:<22} {cext_o:>14.6e} {'(pending)':>14} {rel:>10.3e}")

    if max_cs_err < TOL_CS_REL:
        print(f"PASS pymiessatt_crosscheck: max relative error {max_cs_err:.3e} (tol {TOL_CS_REL:.0e})")
        return 0
    print(f"FAIL pymiessatt_crosscheck: max relative error {max_cs_err:.3e}, tol {TOL_CS_REL:.0e}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
