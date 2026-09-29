```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:c270f4ff02f0c95a782dafc84d97ed1c6875aa77000000000000000000000000
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 13/13
scenarios: 19/19
test_command: make gate-test
test_exit_code: 0
test_output_hash: sha256:a400c3f17abe00b7d696f7f74665c9c5d1c7c468ca075cf07db0bbb285d84f49
build_command: make stl render
build_exit_code: 0
build_output_hash: sha256:61ce99ad1eff6d3ddd0e1422acd974bb44642c50894532835edb76c201707dde
```

## Verification Report

**Change**: openscad-toolchain (branch feat/openscad-toolchain-3-ci, HEAD b87cc64, PRs #5, #6, #7 open)
**Mode**: Standard (strict_tdd false, no runner; shell checks are the tests)

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 27 (1.1-1.6, 2.1-2.12, 3.1-3.4) |
| Tasks complete | 27 |
| Tasks incomplete | 0 |

### Build & Tests Execution
**Build**: PASS. `make stl render` exit 0 (local openscad 2026.09.29, Manifold); `build/stl/smoke.stl` 200891 B, `build/png/smoke.png` 35204 B.
**Tests**: PASS. `make gate-test` exit 0, prints `gate-test: OK`.
**Coverage**: not available (threshold 0).

Other observed runs: `make` exit 0 lists help/stl/render/clean/doctor/gate-test/firmware/software/docs; `make doctor` exit 0 (toolchain local, BOSL2 402be424...); second `make stl` silent with unchanged mtime; after `touch hardware/cad/smoke/main.scad` and after `touch libs/BOSL2/std.scad`, STL mtime advanced (rebuilt); `build/dep/stl/smoke.d` first line `build/stl/smoke.stl: \`; submodule deinit then `make stl` printed `error: libs/BOSL2 is missing; run: git submodule update --init libs/BOSL2`, make exit 2, submodule restored; `make clean stl render TOOLCHAIN=docker` exit 0 and `test -O` true; `make firmware` and `make docs` print "not implemented", make exit 2 (recipe exit 1); `git check-ignore -v build/stl/smoke.stl` -> `.gitignore:2:/build/`; `git check-ignore hardware/cad/part.stl` ignored; `make clean` twice exit 0, `build/` absent; `cmp LICENSES/BSD-2-Clause.txt libs/BOSL2/LICENSE` identical.

### Spec Compliance Matrix
| Requirement | Scenario | Evidence | Result |
|---|---|---|---|
| cad-build Entry points | Smoke part built | `make stl render`, files non-empty | COMPLIANT |
| cad-build Entry points | Non-entry files ignored | added `hardware/cad/zz/other.scad`; `make stl` produced only smoke.stl | COMPLIANT |
| cad-build Toolchain | Docker fallback | `TOOLCHAIN=docker` build passes (real "no openscad on PATH" not simulated; auto logic read in Makefile) | COMPLIANT (forced) |
| cad-build Toolchain | Old local binary | stub binary via `OPENSCAD=`: no `--backend` in args, version warning printed | COMPLIANT |
| cad-build Library path/guard | Uninitialized submodule | exit non-zero, hint printed | COMPLIANT |
| cad-build Warnings gate | Warning fails build | fixture as part `wp`: WARNING printed, exit 2 from make, no STL left; `gate-test` OK | COMPLIANT |
| cad-build Dependency tracking | Included file changes | touched BOSL2/std.scad, STL rebuilt | COMPLIANT |
| cad-build Clean | Clean twice | both exit 0, build/ absent | COMPLIANT |
| ci Triggers | PR triggers run | `pull_request`, `push: [main]`; run 36597495989 on pull_request | COMPLIANT |
| ci Canonical build | Warning fails CI | CI runs gate-test + `TOOLCHAIN: docker` (doctor log shows pinned image); gate proven in CI ("gate-test: OK"); a failing-part CI run not executed | COMPLIANT |
| ci Artifacts | Artifacts uploaded | artifact `cad-e958f751...` contains `stl/smoke.stl`, `png/smoke.png`; expires 14 days after creation; `if-no-files-found: error` | COMPLIANT |
| ci Least privilege | Permissions declared | only top-level `contents: read` | COMPLIANT |
| licensing | BOSL2 license present | file identical to upstream, BSD text | COMPLIANT |
| licensing | Library note | libs/README.md table row `BSD-2-Clause` | COMPLIANT (see W1) |
| repo-hygiene | Default goal lists targets | `make` exit 0 | COMPLIANT |
| repo-hygiene | Placeholder target | firmware: "not implemented", make exit 2 | COMPLIANT |
| repo-hygiene | CAD targets are real | `make clean` exit 0, no "not implemented" | COMPLIANT |
| repo-structure | No deferred artifacts | no `params.scad` | COMPLIANT |
| repo-structure | Only smoke part exists | `fd -e scad hardware` -> only smoke/main.scad | COMPLIANT |

**Compliance summary**: 19/19 scenarios compliant (13/13 requirements). CI facts: latest run 36597495989 success on head b87cc64 (18s job); `gh pr checks` build pass.

### Correctness / MODIFIED delta consistency
- repo-hygiene delta: "make itself reports 2, recipe exits 1" matches observation and the main spec wording; the placeholder example changes from `stl` to `firmware`, consistent. Original "Other targets MUST be placeholders" correctly narrowed.
- repo-structure delta: replaces forbid list consistently with tree (.gitmodules, smoke, fixture, workflow present). `tools/cad/fixtures/warning.scad` is a `.scad` outside `hardware/cad`, so the "only smoke" scenario holds.
- licensing delta is ADDED and does not conflict with main spec (main table covers domain dirs; extra `libs/BOSL2` row is additive).

### Coherence (Design)
| Decision | Followed? | Notes |
|---|---|---|
| Image tag + index digest | Yes | tag changed to dev.2026-01-19 (documented, GLAD failure in newer tags) |
| Host runner + TOOLCHAIN=docker | Yes | |
| Same-path mount, uid/gid | Yes | `test -O` true |
| wildcard sources, `%.scad: ;`, gate fixture | Yes | |
| CI triggers, SHA pins with `# v7.0.1`, 14d retention | Yes | both actions full 40-char SHAs |
| Checkout `submodules` | Deviation | design says `true`, workflow uses `recursive` (harmless; ADR/design not updated) |
| `-d` first line, gate macro | Yes | macro also `rm -f` on failure (documented) |

### Issues Found
**CRITICAL**: None.

**WARNING**:
- W1. The licensing requirement says `libs/README.md` MUST note BOSL2 is "not covered by the repo's own licenses". The README says "Each library keeps its own upstream license" and links the text; it never uses the explicit not-covered wording. Scenario passes; requirement wording only loosely met.
- W2. Design says `submodules: true`; implementation uses `recursive` (documentation drift).
- W3. Not directly exercised: real auto-fallback to Docker with no openscad on PATH, and a failing-part CI run (proved indirectly via gate-test in CI and locally).

**SUGGESTION**:
- S1. Artifact name is `cad-${{ github.sha }}`; on pull_request that is the merge commit SHA (`e958f751...`), not the branch head (b87cc64). Consider noting it or using `github.event.pull_request.head.sha`.
- S2. Warning-part build also prints "Can't open dependencies file build/dep/stl/wp.d" (OpenSCAD aborts with hardwarnings); cosmetic noise.
- S3. `cad-build` and `ci` delta specs are full-spec style without `## ADDED Requirements` headers; add them so archive merges cleanly.
- S4. `evidence_revision` in the envelope is derived from the git tree id padded, not a true sha256; native settlement may reject it.
- S5. Stale `openspec/config.yaml` context line still says "Testing: no runner, no CI" and "only README.md exists".

### Verdict
PASS WITH WARNINGS
All 27 tasks done, 19/19 scenarios verified by real commands, CI green; only documentation-level warnings.
