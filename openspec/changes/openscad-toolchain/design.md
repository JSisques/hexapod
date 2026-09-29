# Design: OpenSCAD Toolchain

## Technical Approach

A root `Makefile` drives OpenSCAD through one macro, `scad`. The macro applies the same flags and warnings gate to every invocation. The toolchain is local `openscad` when one is found, else the pinned Docker image (proposal B2). CI runs on a host runner and forces the Docker path, so CI and a local Docker build run the same bytes (A2). BOSL2 is a submodule (C1). Warnings are gated by `--hardwarnings` plus a stderr scan (D2).

## Architecture Decisions

| # | Topic | Choice | Rejected alternatives | Rationale |
|---|---|---|---|---|
| 1 | Image pin | `openscad/openscad:dev.<date>@sha256:<index-digest>` (tag plus multi-arch index digest) | Tag only; digest only | The digest is immutable and still resolves after the tag is removed. The tag keeps the reference readable. The digest must be the manifest-list digest so amd64 (CI) and arm64 (Apple Silicon) both work. |
| 2 | CI execution | `ubuntu-24.04` host runs `make ... TOOLCHAIN=docker` | Job-level `container:` | `actions/checkout` inside a container that has no `git` falls back to the REST API, which cannot fetch submodules. The image may also lack `make`. |
| 3 | Docker mount | `-v "$(CURDIR):$(CURDIR)" -w "$(CURDIR)"` with the host uid/gid | Mount at `/work` | With identical paths, the paths in `-d` dependency files are valid on the host. The uid/gid mapping keeps `build/` owned by the user. |
| 4 | Source discovery | `$(wildcard hardware/cad/*/main.scad)` | `find` | `wildcard` is built into make and works the same on BSD and GNU. There are no `find -printf` differences. |
| 5 | Stale deps | Empty pattern rule `%.scad: ;` | Post-processing `.d` files with sed/awk | When an included file is deleted, a stale `.d` file does not fail with "No rule to make target". The dependent part rebuilds instead. |
| 6 | Gate proof | Fixture `tools/cad/fixtures/warning.scad` plus a `gate-test` target, run in CI | Documented manual check only | Every CI run proves that the gate still fires. The fixture sits outside `hardware/cad`, so it is never exported. |
| 7 | CI triggers | Every PR plus pushes to `main`, no path filters | `paths:` filters | The proposal requires STL+PNG on every PR. The smoke build takes seconds. |
| 8 | Action pins | Full commit SHA with a `# vX` comment | Major tags | Supply-chain hardening. |
| 9 | BSD-2 text | Verbatim `LICENSE` from BOSL2 at the pinned SHA | Generic SPDX template | Keeps the correct copyright holder. |
| 10 | ADR-0001 | Left unchanged. ADR-0002 resolves its deferred items | Editing ADR-0001 | Accepted ADRs are immutable. |

## Makefile Contract

- **Variables:** `TOOLCHAIN ?= auto` (`auto|local|docker`), `OPENSCAD` (local path override), `OPENSCAD_IMAGE ?= <decision 1>`, `BACKEND ?= manifold`, `IMGSIZE ?= 1024,768`.
- **Detection:** `OPENSCAD` is set only if it is undefined: `$(or $(shell command -v openscad 2>/dev/null),$(wildcard /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD))`. In `auto` mode, `TOOLCHAIN` becomes `local` when this is non-empty, else `docker`.
- **Command:** in local mode, `OPENSCAD_CMD = "$(OPENSCAD)"` with `export OPENSCADPATH := $(CURDIR)/libs`. In Docker mode, `docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp -e OPENSCADPATH=$(CURDIR)/libs -v "$(CURDIR):$(CURDIR)" -w "$(CURDIR)" --entrypoint openscad $(OPENSCAD_IMAGE)`.
- **Backend:** recursive `HAS_BACKEND` is `yes` in Docker mode. Otherwise it is `$(shell "$(OPENSCAD)" --help 2>&1 | grep -q -- --backend && echo yes)`. `BACKEND_FLAG = $(if $(HAS_BACKEND),--backend=$(BACKEND))`.
- **Outputs:** `PARTS := $(patsubst hardware/cad/%/main.scad,%,$(SRCS))`. STL files go to `build/stl/<part>.stl` and PNG files to `build/png/<part>.png`. Dependency files go to `build/dep/{stl,png}/<part>.d`, and logs to `build/log/{stl,png}/<part>.log`. The file includes `-include $(wildcard build/dep/*/*.d)`.
- **Safety:** `.DELETE_ON_ERROR:`, `.SUFFIXES:`, and no `.ONESHELL`, for compatibility with macOS make 3.81.
- **Prerequisites:** `$(STLS) $(PNGS): | preflight`. The phony `preflight` target:
  - fails with `run: git submodule update --init libs/BOSL2` when `libs/BOSL2/std.scad` is missing;
  - in Docker mode, fails with an install hint when `docker` is missing;
  - in local mode, warns on stderr when `HAS_BACKEND` is empty. The warning prints the `--version` output and says: "CI image is canonical; use TOOLCHAIN=docker for parity".
