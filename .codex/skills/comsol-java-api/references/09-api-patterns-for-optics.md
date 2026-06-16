# API Patterns For Optics

This file solves: map COMSOL Java API layers to optics_agent waveguide, eigenmode, and paper-reproduction models, and identify where this Java API manual is insufficient.

## Source Split

- Manual-derived: generic Java API layers for geometry, mesh, study, solver, results.
- optics_agent-derived: Degiron 2009 Fig. 3 and COMSOL runtime probes exposed headless batch restrictions, mesh fallback needs, and mode-analysis gaps.

## Waveguide/Eigenmode API Layers

| Layer | API objects | Typical content |
|---|---|---|
| Parameters | `model.param()` | `lambda0`, `k0`, widths, gaps, thickness sweep, material constants. |
| Geometry | `model.geom()` | 2D cross-section, layer stack, metal, dielectric guide, air/substrate/domain truncation. |
| Selections | `model.selection()`, geometry `createselection` | Domains for materials; boundaries for scattering/PML/PEC/symmetry. |
| Materials | `model.material()` or variables | Complex permittivity/refractive index per domain. |
| Physics | `model.physics()` | Wave Optics/RF interface, mode-analysis feature, boundary conditions. |
| Mesh | `model.mesh()` | Explicit `FreeTri`/`FreeTet`, size controls near metal/gaps/interfaces. |
| Study | `model.study()` | `ModeAnalysis`/`BoundaryModeAnalysis`/`Eigenvalue`/`Frequency`, depending on module and dimension. |
| Solver | `model.sol()` | Auto sequence plus eigenvalue shift, number of modes, tolerances. |
| Results | `model.result()` | `neff`, `beta`, losses, field profiles, tables/stdout rows. |

## What The Java API Manual Does Not Provide

The Java API reference does not replace:

- Wave Optics Module User's Guide: exact electromagnetic interface options, mode-analysis settings, ports, scattering/PML boundaries, and variables such as `emw.neff`.
- RF Module User's Guide: RF interface strings and boundary mode analysis behavior.
- COMSOL Multiphysics Reference Manual: detailed solver theory, eigenvalue solver behavior, advanced solver errors, and version-specific changes.

Use GUI-exported Java for exact COMSOL 6.3 feature tags and setting keys.

## Degiron 2009 Fig. 3 Lessons

- Java API syntax is official, but hand-written Java is not equivalent to a correct GUI model.
- Mode analysis depends on physics feature, boundary, material, mesh, and solver sequence details that were not fully recoverable from the generic Java API manual.
- Physics-controlled mesh failed in the actual Degiron run; explicit `FreeTri` mesh was a useful fallback.
- Full-vector mode analysis reached the eigensolver but failed matrix factorization across shifts. That is a physical/numerical setup problem, not just a runner problem.
- `emw.neff` and `ewfd.neff` are not guaranteed to exist. They depend on the selected physics interface and study type.

## Conservative Build Ladder

1. Start with a scalar core PDE/Helmholtz smoke model to validate Java, geometry, mesh, study, solver, and output flow.
2. Add a minimal Wave Optics/RF GUI-exported model for one dielectric waveguide mode.
3. Add metal and loss only after a dielectric mode returns plausible `neff`.
4. Add coupled structures and sweeps after isolated components pass.
5. Validate result ranges and mode branch labels separately from Magnus job success.

## Notes And Common Errors

- Do not report a surrogate/fallback sweep as a physical COMSOL reproduction.
- If mode-analysis settings are unknown, explicitly request or generate a minimal GUI-exported Java template rather than guessing.
- Keep stdout CSV markers simple when COMSOL Java sandbox blocks file output.
