# ADR-0001: Repository layout and licensing

## Status

Accepted

## Date

2026-09-29

## Context

The repository is greenfield and will hold mixed domains: mechanical and electrical hardware, microcontroller firmware, and hosted software. These domains have different toolchains, different artifacts, and different licensing needs, so the layout and license policy must be settled before content arrives.

## Decision

1. **Layout (Option B, per-domain skeleton).** Top-level directories `hardware/` (with `cad/`, `electronics/`, `bom/`), `firmware/`, `software/`, `docs/` (with `architecture/`, `build-guide/`, `adr/`), `tools/`, and `libs/`. Each directory carries a README that records its purpose and license.
2. **Generated artifacts.** STL and PNG files are build outputs and are not committed. Git LFS is not used. CI will build artifacts later. Curated images are allowed only under `docs/`.
3. **Split licensing.** `hardware/` and `docs/` use CC-BY-SA-4.0. `firmware/`, `software/`, `tools/`, and root build files use MIT. `libs/*` keep the upstream license of each library. License texts live in `LICENSES/<SPDX-ID>.txt`. There is no root `LICENSE` file, because it would imply a single license.
4. **ADRs.** Decision records are stored in `docs/adr/` in the Nygard format.

## Alternatives considered

- **Layouts A and C:** other top-level organizations were rejected in favor of the per-domain layout (Option B), which maps directly to the different toolchains and licenses.
- **Committing STL files:** rejected; binary outputs bloat history and go stale against the sources.
- **Git LFS:** rejected; adds tooling and hosting constraints with no current need.
- **CERN-OHL:** rejected for hardware; CC-BY-SA-4.0 is simpler and sufficient for now.
- **Apache-2.0:** rejected for code; MIT is simpler and sufficient.
- **A single license for everything:** rejected; documentation and hardware designs benefit from share-alike terms that are a poor fit for code.

## Consequences

- Contributors must check the license table (root README and this ADR) before adding files.
- Future CI owns artifact generation and publication.
- REUSE lint is a possible follow-up once source files exist.
