# Design: Hexapod Repository Bootstrap

## Technical Approach

This change is purely additive, except for the rewrite of `README.md`. It creates the Option B per-domain skeleton, and each directory gets a README so git tracks it and records its purpose and license. Hygiene lives in three root files: `.gitignore`, `.editorconfig`, and `Makefile`. Licensing uses REUSE-style `LICENSES/<SPDX-ID>.txt` files. The authoritative path-to-license mapping lives in the root README table and in ADR-0001. There is no source code, so the design is a file contract.

## Architecture Decisions

| Topic | Options | Tradeoff | Decision |
|---|---|---|---|
| Directory tracking | `.gitkeep` / README per dir | A README documents purpose and license | README per dir |
| License file layout | Root `LICENSE` / `LICENSES/<SPDX>.txt` | A root `LICENSE` implies a single license and misleads GitHub detection | `LICENSES/CC-BY-SA-4.0.txt`, `LICENSES/MIT.txt`. No root `LICENSE` |
| License mapping | SPDX headers + `REUSE.toml` / README table + per-dir note | Full REUSE is heavy while no source exists | Table + per-dir note now. REUSE lint is deferred |
| Generated images | Ignore all / ignore all except under `docs/` | Needs one curated hero image | `*.png` ignored repo-wide, re-included under `/docs/` only |
| Placeholder exit code | 0 / non-zero | Exit 0 lets a future CI pass silently with no artifacts | Placeholders exit `1` with a "not implemented" message |
| Help implementation | Hard-coded echo / `##` self-documenting via awk | awk is POSIX and keeps targets and help in sync | Self-documenting `##` comments |
| `.gitattributes` | Add / skip | No LFS, and `.editorconfig` covers LF for editors | Skip (deferred) |
| ADR format | Nygard / MADR full | MADR is verbose for a solo repo | Nygard + "Alternatives considered" |

## Directory Tree

```
.
├── .editorconfig                 (new)
├── .gitignore                    (new)
├── Makefile                      (new)
├── README.md                     (modify)
├── LICENSES/
│   ├── CC-BY-SA-4.0.txt          (new, verbatim legalcode)
│   └── MIT.txt                   (new, "Copyright (c) 2026 Javier Plaza Sisqués")
├── hardware/README.md            (new)
│   ├── cad/README.md
│   ├── electronics/README.md
│   └── bom/README.md
├── firmware/README.md
├── software/README.md
├── docs/README.md
│   ├── architecture/README.md
│   ├── build-guide/README.md
│   └── adr/
│       ├── README.md
│       └── 0001-repository-layout-and-licensing.md
├── tools/README.md
└── libs/README.md
```

## File Content Outline

| File | Content |
|---|---|
| `README.md` | Title, one-paragraph pitch, repo map (dir → purpose), license table, `make help` quick start, link to ADR index |
| `hardware/README.md` | Domain overview, links to its three subdirectories, `License: CC-BY-SA-4.0` |
| `hardware/cad/README.md` | OpenSCAD parts/assemblies (planned). STL/PNG are build outputs and are never committed |
| `hardware/electronics/README.md` | Schematics/PCB. Tooling not yet decided |
| `hardware/bom/README.md` | Bill of materials (planned `bom.csv`) |
| `firmware/README.md` | MCU firmware stub. Stack not yet decided. `License: MIT` |
| `software/README.md` | Hosted/control software stub. Stack not yet decided. `License: MIT` |
| `docs/README.md` + 3 subdir READMEs | Purpose of each section. Curated images allowed. `License: CC-BY-SA-4.0` |
| `docs/adr/README.md` | Format, naming `NNNN-kebab-title.md`, status values, index table |
| `tools/README.md` | Dev/build scripts. `License: MIT` |
| `libs/README.md` | Third-party libraries (future BOSL2 submodule). Each keeps its own upstream license |

Every per-directory README ends with a line in this form: `License: <SPDX-ID> — see [LICENSES/<SPDX-ID>.txt](../LICENSES/<SPDX-ID>.txt)`, with the relative path adjusted for the directory depth.

