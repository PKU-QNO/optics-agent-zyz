# Mie Reproduction Papers

11 papers, executed in 7 stages by increasing difficulty. Each stage has one main paper plus optional references. Non-arXiv PDFs are in `papers/mie/`; arXiv papers are accessible directly.

## Stage 1 — Single-sphere Mie basics

### Akimov — Mie scattering theory: a review (arXiv 2401.04146, 2024)

Systematic review of the physical origin of electric/magnetic multipole coefficients in Mie scattering; analyzes asymptotic behavior of spherical Bessel/Hankel functions and its effect on scattering efficiency.

- **Goal**: implement Lorenz-Mie core formulas; observe smooth transition across Rayleigh / Mie / geometric-optics regimes and the emergence order of multipoles.
- **Outputs**: `code/mie_coefficients.py` ($a_n, b_n$), `code/scattering.py` (cross sections), $Q_{sca}(x)$ curve for $n=1.5,2,3,4$, multipole decomposition.
- **Verification**: energy conservation, Rayleigh $x^4$, large-size $Q\to2$.
- **Caveat**: Akimov is a review and may have typos; verify $a_n,b_n$ against Bohren & Huffman or Kerker, use Akimov only as cross-check.

## Stage 2 — Metal sphere LSPR

### Colas des Francs — Mie plasmons: modes volumes, quality factors and coupling strengths (arXiv 1112.2814, 2011)

Mie expansion for metal nanosphere LSPR; closed-form expressions for mode volume, quality factor, Purcell factor.

- **Goal**: introduce Drude dispersion; examine how real/imaginary parts of the dielectric function set LSPR position and linewidth.
- **Outputs**: `code/drude.py` (Au/Ag Drude), `code/lspr.py`, LSPR wavelength vs radius ($R=10,20,50,100$ nm), Purcell factor spectrum.
- **Verification**: quasi-static LSPR $\mathrm{Re}(\varepsilon)=-2\varepsilon_d$.
- **Physics**: difference between quasi-static ($a_1$-dominated) and full Mie expansion.

## Stage 3 — Dielectric sphere Mie modes

### Main paper: to be supplemented via Web of Science

References: García-Etxarri et al. (2011); Kuznetsov et al. "Magnetic light" (Sci. Rep. 2012); Evlyukhin et al. "Demonstration of Magnetic Dipole Resonances of Dielectric Nanospheres" (Nano Lett. 2012); Kuznetsov et al. "Optically resonant dielectric nanostructures" (Science 2016).

High-index dielectric spheres support richer Mie modes (magnetic/electric dipole and quadrupole) via internal displacement current, with lower loss than plasmonic structures.

- **Goal**: compare metal LSPR vs dielectric Mie resonance; understand richer electric/magnetic multipole structure.
- **Outputs**: dielectric sphere extinction spectrum, multipole decomposition, magnetic dipole mode visualization.
- **Physics**: magnetic dipole from internal circulating displacement current; resonance set by size parameter and refractive index; electric/magnetic dipole ratio sets Kerker condition.

## Stage 4 — Core-shell Mie

### Tam — Mesoscopic nanoshells (JCP 127, 2007) — `papers/mie/204703_1_online.pdf`

Two-layer Lorenz-Mie for core-shell extinction; quasi-static fails for both thick and thin shells, requiring full series.

- **Goal**: extend single-sphere to core-shell; understand recursive boundary conditions between two layers.
- **Outputs**: `code/core_shell_mie.py`, extinction spectra vs shell thickness, shell-thickness–resonance-wavelength map, quasi-static vs full Mie comparison.
- **Verification**: shell-thickness→∞ collapses to single sphere (core material); core→0 collapses to single sphere (shell material).
- **Reference**: Arruda, "Toroidal dipole in core-shell spheres" (arXiv 2406.06800).

## Stage 5 — Periodic array collective resonance (SLR)

### Auguie & Barnes — Collective Resonances in Gold Nanoparticle Arrays (PRL 101, 2008) — `papers/mie/PhysRevLett.101.143902.pdf`

Coupling of Rayleigh anomaly and LSPR in periodic arrays produces high-Q surface lattice resonances whose linewidth is set by array period.

- **Goal**: transition from single sphere to periodic system; understand how diffraction coupling modifies resonance.
- **Outputs**: `code/coupled_dipole.py` (CDA), extinction spectra vs period (annotated Rayleigh anomaly and SLR), linewidth-vs-period curve.
- **Verification**: Rayleigh anomaly $\lambda=P\cdot n_{\text{eff}}$; large period collapses to single sphere.
- **Reference**: Gerasimov, "Plasmonic lattice Kerker effect" (arXiv 2007.13317).

## Stage 6 — Binary array geometric resonance

### Li J et al. — Tuning of narrow geometric resonances in Ag/Au binary nanoparticle arrays (Opt. Express 18, 2010) — `papers/mie/Li_J_OE2010.pdf` or `papers/mie/oe-18-17-17684.pdf`

Binary arrays of two particle materials/sizes tune geometric resonance position and linewidth independently via size ratio.

- **Goal**: introduce two single-particle polarizabilities into CDA; understand material dispersion and geometric coupling.
- **Outputs**: `code/binary_cda.py`, extinction spectra vs size ratio, linewidth-vs-size-ratio curve.
- **Verification**: large period collapses to single-particle result.

## Stage 7 — Effective refractive index and phase diagram

### Rybin — Phase diagram for the transition from photonic crystals to dielectric metamaterials (Nat. Commun. 6, 2015) — `papers/mie/Rybin_NatComm2015.pdf`

Compares Mie resonance wavelength vs Bragg resonance wavelength to build a phase diagram separating photonic-crystal and metamaterial regimes on the permittivity–filling-fraction plane.

- **Goal**: condense array scattering response into effective optical parameters; obtain effective refractive index dispersion.
- **Outputs**: `code/effective_medium.py` (S-parameter retrieval of $\varepsilon_{\text{eff}}, \mu_{\text{eff}}$), `code/phase_diagram.py`, $n_{\text{eff}}$ dispersion, $(\varepsilon, P/\lambda)$ phase diagram.
- **Verification**: low filling fraction → Maxwell-Garnett.

## Optional Papers (clear attachment points)

| Paper | arXiv | Content | Attachment |
|---|---|---|---|
| Tagviashvili | 0910.3305 | ENZ-limit Mie scattering | effective medium $n_{\text{eff}}\to0$ |
| Shamkhi | 1808.10708 | generalized Kerker transverse scattering | array angular scattering |
| Arruda | 2406.06800 | core-shell toroidal dipole | core-shell extension |
| Nieto-Vesperinas | 1201.6146 | Si sphere Kerker condition | single-sphere directional scattering |

## Execution Order Summary

Stage 1 (single sphere) → Stage 2 (metal LSPR) → Stage 3 (dielectric modes) → Stage 4 (core-shell) → Stage 5 (SLR) → Stage 6 (binary array) → Stage 7 (effective medium). Optional papers attach to their stated stages. Do not skip ahead — each stage's verifier depends on the previous stage's implementation being correct.
