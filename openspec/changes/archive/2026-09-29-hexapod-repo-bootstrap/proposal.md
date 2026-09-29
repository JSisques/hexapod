# Proposal: Hexapod Repository Bootstrap

## Intent

The repo is greenfield: a one-line README and no layout, licenses, or hygiene files. Before any CAD, firmware, or software work begins, it needs a predictable structure, clear license boundaries, and recorded decisions.

## Scope

### In Scope
- Directory skeleton (Option B), each directory with a short README: `hardware/{cad,electronics,bom}`, `firmware/`, `software/`, `docs/{architecture,build-guide,adr}`, `tools/`, `libs/`
- Root `README.md` rewrite with a repo map and a license table
- `.gitignore` (ignores `build/` and generated STL/PNG), `.editorconfig`
- `LICENSES/` holding CC-BY-SA-4.0 (hardware) and MIT (firmware/software)
- Base `Makefile` with `help` and placeholder targets only
- Empty `firmware/` and `software/` stubs
- `docs/adr/0001-repository-layout-and-licensing.md` recording layout, STL policy, and licensing

### Out of Scope
- BOSL2 submodule, sample OpenSCAD part, `params.scad`
- GitHub Actions / CI workflow
- MCU, servo, driver, and language choices
- Electronics tooling (KiCad) and hosting decisions

## Capabilities

### New Capabilities
- `repo-structure`: the top-level per-domain layout, per-directory READMEs, and root repo map
- `repo-hygiene`: `.gitignore` (no committed STL/PNG/`build/`), `.editorconfig`, and the base Makefile entry point
- `licensing`: split licensing (CC-BY-SA 4.0 for hardware, MIT for firmware/software) via `LICENSES/` and the README table
- `decision-records`: ADR location, format, and the first ADR

### Modified Capabilities
None

## Approach

Use Option B from the exploration, because each domain gets one toolchain and one future CI job, paths stay shallow, and the tree shows what the project is. Generated STL/PNG are build outputs: ignore them now and produce them in CI later, with no Git LFS. The Makefile is the single entry point; for now it only prints help and stub targets. ADR-0001 records the confirmed decisions so later changes can refer to it.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `README.md` | Modified | Repo map, license table |
| `hardware/`, `firmware/`, `software/`, `tools/`, `libs/` | New | Skeleton plus READMEs |
| `docs/` | New | architecture, build-guide, adr/0001 |
| `LICENSES/` | New | CC-BY-SA-4.0, MIT texts |
| `.gitignore`, `.editorconfig`, `Makefile` | New | Hygiene and entry point |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Mixed-license ambiguity | Med | A per-directory license note plus a README table |
| Placeholder Makefile targets mistaken for real ones | Low | Targets print "not implemented" |
| Empty dirs not tracked by git | Low | A README in each directory |

## Rollback Plan

The change is purely additive apart from `README.md`. To roll back, revert the bootstrap commit(s) with `git revert`. There is no runtime, data, or dependency impact.

## Dependencies

- None

## Success Criteria

- [ ] Every Option B directory exists and has a README
- [ ] The root README maps each directory and states its license
- [ ] `LICENSES/` contains the full CC-BY-SA-4.0 and MIT texts
- [ ] `make` / `make help` runs and lists targets
- [ ] `git status` shows generated `*.stl`, `*.png` under build paths, and `build/` as ignored
- [ ] ADR-0001 records layout, STL policy, and licensing
