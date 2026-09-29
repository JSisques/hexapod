# Tasks: Hexapod Repository Bootstrap

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~750-850 (CC-BY-SA-4.0 verbatim ~430; rest ~350) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (hygiene+skeleton+ADR) -> PR 2 (CC-BY-SA text) -> PR 3 (MIT+root README) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Hygiene files, dir skeleton, ADR-0001 (~300 lines) | PR 1 | `make help; make stl; echo $?` | `git check-ignore -v build/x a.stl x.3mf render.png` | Revert PR 1 |
| 2 | Verbatim CC-BY-SA-4.0 legalcode (~430 lines, generated text, size-exception candidate) | PR 2 | `wc -l LICENSES/CC-BY-SA-4.0.txt` | N/A: static legal text | Delete `LICENSES/CC-BY-SA-4.0.txt` |
| 3 | MIT text, root README rewrite with license table | PR 3 | `rg "MIT" LICENSES/MIT.txt README.md` | `fd README.md` (13 files) | Revert PR 3 |

For feature-branch-chain: PR 1 base = tracker branch; PR 2 base = PR 1 branch; PR 3 base = PR 2 branch.

## Phase 1: Hygiene (PR 1)

- [x] 1.1 Create `.gitignore` per design (stl/3mf/amf/off/gcode/png, `!/docs/**/*.png`, `/.atl/`, OS noise). Verify: `git check-ignore -v build/x hardware/cad/a.stl x.3mf render.png .atl/x` all match; `git check-ignore docs/hero.png` exits 1.
- [x] 1.2 Create `.editorconfig` per design. Verify: `rg "root = true" .editorconfig`.
- [x] 1.3 Create `Makefile` (tab recipes, `##` help, placeholders exit 1). Verify: `make` and `make help` exit 0 listing 7 targets; `make stl`, `make clean` exit 1 with stderr message.

## Phase 2: Skeleton and ADR (PR 1)

- [x] 2.1 Create `hardware/README.md`, `hardware/cad/README.md`, `hardware/electronics/README.md`, `hardware/bom/README.md` (CC-BY-SA-4.0 note, `../LICENSES/...` relative paths).
- [x] 2.2 Create `firmware/README.md`, `software/README.md`, `tools/README.md` (MIT note).
- [x] 2.3 Create `libs/README.md` (upstream licenses, future BOSL2 submodule).
- [x] 2.4 Create `docs/README.md`, `docs/architecture/README.md`, `docs/build-guide/README.md` (CC-BY-SA-4.0 note).
- [x] 2.5 Create `docs/adr/README.md` (format, `NNNN-kebab-title.md`, status values, index table).
- [x] 2.6 Create `docs/adr/0001-repository-layout-and-licensing.md` with all sections in design order, Accepted, 2026-09-29, Alternatives considered.

## Phase 3: Licensing and root README (PR 2, PR 3)

- [ ] 3.1 (PR 2) Create `LICENSES/CC-BY-SA-4.0.txt` with verbatim legalcode from creativecommons.org.
- [ ] 3.2 (PR 3) Create `LICENSES/MIT.txt` with "Copyright (c) 2026 Javier Plaza Sisqués". Confirm no root `LICENSE` exists.
- [ ] 3.3 (PR 3) Rewrite `README.md`: pitch, repo map, license table (docs/hardware CC-BY-SA-4.0; tools/firmware/software MIT; libs upstream), `make help` quick start, ADR link.

## Phase 4: Verification

- [x] 4.1 `fd README.md` returns 13 files; `fd -t d -d 2` shows every spec'd directory.
- [x] 4.2 `rg "^License:" -g '*/README.md'` matches each domain and subdirectory README (`libs/` excepted).
- [x] 4.3 Re-run Phase 1 shell checks; `git status --short` shows no stray `.atl/` or generated files.
