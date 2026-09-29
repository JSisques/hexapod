# Apply Progress: hexapod-repo-bootstrap

Branch: feat/hexapod-repo-bootstrap-1-skeleton (PR 1 of feature-branch-chain). Uncommitted, in working tree.

## Completed
- [x] 1.1 .gitignore
- [x] 1.2 .editorconfig
- [x] 1.3 Makefile
- [x] 2.1 hardware READMEs (4)
- [x] 2.2 firmware, software, tools READMEs
- [x] 2.3 libs/README.md
- [x] 2.4 docs READMEs (3)
- [x] 2.5 docs/adr/README.md
- [x] 2.6 ADR-0001 (Accepted, 2026-09-29)

## Remaining
- 3.1 (PR 2), 3.2, 3.3 (PR 3), 4.x verification

## Verification observed
- `make` and `make help`: exit 0, 7 targets listed.
- `make stl`, `make clean`: stderr message; recipe exits 1 (make itself reports exit 2, "Error 1").
- `git check-ignore -v build/x hardware/cad/a.stl x.3mf render.png .atl/x`: all matched; `docs/hero.png`: exit 1 (not ignored).

## Deviations
None. License links use ../LICENSES paths adjusted by depth; targets land in PR 2/3.
