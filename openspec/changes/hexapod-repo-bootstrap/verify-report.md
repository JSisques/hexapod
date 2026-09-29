# Verify Report: hexapod-repo-bootstrap

Branch: feat/hexapod-repo-bootstrap-3-mit-readme (PR1+PR2+PR3). Strict TDD: false. Mode: openspec.
Working tree was clean before this report was written.

## Observed command output
- `make`: exit 0, lists 7 targets (help, stl, render, firmware, software, docs, clean). `make help`: exit 0.
- `make stl` / `make clean`: stderr "not implemented yet (see docs/adr/0001-...)", recipe `Error 1`, make process exit status 2.
- `git check-ignore -v build/x hardware/cad/a.stl hardware/cad/part.stl x.3mf render.png build/out.stl build/render.png .atl/x`: all matched, exit 0.
- `git check-ignore docs/hero.png docs/architecture/hero.png`: exit 1 (not ignored).
- `fd README.md -E openspec`: 13 files (root + 12 subdirectories).
- `fd -t d -d 2`: hardware/{cad,electronics,bom}, firmware, software, docs/{architecture,build-guide,adr}, tools, libs, LICENSES all present.
- `rg "^License:"`: 11 matches (hardware x4, docs x4 incl. adr, firmware, software, tools = MIT). libs excepted.
- LICENSES: CC-BY-SA-4.0.txt 428 lines, MIT.txt 21 lines ("Copyright (c) 2026 Javier Plaza Sisqués"); no root LICENSE (only LICENSES/).
- No `.gitmodules`, `params.scad`, `*.scad`, `.github`. firmware/ and software/ contain only README.md.
- `git status --short`: empty (before this report).

## Compliance matrix
| Requirement / Scenario | Result |
|---|---|
| Structure: all directories present | PASS |
| Structure: README in each dir | PASS |
| Structure: stubs hold no code | PASS |
| Structure: root README map covers all domains | PASS |
| Structure: no deferred artifacts | PASS |
| Hygiene: build output ignored | PASS |
| Hygiene: stray STL ignored | PASS |
| Hygiene: .editorconfig root=true + [Makefile] tabs | PASS (section is `[{Makefile,*.mk}]`) |
| Hygiene: `make` lists targets, exit 0 | PASS |
| Hygiene: placeholder prints "not implemented", non-zero | PASS (make exits 2, recipe 1) |
| Licensing: both texts present, MIT holder+year | PASS |
| Licensing: root README table complete | PASS |
| Licensing: per-dir note matches table | PASS |
| ADR: location/naming | PASS |
| ADR: five sections, Status Accepted | PASS |
| ADR: Option B, LFS, CC-BY-SA-4.0, MIT in Decision | PASS |
| ADR: deferred items (MCU, servo, languages) noted | FAIL (SHOULD) |

## Issues
CRITICAL: none.

WARNING
1. ADR-0001 does not list deferred decisions (MCU, servo/driver, languages, KiCad, hosting). Spec says SHOULD, and the "Deferred items noted" scenario has no supporting text. Add a "Deferred decisions" list.
2. Spec/design say placeholders exit "1"; observed make exit status is 2 (recipe exits 1, make wraps it as 2). Non-zero holds. Consider wording "recipe fails with Error 1 / non-zero".

SUGGESTION
1. tasks.md 4.1-4.3 still unchecked; the checks pass and can be marked done.
2. apply-progress.md is stale (mentions PR 1 branch, 3.x remaining).
3. Verbatim integrity of CC-BY-SA-4.0.txt was not checked against upstream (no network check); 428 lines, header looks correct.
4. Root README table lists `libs/` upstream license and root build files, which is consistent with design.
