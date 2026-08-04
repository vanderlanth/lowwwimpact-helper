# lowwwimpact — Evaluate a site

Audit a live site and evaluate it against the 27 lowwwimpact sustainability criteria. One command,
one pipeline.

Usage: `/lowwwimpact-evaluate <url>` — or add `--debug` for measurement-only.

Run the **Evaluate Mode Workflow** defined in the skill (single source of truth): `SKILL.md` →
section **Evaluate Mode Workflow**. The summary below is for orientation.

## Prerequisites

- **Playwright CLI** — `playwright-cli --help` must work. Install with
  `npm install -g @playwright/cli@latest && playwright-cli install-browser`.
- **Lighthouse** via `npx` (Node.js ≥ 18). If unavailable, scores are omitted and noted.

## Pipeline

1. **Journeys** — ask for 1–2 user journeys, or accept `skip`.
2. **Discovery** — crawl the landing page plus 3–5 inner pages, each in a fresh session, and write
   `workspace/discovery.md`.
3. **Six audit phases** — images, media & fonts, JavaScript, CSS & HTML, network & infrastructure,
   carbon & performance. Mutually independent: delegate in parallel where the host supports
   subagents, otherwise run in sequence. Each writes to `workspace/phases/`.
4. **Synthesis** — merge into `workspace/sustainability-report.md`, ranked by KB savings.
5. **Criteria** — evaluate all 27 against the audit evidence and write
   `workspace/lowwwimpact-evaluation.json`.

Every run measures cold. There is no caching or artifact reuse — the measurement semantics depend
on genuine cold loads, and reused numbers would not be comparable across runs.

## Output contract

**`workspace/lowwwimpact-evaluation.json` must match `references/valid-example.json` exactly.**
It is consumed downstream; a structural mismatch is a failed run regardless of how good the
findings are. Read that file before writing.

The two traps: `pages` and `journeys` are **objects** keyed `page-1` / `journey-1`, not arrays,
even though `evaluation` right beside them genuinely is an array. And `lighthouse_recap` and
`recommendations` are required top-level keys even when the underlying data is thin.

## `--debug`

Measurement-only. Runs auth setup plus weight and Lighthouse measurement, writes
`workspace/debug-weights.json`, prints the per-page summary, and stops. Does not load criteria, run
the evaluator, or run any audit phase. Use it to confirm a login flow works before committing to a
full run.

## Pages behind a login

Put credentials in a `.env` at the project root — variables matching `*_USER` / `*_LOGIN` /
`*_EMAIL` and `*_PASS` / `*_PASSWORD`. The first run detects the login redirect, logs in, and saves
`workspace/auth-state.json` for reuse. Keep both files out of version control.
