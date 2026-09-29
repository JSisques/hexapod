# Decision Records Specification

## Purpose

Define where architecture decisions live, their format, and the first ADR.

## Requirements

### Requirement: ADR location and naming

ADRs MUST live in `docs/adr/` and be named `NNNN-kebab-title.md` with a zero-padded sequence number.

#### Scenario: First ADR named correctly

- GIVEN `docs/adr/`
- WHEN its files are listed
- THEN `0001-repository-layout-and-licensing.md` exists

### Requirement: ADR format

Each ADR MUST include Title, Status, Context, Decision, and Consequences sections.

#### Scenario: Sections present

- GIVEN `docs/adr/0001-repository-layout-and-licensing.md`
- WHEN its headings are read
- THEN all five sections exist and Status is `Accepted`

### Requirement: ADR-0001 content

ADR-0001 MUST record: the per-domain layout (Option B), the STL/PNG policy (generated in CI, not committed, no Git LFS), and split licensing (CC-BY-SA-4.0 hardware, MIT firmware/software). It SHOULD list deferred decisions (MCU, servo/driver, languages, KiCad, hosting).

#### Scenario: Decisions recorded

- GIVEN ADR-0001
- WHEN searched for "Option B", "LFS", "CC-BY-SA-4.0", and "MIT"
- THEN each term appears in the Decision section

#### Scenario: Deferred items noted

- GIVEN ADR-0001
- WHEN read
- THEN MCU, servo, and language choices are marked as deferred, not decided