- **Targets (all with `## `):**
  - `stl` and `render`;
  - `clean` (`rm -rf build`);
  - `doctor` (toolchain, binary/image, version, backend, `git submodule status libs/BOSL2`, docker availability; always exits 0);
  - `gate-test`.
- **Placeholders:** `firmware`, `software`, and `docs` keep `NOT_IMPLEMENTED`.
- **Help:** the awk regex is unchanged. Pattern rules and helper targets have no `## `, so they stay hidden. The printf width becomes `%-12s`.

Gate macro, used by all three pattern rules (`$(1)` output, `$(2)` input, `$(3)` extra flags, `$(4)` kind):

```make
scad = mkdir -p $(@D) build/dep/$(4) build/log/$(4); log=build/log/$(4)/$*.log; \
  $(OPENSCAD_CMD) --hardwarnings $(BACKEND_FLAG) $(3) -o $(1) -d build/dep/$(4)/$*.d $(2) 2>"$$log"; st=$$?; \
  cat "$$log" >&2; \
  if [ $$st -ne 0 ] || grep -Eq 'WARNING|ERROR' "$$log"; then echo "error: OpenSCAD warnings/errors in $(2)" >&2; exit 1; fi

build/stl/%.stl: hardware/cad/%/main.scad | preflight ; @$(call scad,$@,$<,,stl)
build/png/%.png: hardware/cad/%/main.scad | preflight ; @$(call scad,$@,$<,--imgsize=$(IMGSIZE) --autocenter --viewall --render,png)
build/gate/%.stl: tools/cad/fixtures/%.scad | preflight ; @$(call scad,$@,$<,,gate)
```

The `-o` value is `$@`, so the first line of each `.d` file is `build/stl/<part>.stl:` (or the PNG path). This is the correct target. `gate-test` runs `$(MAKE) build/gate/warning.stl` and captures the output. It passes only when that build exits non-zero **and** the output contains `WARNING`, so a missing binary cannot give a false pass.

## Data Flow

```
make stl ─→ preflight (BOSL2? docker? backend warning)
        └─→ build/stl/<p>.stl ← hardware/cad/<p>/main.scad (+ .d deps)
              scad macro: OPENSCAD_CMD ─stderr→ build/log/stl/<p>.log ─grep→ pass | rm + exit 1
CI: checkout(submodules) → make doctor → make gate-test → make stl render → upload build/stl, build/png
```

## File Changes

| File | Action | Description |
|---|---|---|
| `.gitmodules`, `libs/BOSL2` | Create | `https://github.com/BelfrySCAD/BOSL2.git` at the pinned SHA |
| `LICENSES/BSD-2-Clause.txt` | Create | Verbatim BOSL2 `LICENSE` |
| `libs/README.md` | Modify | Table: library, path, upstream, SPDX `BSD-2-Clause`, pin, init/bump commands |
| `.editorconfig` | Modify | Add `[.gitmodules] indent_style = tab`. The `*.scad` rule already exists. |
| `Makefile` | Modify | As described in Makefile Contract |
| `hardware/cad/smoke/main.scad` | Create | Header `// SPDX-License-Identifier: CC-BY-SA-4.0`, `include <BOSL2/std.scad>`, `$fn = 32; cuboid([20, 20, 10], rounding = 2);` |
| `tools/cad/fixtures/warning.scad` | Create | `// Intentional warning for gate-test` + `cube(size = undefined_on_purpose);` |
| `docs/adr/0002-openscad-toolchain.md` | Create | Sections: Title, Status Accepted, Date, Context, Decision (image tag+digest, local selection, BOSL2 SHA, entry points, gate, CI, PNG camera), Alternatives, Consequences, Bump procedure |
| `docs/adr/README.md` | Modify | Index row for 0002 |
| `hardware/cad/README.md` | Modify | Part-directory convention (`[a-z0-9-]`, `main.scad` entry point), outputs, gate |
| `README.md` | Modify | Status, clone `--recurse-submodules`, prerequisites, `make stl render doctor`, `libs/BOSL2` license row, ADR-0002 link, placeholders are `firmware/software/docs` only |
| `.github/workflows/cad.yml` | Create | See CI below |
| `openspec/config.yaml` | Modify | Context: OpenSCAD + GitHub Actions. `verify.build_command: make stl render`, `verify.test_command: make gate-test` |

