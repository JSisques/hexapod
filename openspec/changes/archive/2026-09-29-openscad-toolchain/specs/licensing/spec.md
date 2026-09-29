# Delta for Licensing

## ADDED Requirements

### Requirement: Third-party library licenses

Third-party code under `libs/*` MUST keep its upstream license. For BOSL2 (BSD-2-Clause), the full text MUST exist at `LICENSES/BSD-2-Clause.txt`, and `libs/README.md` MUST note that `libs/BOSL2` is BSD-2-Clause and not covered by the repo's own licenses.

#### Scenario: BOSL2 license present

- GIVEN the tree after the change
- WHEN `LICENSES/BSD-2-Clause.txt` is read
- THEN it exists, is non-empty, and contains the BSD 2-Clause text

#### Scenario: Library note

- GIVEN `libs/README.md`
- WHEN it is read
- THEN it states `BSD-2-Clause` for `libs/BOSL2`
