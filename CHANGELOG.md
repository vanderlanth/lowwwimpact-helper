# Changelog

All notable changes to this skill are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Every Playwright session failed to open on a machine without a system Chrome install.**
  `playwright-cli -s=<name> open` defaults to the `chrome` channel and aborts with *"Chromium
  distribution 'chrome' is not found at /Applications/Google Chrome.app"*. Only two of sixteen
  call sites passed `--browser=chromium`; the other fourteen — including the first step of
  `/measure-page-weight` and every audit phase — would stop the run at its first command. All
  sixteen now pass the flag.

- **Media files were counted twice, inflating page weight non-deterministically.** Browsers stream
  media as several HTTP Range requests, and `getKB` summed each 206 response body as if it were a
  separate download. On `liip.ch/…/liipgpt` a 1 MB video was counted as ~2 MB, and because the
  number of chunks that complete varies per run, deferred weight swung between ~3075 KB and
  ~4062 KB across runs. 206 responses now have their byte ranges unioned per URL and counted once;
  200 responses are still summed, since a genuine second full fetch really did cross the wire
  twice. The duplicate-request detector skips 206s for the same reason — it had been reporting
  ~987 KB "wasted" on a file fetched once. Three consecutive runs after the fix: 1900/3074,
  1899/3072, 1900/3072.

- **Full evaluations reported page weights far below reality.** `/measure-page-weight` measured
  correctly, but evaluate mode never used it. The carbon-performance phase carried its own inline
  copy of the measurement — a stale fork missing the cookie-consent click (consent-gated
  third-party bytes never loaded), `deviceScaleFactor: 2` (1x instead of 2x responsive images),
  `Network.clearBrowserCache` on a session reused across the Step 6 comparison pages (inner pages
  measured warm, shared CSS/JS/font bytes counted as 0), and `state-load` of `auth-state.json`
  (authenticated sites measured the login page). It then wrote those numbers to
  `workspace/page-weights.json`, which made the evaluator skip its own Step 3.5 measurement and
  ship the undercount to the report.

### Changed

- **One measurement implementation, in `commands/measure-page-weight.md`.** The
  carbon-performance phase now invokes `/measure-page-weight` and reads
  `workspace/page-weights.json` instead of measuring; it no longer writes that file. Its remaining
  Playwright work — the per-asset-type breakdown — opens a fresh session per page and is explicitly
  labelled proportional evidence, never a total.
- **Lighthouse runs once.** The carbon phase reads scores from `page-weights.json`; its standalone
  Lighthouse invocation is now a documented fallback for a URL that was never measured.
- **`references/playwright-guide.md` no longer reproduces the standalone measurement snippet** —
  it points at the command and lists the six requirements a correct measurement must satisfy. The
  journey measurement code, which is current, stays.
- **The evaluator validates the weights cache before trusting it** (`meta.source` must be
  `measure-page-weight`, all 8 keys present, no nulls, URLs covered). A cache from any other
  producer is discarded and re-measured, so a future fork cannot silently win again.

## [3.0.0] — 2026-08-04

Restructure around three named modes, portable across hosts.

### Changed

- **Modes are named, not numbered:** **passive**, **evaluate**, **eco-specs**. The numbering had
  changed twice, which made it the worst possible way to name things people type.
- **Evaluate absorbs the old review and evaluate modes** into one pipeline: discovery → six audit
  phases → synthesis → measurement → criteria. One command, two outputs
  (`sustainability-report.md`, `lowwwimpact-evaluation.json`). The old three-tier evidence chain
  existed only to cope with the audit not having run; inside one pipeline it is unnecessary.
- **`agents/` → `phases/`,** split into `phases/evaluate/` and `phases/eco-specs/`. Each phase
  declares `## Inputs` and `## Outputs`, reads and writes only fixed `workspace/` paths, and takes
  no parameters — so a host without subagents runs them in sequence for the same result. The
  delegate-if-available rule is stated once in `SKILL.md` instead of per file.
- **Per-phase reports moved** from `workspace/agents/` to `workspace/phases/`.
- **`companion.md` → `passive.md`,** rewritten as a router: it names the integration moment and
  points at the numbered block in `references/ecodesign-requirements-concise.md` rather than
  restating the guidance at lower resolution.
- **Install is host-aware.** It detects Claude Code, opencode, or Cursor from where the skill sits
  and copies commands to that host's directory. Fixes a live bug: a Cursor user following the
  README cloned to `.cursor/skills/` and init halted because it only looked in `.claude/skills/`.
- **Passive mode installs into `AGENTS.md`** by injection between
  `<!-- lowwwimpact:passive:start -->` / `<!-- lowwwimpact:passive:end -->` markers, replaced on
  re-run. `CLAUDE.md` gets a single `@AGENTS.md` line on Claude Code. Injection replaces the old
  `@path` import because that syntax is Claude Code-only; the trade-off is that the block goes
  stale until init is re-run.
- **Audit findings now cite both** a requirement block and a fix command — the block works in any
  host and carries the documentation links, the command executes the fix where a command runner
  exists.

### Added

- **`references/valid-example.json` is now wired in as the evaluate output contract.** It was in
  the repo but referenced by nothing, so the evaluator had been assembling output from partial
  inline fragments that never showed `lighthouse_recap` or `recommendations`. It is now a required
  input, with the shape documented in both `SKILL.md` and the evaluator — including that `pages`
  and `journeys` are objects keyed `page-N` / `journey-N`, not arrays.
- **`scripts/validate-evaluation.py`** — enforces that contract. Non-zero exit means the run is
  invalid regardless of the quality of its findings.
- **`/lowwwimpact-evaluate` and `/lowwwimpact-eco-specs`** commands, so modes are invoked the same
  way in every host rather than depending on Claude Code skill auto-discovery.
- Host and model support documented honestly in `README.md`: hosts are portable, but the criteria
  evaluation needs a large-context model and will not work on a small local one.

### Removed

- **BREAKING — fix mode is gone.** No `workspace/fix-plan.md`. The synthesizer keeps its
  KB-ranked Fix Command Summary inside the audit report; it simply no longer feeds a second mode.
- **BREAKING — numbered mode invocations no longer resolve.** "mode 1" … "mode 4" are not
  recognized; use the names or the commands.

### Unchanged, deliberately

Measurement is frozen. `references/auth-measure-pipeline.md`, `commands/measure-page-weight.md`,
and every measurement step in the evaluator received label renames only — no logic edits. Every run
still measures cold, with no artifact reuse, because the semantics depend on genuine cold loads and
reused numbers would not be comparable across runs.

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
