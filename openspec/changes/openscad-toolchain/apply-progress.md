# Apply Progress: openscad-toolchain

## PR 1 (branch feat/openscad-toolchain-1-bosl2): tasks 1.1-1.6 done

- 1.1 BOSL2 submodule added at libs/BOSL2, pinned to 402be424319c2ed1bd8c11f29a71fe22b16b06b2 (v2.0.763, tip of origin/master at apply time).
- 1.2 LICENSES/BSD-2-Clause.txt copied with `cp` from libs/BOSL2/LICENSE (verified with `cmp`).
- 1.3 libs/README.md: table, init and bump commands.
- 1.4 .editorconfig: `[.gitmodules]` with `indent_style = tab`.
- 1.5 README.md: `libs/BOSL2` BSD-2-Clause license row.
- 1.6 Verified: `git submodule status libs/BOSL2` shows the pinned SHA; license file exists.

Not committed (per instructions). Remaining: PR 2 (2.1-2.12), PR 3 (3.1-3.4).
