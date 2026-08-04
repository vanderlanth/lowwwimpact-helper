# Changelog

All notable changes to this skill are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] — 2026-08-04

### Changed

- **Mode 4 and Mode 5 are merged into a single Mode 4: Eco-Design Specs & Review.** Discovery runs
  once and writes `workspace/element-inventory.json`; two writer agents then consume it in parallel
  to produce `workspace/dev-specs.md` and `workspace/eco-review.md`. Both outputs are produced on
  every run — there are no flags and no sub-modes.
- Four agents replace the previous four, split by responsibility rather than by audience:
  `figma-inventory-agent.md` and `code-inventory-agent.md` discover; `dev-specs-writer.md` and
  `designer-review-writer.md` write. The Figma annotation-extraction logic, previously duplicated
  across two agents, now exists in one place, and a Figma frame is fetched once instead of twice.
- Developer specs are now sourced from `references/ecodesign-requirements-concise.md` (41 blocks
  with curated documentation links). The per-section WebSearch step is removed — reference links
  come from that file, which makes output faster and deterministic.
- Corrected the 1.0.0 entry below: Evaluate is Mode 2 and Fix is Mode 3, not the reverse.

### Removed

- **BREAKING — Mode 5 no longer exists.** Its trigger words ("eco review", "designer review",
  "design review", "review for designers") now route to Mode 4. There is no alias or deprecation
  shim; prompts naming "mode 5" explicitly will not resolve.
- **BREAKING — PDF export is dropped.** No `md-to-pdf` invocation, no `workspace/eco-review.pdf`.
  The designer review is delivered as markdown only.
- `references/figma-specs.md` — superseded by `references/ecodesign-requirements-concise.md`.
- `agents/mode-4-specs/` and `agents/mode-5-designer-review/`.

## [1.1.0] — 2026-07-22

Recorded retroactively — these modes shipped without a changelog entry.

### Added

- **Mode 0: Init** — per-project setup: copies fix commands into `.claude/commands/` and wires the
  companion `@import` into `CLAUDE.md`
- **Mode 4: Specs** — developer-facing eco-design specs from Figma frames or a code project
- **Mode 5: Designer Eco-Review** — designer-facing per-screen review and PDF from Figma frames or
  a code project
- `companion.md` — always-on sustainability nudges during normal development
- `evaluate --debug` measurement-only variant and the shared auth + measure pipeline

## [1.0.0] — 2026-03-10

### Added

- Multi-agent sustainability audit system with 6 specialized audit agents + synthesizer
- **Mode 1: Review** — live Playwright-based site inspection producing a carbon-graded report
- **Mode 2: Evaluate** — structured lowwwimpact criteria assessment (27 MVP criteria from WSG)
- **Mode 3: Fix** — guided walkthrough delegating to 12 `/xyz-optim` companion commands
- Reference files: carbon measurement model, media optimization, code efficiency, performance budgets, sustainability checklist, Playwright guide, report template
- `lowwwimpact-criteria.json` with pre-filled `default_answer` and `default_description` for each criterion
- Evaluator agent with 20+ Playwright inspection snippets for automated checks