**CI (`cad.yml`):**
- Triggers: `pull_request`, `push: branches [main]`, `workflow_dispatch`.
- Permissions: `contents: read`.
- Concurrency: `cad-${{ github.ref }}`, cancel-in-progress.
- One job on `ubuntu-24.04` with `timeout-minutes: 20`.
- `env: TOOLCHAIN: docker`, so make reads it and the image comes from the Makefile (single source).
- Steps: checkout with `submodules: true` → `make doctor` → `make gate-test` → `make stl render` → `upload-artifact` (name `cad-${{ github.sha }}`, paths `build/stl` and `build/png`, `retention-days: 14`, `if-no-files-found: error`).

## Testing Strategy

| Check | Command | Expect |
|---|---|---|
| Help | `make; make help` | exit 0; lists `stl render clean doctor gate-test` |
| Build | `make clean && make stl render && test -s build/stl/smoke.stl && test -s build/png/smoke.png` | exit 0 |
| Dep target | `rg -q '^build/stl/smoke.stl:' build/dep/stl/smoke.d && rg -q 'BOSL2/std.scad' build/dep/stl/smoke.d` | exit 0 |
| Incremental | second `make stl` is silent, runs no OpenSCAD, and leaves the STL mtime unchanged (the order-only phony `preflight` always runs, so make prints no "Nothing to be done"). Running `touch hardware/cad/smoke/main.scad` then `make stl` rebuilds | as stated |
| Gate | `make gate-test` | prints `gate-test: OK` |
| Submodule guard | `git submodule deinit -f libs/BOSL2; make stl` | non-zero, hint printed; restore with `git submodule update --init` |
| Docker | `make clean stl render TOOLCHAIN=docker && test -O build/stl/smoke.stl` | exit 0 |
| Placeholder | `make firmware` | "not implemented", non-zero |
| Ignore | `git check-ignore build/stl/smoke.stl` | ignored |
| CI | the PR run | artifact `cad-<sha>` contains `smoke.stl` and `smoke.png` |

## Threat Matrix

The Makefile runs shell subprocesses (openscad, docker), but none of the git/PR automation boundaries apply.

| Boundary | Applicability |
|---|---|
| Documentation-like paths | N/A: nothing executes docs. Only `hardware/cad/*/main.scad` is consumed |
| Git repository selection | N/A: no `git -C`/cwd automation. `doctor` only reads submodule status |
| Commit state | N/A: no commit automation |
| Push state | N/A: no push automation |
| PR commands | N/A: CI only reads and uploads artifacts. `contents: read` |

Paths with spaces are unsupported (a make limitation). Part names are restricted to `[a-z0-9-]` by convention.

## Migration / Rollout

The work is delivered as three chained PRs, each under 400 lines. BOSL2 is a gitlink, so it counts as 1 line.
1. `.gitmodules`, submodule, BSD-2 text, `libs/README.md`, `.editorconfig`, README license row (~60 lines).
2. Makefile, smoke part, fixture, ADR-0002 and its index row, `hardware/cad/README.md`, `config.yaml` (~260 lines).
3. `cad.yml` and the README usage docs (~90 lines).

Rollback reverts the PRs in reverse order.

## Apply-time Findings (PR 2)

- Image pin is `openscad/openscad:dev.2026-01-19@sha256:0af06bc2aa7a45d18b01a23cfb9dae6dddcd9542611e7be50edea6beb3b52fa7`. Newer tags `dev.2026-09-23` and `dev.2026-09-28` fail PNG export ("Can't create OffscreenView: Unable to initialize GLAD"); `dev.2026-01-19` renders with no WARNING.
- In-image binary is `/usr/local/bin/openscad`; `--entrypoint openscad` works.
- The `.d` first line is `build/stl/smoke.stl: \` as designed.
- Make 3.81 prints nothing on an up-to-date `make stl` (see Testing Strategy).
- The gate macro also runs `rm -f $(1)` on failure, so a failed build leaves no output.
- An internal `TC` variable holds the resolved toolchain, so `TOOLCHAIN=` on the command line is never overridden.

## Open Questions

- [ ] At apply time, confirm the exact `dev.<date>` tag, its index digest, the in-image binary name and path (`--entrypoint openscad`), and that EGL PNG rendering does not print a `WARNING`.
- [ ] Confirm the app bundle name that `openscad@snapshot` installs on macOS. Users can set `OPENSCAD=` otherwise.
- [ ] The spec phase must allow `tools/cad/fixtures/*.scad` in the `repo-structure` delta.
