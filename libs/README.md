# Libraries

Third-party libraries, pinned as git submodules.

| Library | Path | Upstream | License (SPDX) | Pin |
| --- | --- | --- | --- | --- |
| BOSL2 | `libs/BOSL2` | https://github.com/BelfrySCAD/BOSL2 | `BSD-2-Clause` | `402be424319c2ed1bd8c11f29a71fe22b16b06b2` (v2.0.763) |

Initialize after cloning (or clone with `--recurse-submodules`):

```sh
git submodule update --init libs/BOSL2
```

Bump the pin:

```sh
git -C libs/BOSL2 fetch origin
git -C libs/BOSL2 checkout <new-sha>
git add libs/BOSL2
```

Then update the pin in this table and in ADR-0002.

Each library keeps its own upstream license and is not covered by this repository's own licenses (CC-BY-SA-4.0 and MIT). Check the license shipped inside each library directory before reuse or redistribution. The BOSL2 license text is in [`LICENSES/BSD-2-Clause.txt`](../LICENSES/BSD-2-Clause.txt).
