# COMSOL Capability Probes

These Java files are tiny headless COMSOL probes used by the Magnus blueprint
`Optics_COMSOL_Runtime_zyz`.

They are intentionally small:

- `CorePdeEigenmode.java` checks the generic Coefficient Form PDE/eigenmode path.
- `OpticsHelmholtz.java` solves a scalar Helmholtz-like core PDE field problem.
- `WaveOpticsProbe.java` attempts a Wave Optics/RF-style electromagnetic interface.
- `FluidLaminarProbe.java` attempts a Laminar Flow/Creeping Flow interface.
- `FluidPdeFallback.java` solves a simple flow-like core PDE fallback.

Professional module probes should be interpreted carefully: success means the
interface could be created and solved in this minimal setting; failure may mean
missing module, missing license, or an interface setup issue. The report should
quote the COMSOL log rather than silently guessing.