**License table (root README):**

| Path | License |
|---|---|
| `hardware/`, `docs/` | CC-BY-SA-4.0 |
| `firmware/`, `software/`, `tools/`, root build files | MIT |
| `libs/*` | Upstream license of each library |

## Interfaces / Contracts

### `.gitignore`

```gitignore
# Build outputs
/build/

# Generated CAD / render artifacts (produced by make/CI, never committed)
*.stl
*.3mf
*.amf
*.off
*.gcode
*.png

# Curated documentation images are allowed
!/docs/**/*.png

# Local tooling (skill registry cache)
/.atl/

# OS / editor noise
.DS_Store
*~
*.swp
.idea/
.vscode/
```

The negation works because no parent directory of `docs/` is excluded.

### `.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.scad]
indent_size = 4

[{Makefile,*.mk}]
indent_style = tab
indent_size = 4

[*.md]
trim_trailing_whitespace = false

[LICENSES/**]
indent_style = unset
indent_size = unset
trim_trailing_whitespace = false
```

Markdown keeps trailing whitespace because two trailing spaces are a hard line break. License texts are verbatim and must not be reformatted.

### `Makefile`

```make
.DEFAULT_GOAL := help
.PHONY: help stl render firmware software docs clean

NOT_IMPLEMENTED = @echo "make $@: not implemented yet (see docs/adr/0001-repository-layout-and-licensing.md)" >&2; exit 1

help: ## List available targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-10s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

stl: ## Export STL models to build/ (placeholder)
	$(NOT_IMPLEMENTED)
render: ## Render PNG previews to build/ (placeholder)
	$(NOT_IMPLEMENTED)
firmware: ## Build firmware (placeholder)
	$(NOT_IMPLEMENTED)
software: ## Build software (placeholder)
	$(NOT_IMPLEMENTED)
docs: ## Build documentation (placeholder)
	$(NOT_IMPLEMENTED)
clean: ## Remove build outputs (placeholder)
	$(NOT_IMPLEMENTED)
```

Recipes use tab indentation. Running `make` with no target shows `help`.

### ADR-0001 structure

The title is `# ADR-0001: Repository layout and licensing`. It contains these sections in order:

- **Status**: Accepted
- **Date**: 2026-09-29
- **Context**: greenfield, mixed hardware/firmware/software domains
- **Decision**:
  1. Option B layout
  2. STL/PNG are build outputs, not committed, no Git LFS, CI-built later, curated images only under `docs/`
  3. Split licensing per the table above, no root `LICENSE`
  4. ADRs stored in `docs/adr/`, Nygard format
- **Alternatives considered**: layouts A and C; committing STL; Git LFS; CERN-OHL; Apache-2.0; a single license
- **Consequences**: contributors check the license table; future CI owns artifacts; REUSE lint is a possible follow-up

## Data Flow

```
developer ──make──▶ help (exit 0: target list)
          ──make stl|render|...──▶ stderr "not implemented" (exit 1)
future CI ──make stl──▶ build/*.stl (ignored) ──▶ release artifacts
```

## Testing Strategy

There is no test runner, so verification uses commands:

| Check | Command | Expected |
|---|---|---|
| Help | `make`, `make help` | exit 0, lists 7 targets |
| Placeholder | `make stl` | recipe exits 1 (make exits 2), message on stderr |
| Ignored | `git check-ignore -v build/x hardware/cad/a.stl x.3mf render.png` | all matched |
| Allowed | `git check-ignore docs/hero.png` | exit 1 (not ignored) |
| Tree | `fd README.md` | 13 READMEs (12 subdirectories + root) |

## Threat Matrix

N/A. The Makefile recipes run only static `echo`/`awk` with no user input. There is no routing, subprocess orchestration, VCS/PR automation, or process-integration boundary.

## Migration / Rollout

No migration is required. To roll back, run `git revert`.

## Open Questions

- [x] `.atl/` is ignored via `.gitignore` (decided by the user).
- [ ] Copyright holder string for MIT: assumed "Javier Plaza Sisqués".
