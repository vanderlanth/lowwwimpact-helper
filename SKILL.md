# lowwwimpact-helper

A sustainability skill for web projects. It audits a live site with Playwright and evaluates it
against the lowwwimpact criteria, generates paired eco-design deliverables from Figma frames or a
codebase, and keeps a light sustainability lens active during everyday development.

## Modes

Three modes. Named, not numbered — the numbering changed twice and broke people's prompts.

| Mode | Trigger | Produces |
|---|---|---|
| **Passive** | Always on after install — never invoked | Lower-impact suggestions at the moment you add an image, font, embed, dependency, or animation |
| **Evaluate** | `/lowwwimpact-evaluate <url>`, or "evaluate", "audit", "lowwwimpact", "criteria" + a URL | `sustainability-report.md` and `lowwwimpact-evaluation.json` |
| **Eco-Specs** | `/lowwwimpact-eco-specs`, or "eco specs", "dev specs", "eco review", "designer review" | `dev-specs.md` and `eco-review.md` |

### Passive

Installed into the project's `AGENTS.md` by the install workflow, so it is in context for every
session without being invoked. It offers the lower-impact option at integration moments and points
at the relevant block of `references/ecodesign-requirements-concise.md`. Advisory only — it never
blocks, and it proceeds with the developer's choice.

### Evaluate

One pipeline, one command: crawl the site, run six audit phases, synthesize a report, measure page
weight and Lighthouse, then evaluate the 27 lowwwimpact criteria. Requires Playwright and a live
URL.

Two outputs. `workspace/sustainability-report.md` is the human-facing audit with findings ranked by
KB savings. `workspace/lowwwimpact-evaluation.json` is the structured criteria assessment — **its
structure is a hard contract defined by `references/valid-example.json`.**

`evaluate --debug` is the measurement-only variant: auth plus weight and Lighthouse, nothing else.
Use it to verify a login flow works before running the full pipeline.

### Eco-Specs

Runs discovery once and writes two audience-specific files from it. No flags, no sub-modes — every
run produces both. Does not require Playwright or a live URL.

**With `figma.com` frame URLs:** inspects each frame via the Figma MCP — annotations first, then
visual detection. **Without:** scans the current project — project-wide detection plus a per-screen
scan of 2–3 representative templates.

Either path writes `workspace/element-inventory.json`, which both writers consume:

| Output | Audience | Content |
|---|---|---|
| `workspace/dev-specs.md` | Developers | Technical requirements per element type, sourced from `references/ecodesign-requirements-concise.md` with its curated documentation links |
| `workspace/eco-review.md` | Designers | Per-screen findings against the eco-design principles, key actions, and a design sobriety section. No code, no developer jargon. |

---

## How this skill runs

The skill is plain markdown. It is designed to work in any host that can read files, run shell
commands, and follow a multi-step document — Claude Code, opencode, Cursor, and others.

**Phases are self-contained.** Each file in `phases/` declares its `## Inputs` and `## Outputs` and
reads and writes only the `workspace/` paths named there. No parameters are passed in.

**Delegate if you can, run inline if you can't.** This rule applies everywhere and is stated only
here:

- The six evaluate audit phases are mutually independent. Delegate them in parallel where the host
  supports subagents; otherwise run them in sequence. The result is identical either way.
- The two eco-specs writers are likewise independent of each other, but both depend on the
  inventory phase completing first.
- Everything else is sequential by nature.

**Model capability varies.** Each audit phase and each eco-specs phase carries ~2k tokens of
instruction and runs comfortably on modest models. The criteria evaluation is much heavier — the
evaluator plus the criteria file is ~20k tokens before any page data — and needs a large-context,
capable model to produce a valid result. See the portability notes in `README.md`.

---

## Prerequisites

**Playwright CLI** — required by evaluate. Not needed for eco-specs or passive.

```bash
npm install -g @playwright/cli@latest
playwright-cli install-browser
playwright-cli install --skills
```

Verify with `playwright-cli --help`.

**Lighthouse CLI** — used by evaluate for performance, accessibility, best-practices, and SEO
scoring. Runs via `npx`; no install needed with Node.js ≥ 18. Verify: `npx lighthouse --version`.
If unavailable, Lighthouse scores are omitted and noted in the report.

**Figma MCP** — required by eco-specs only when Figma frame URLs are given.

## Inputs

1. **Target URL** — required for evaluate
2. **Monthly pageviews** (optional) — for annual carbon estimates (default: 10,000)
3. **Focus areas** (optional) — which audit domains matter most
4. **Context** (optional) — app description, constraints, hosting provider
5. **Criteria file** (optional) — defaults to `references/lowwwimpact-criteria.json`
6. **User journeys** (optional) — 1–2 natural-language task descriptions. Evaluate asks before
   proceeding if not supplied.

If optional inputs are absent, use reasonable defaults and note the assumptions.

---

## Phase Roster

### Evaluate phases

| Phase | Focus | Tools | Fixes map to |
|---|---|---|---|
| **Images** | Formats, compression, responsive, lazy loading, alt text | Playwright CLI | block 1–3 · `/image-optim` |
| **Media & Fonts** | Video facades, font loading, WOFF2, animations | Playwright CLI | blocks 6–13 · `/media-optim`, `/typo-optim`, `/animation-optim` |
| **JavaScript** | Bundle size, loading strategy, native APIs, code splitting | Playwright CLI | blocks 31–32 · `/native-feature-optim`, `/performance-optim` |
| **CSS & HTML** | CSS size, critical CSS, semantic HTML, dark mode, reduced-motion | Playwright CLI | blocks 29–30 · `/native-feature-optim`, `/seo-optim` |
| **Network & Infrastructure** | Caching, compression, third-party domains, service worker | Playwright CLI, WebSearch | blocks 14–18, 34–36 · `/cache-compression-optim`, `/third-party-optim` |
| **Carbon & Performance** | Page weight budget, carbon calculation, hosting | Playwright CLI, WebFetch | block 36 · `/performance-optim` |
| **Synthesizer** | Merges the six reports into the ranked report | — | — |
| **Evaluator** | Maps findings to the 27 criteria, writes the contract JSON | Playwright CLI, WebFetch | — |

Files live in `phases/evaluate/`.

**Findings cite both a block and a command.** The requirement block in
`references/ecodesign-requirements-concise.md` explains what and why and carries documentation
links — it works in every host. The `/xyz-optim` command executes the fix where a command runner
exists. Write findings as `→ block 1 (Raster images) · /image-optim`.

### Eco-specs phases

| Phase | Input | Writes |
|---|---|---|
| **Figma Inventory** | Figma frame URLs | `workspace/element-inventory.json` |
| **Code Inventory** | Project directory | `workspace/element-inventory.json` |
| **Dev Specs Writer** | the inventory | `workspace/dev-specs.md` |
| **Designer Review Writer** | the inventory | `workspace/eco-review.md` |

Files live in `phases/eco-specs/`. One inventory phase runs, then both writers.

### Fix command catalogue

These live in `commands/` and are copied into the host's command directory at install. The skill
references them by name — it contains no fix logic itself.

| Command | Domain |
|---------|--------|
| `/lowwwimpact-evaluate` | Run the evaluate pipeline |
| `/lowwwimpact-eco-specs` | Run the eco-specs pipeline |
| `/lowwwimpact-init` | Install into the current project |
| `/measure-page-weight` | Page weight + Lighthouse → `workspace/page-weights.json` |
| `/image-optim` | Image formats, responsive, lazy loading, compression, CLS |
| `/media-optim` | Video/audio: autoplay, preload, formats, facades, accessibility |
| `/cms-media-optim` | CMS upload constraints, auto-processing, editor guardrails |
| `/typo-optim` | WOFF2, subsetting, self-hosting, font-display, system fallback |
| `/animation-optim` | GPU-safe properties, prefers-reduced-motion, no GIFs |
| `/third-party-optim` | Facades for YouTube/Vimeo/Maps/Calendly/social, max 4 domains |
| `/native-feature-optim` | Native HTML/CSS over JS: dialog, details, scroll-snap, popover |
| `/cache-compression-optim` | Gzip/Brotli, Cache-Control, hashed filenames |
| `/performance-optim` | Page weight budget, Lighthouse, bundle analysis, CI enforcement |
| `/reusable-components-optim` | Duplicate CSS/JS detection, shared utilities, unused exports |
| `/compatibility-optim` | Progressive enhancement, @supports, polyfills, degradation |
| `/seo-optim` | Titles, descriptions, canonical, Open Graph, JSON-LD |

---

## Install Workflow

Finishes per-project setup after the skill folder has been cloned into the project. Idempotent —
safe to re-run after an update. Also available as `/lowwwimpact-init` once installed.

### Step 1 — Detect the host

Find where the skill actually lives and derive the destinations:

| Skill directory | Host | Commands → | Passive → |
|---|---|---|---|
| `.claude/skills/lowwwimpact-helper/` | Claude Code | `.claude/commands/` | `AGENTS.md`, plus `@AGENTS.md` in `CLAUDE.md` |
| `.opencode/lowwwimpact-helper/` | opencode | `.opencode/commands/` | `AGENTS.md` |
| `.cursor/skills/lowwwimpact-helper/` | Cursor | `.cursor/commands/` | `AGENTS.md` |

If more than one matches, ask which host to install for. If none matches, ask the user where the
skill lives rather than guessing.

### Step 2 — Copy the commands

Plain-copy `<skill>/commands/*.md` into the host's command directory, creating it if needed and
overwriting existing files so updates refresh. This includes `lowwwimpact-init.md` itself.

Do not add YAML frontmatter. The files are plain markdown precisely so the same file works in
every host.

### Step 3 — Install passive mode into `AGENTS.md`

Ensure `<project>/AGENTS.md` exists, then inject the contents of `<skill>/passive.md` between
marker comments:

```markdown
<!-- lowwwimpact:passive:start -->
…contents of passive.md…
<!-- lowwwimpact:passive:end -->
```

**Idempotent by replacement**: if both markers are already present, replace everything between
them. Only append the block when the markers are absent. Never write the block twice.

Content is injected rather than imported because `@path` imports are Claude Code syntax and the
`AGENTS.md` convention has no portable import mechanism. The cost is that the block goes stale when
the skill updates — re-running install refreshes it, the same way it refreshes the commands.

### Step 4 — Claude Code only: point `CLAUDE.md` at `AGENTS.md`

Ensure `<project>/CLAUDE.md` contains the single line `@AGENTS.md`. Skip if already present. This
keeps one source of passive guidance across all hosts.

### Step 5 — Report

List the commands copied, the host detected, and whether the passive block was added or replaced.

Everything installs at the **project** level — nothing is written to `~/.claude` or the equivalent.

---

## Evaluate Mode Workflow

One pipeline. Every run measures cold — there is no artifact reuse or caching layer, because the
measurement semantics depend on genuine cold loads and reused numbers would not be comparable.

### Step 0: Collect user journeys

If no journeys were provided in the prompt, ask:

> "Do you have 1–2 user journeys to include in this evaluation?
> Example: 'From the homepage, find a product and add it to the cart, then visit the cart.'
> You can also say **skip** to proceed without journey data."

If the user says skip, set journeys = [] and continue.

### Step 1: Setup

1. Confirm the target URL and any user-provided context
2. Ensure Playwright CLI is installed (`playwright-cli --help`)
3. Create `workspace/` with a `phases/` subdirectory for per-phase reports

### Step 2: Discovery

Before the audit phases, crawl the site to build a shared resource inventory.
**Each page is measured in a fresh session** (no cache from previous pages):

1. For each page to discover (landing page + 3–5 key inner pages):
   a. Open a new named session: `playwright-cli -s=disc-N open <url>`
      Then immediately set the standard audit viewport: `playwright-cli -s=disc-N resize 1440 760`
   b. Wait for the page to fully load + 3 seconds (catches late-triggered resources):
      ```bash
      playwright-cli -s=disc-N eval "new Promise(r => { if (document.readyState === 'complete') r(); else window.addEventListener('load', r, {once: true}); })"
      playwright-cli -s=disc-N eval "new Promise(r => setTimeout(r, 3000))"
      ```
   c. Capture network data and snapshot (no screenshots)
   d. Measure page weight via Performance API (conservative — cross-origin resources may be 0)
   e. Close the session: `playwright-cli -s=disc-N close`
   f. Increment N and repeat for the next page
2. Build a resource inventory from the landing page session data
3. Build a simple sitemap of discovered pages
4. Save to `workspace/discovery.md`

> **Note on discovery weights**: The Performance API cannot measure cross-origin resources
> without a `Timing-Allow-Origin` header — third-party bytes (analytics, consent managers,
> CDN assets from external domains) may appear as 0. Report weights as conservative estimates
> and note this limitation in `discovery.md`. Lighthouse-based measurements in the
> carbon-performance phase provide the authoritative figures.

Discovery template:

```markdown
# Discovery: [Site Name]

## Pages Discovered
| Page | URL | Weight | Requests |
|------|-----|--------|----------|
| Home | / | X KB | N |
| About | /about | X KB | N |
| ... | ... | ... | ... |

## Resource Inventory (Landing Page)
| Type | Count | Total KB |
|------|-------|----------|
| Images | N | X KB |
| JavaScript | N | X KB |
| CSS | N | X KB |
| Fonts | N | X KB |
| HTML | 1 | X KB |
| Other | N | X KB |
| **Total** | **N** | **X KB** |

## Third-Party Domains
| Domain | Requests | Total KB | Purpose |
|--------|----------|----------|---------|
| ... | N | X KB | ... |

## Navigation Structure
[Simple sitemap tree]
```

This discovery output is shared with all audit phases as context.

### Step 3: Audit phases

Run the six audit phases. They are mutually independent — delegate them in parallel where the host
supports it, otherwise run them in sequence.

Each phase receives, by reading it:

- The target URL
- `workspace/discovery.md`
- Its own instructions from `phases/evaluate/`
- `references/playwright-guide.md` and the relevant files in `references/`

Each phase:

1. Opens its own Playwright CLI session (`-s=<phase-name>`)
2. Navigates the relevant pages
3. Inspects resources, network data, DOM structure, and response headers
4. Takes snapshots as evidence — **no screenshots**, they are not needed here
5. Writes findings to `workspace/phases/<name>-audit.md` with estimated KB savings, and tags each
   finding with its requirement block and fix command

### Step 4: Synthesis

The synthesizer phase:

1. Reads all six phase reports from `workspace/phases/`
2. Deduplicates overlapping findings (does not double-count savings)
3. Calculates the sustainability grade using the SWD carbon model
4. Builds the page weight breakdown table
5. Maps every finding to its requirement block and fix command
6. Ranks findings by bandwidth savings (KB) and implementation effort
7. Creates the Fix Command Summary table
8. Creates the Sprint Plan
9. Calculates improvement potential (projected grade after fixes)
10. Writes `workspace/sustainability-report.md` following `references/report-template.md`

### Step 5: Load criteria

Read the criteria file (default: `references/lowwwimpact-criteria.json`). Parse the `criteria`
array. Skip entries whose `id` starts with `TODO` — those are unfilled placeholders.

### Step 6: Evaluate each criterion

The evaluator phase reads `workspace/sustainability-report.md` and the reports in
`workspace/phases/` as its evidence, plus direct Playwright inspection where needed. Each criterion
has a `report_mapping` field pointing at the relevant phase report.

Process each criterion by its `automatable` flag and `type`:

- **`automatable: false`** → `answer: null`, note explains why human judgment is needed
- **`automatable: true`** → evaluate from report evidence and/or Playwright inspection
- **`automatable: "partial"`** → answer what can be confirmed, leave the rest for human review

Answer types:

- **boolean** → `true` or `false`
- **range** → a number based on measurable data
- **numeric** → a count based on measurable data
- **checkboxes** → array of strings from the `answers` list that are confirmed true

The 27 criteria may be reasoned about in groups to keep context manageable. **Assembling the output
document stays a single pass**, because splitting assembly threatens the output contract.

### Step 7: Write the evaluation JSON

**The structure of `workspace/lowwwimpact-evaluation.json` is a hard contract defined by
`references/valid-example.json`.** Read that file and match it exactly before writing. It is
consumed downstream; a structural mismatch is a failed run regardless of how good the findings are.

| Key | Type | Notes |
|---|---|---|
| `meta` | object | `url`, `urls[]`, `date`, `lighthouse`, `criteria_version`, `total_criteria`, `evaluated`, `skipped_subjective`, `na` |
| `evaluation` | **array of 27** | each `{ id, type, question, answer, note }` |
| `pages` | **object** keyed `page-1`, `page-2`, … | **not an array** |
| `lighthouse_recap` | string | required top-level key |
| `recommendations` | object | `executive_summary` + `top_5` |
| `journeys` | **object** keyed `journey-1`, … | **not an array** |

`pages` and `journeys` being objects keyed by index string, next to `evaluation` which genuinely is
an array, is the trap. Do not normalise them.

**Validate before presenting the result:**

```bash
python3 scripts/validate-evaluation.py workspace/lowwwimpact-evaluation.json
```

A non-zero exit means the output violates the contract. Fix the structure and re-run. Never present
an evaluation that fails this check.

Each page entry in `pages` MUST contain exactly these 8 keys — no more, no fewer. NEVER rename them, prefix them, or add extra keys (e.g. do NOT add `fcp`, `lcp`, `tbt`, `cls`, `co2_g`, `grade`, `lighthouse_performance`, `total_kb`, or any other field):
- `url` — full page URL
- `title` — page title from `document.title`
- `performance` — Lighthouse performance score (0–100)
- `accessibility` — Lighthouse accessibility score (0–100)
- `best_practices` — Lighthouse best practices score (0–100)
- `seo` — Lighthouse SEO score (0–100)
- `initial_weight_kb` — transfer size on first load in KB
- `deferred_weight_kb` — total KB measured after scrolling to the bottom of the page

`journeys` contains one entry per user journey provided (keys `journey-1`, `journey-2`, …).
Each entry has the original `description` and an ordered `pages` array of `{ url, name, kb }`.
`name` is derived from `document.title`, stripped of the site suffix and shortened to 2–3 words.
`kb` is the total transfer size of that page measured during the clean measurement pass.
Omit the `journeys` key entirely if the user skipped journey input.

`meta.lighthouse` is `"carbon-performance-audit"` when data came from the carbon-performance phase,
`"standalone"` when Lighthouse was run directly, or `null` (with `pages` omitted)
when no Lighthouse data was available.

`lighthouse_recap` is a plain string (max 600 characters) written after all 27 criteria are
evaluated. It focuses on the lowest-scoring Lighthouse category and cross-references audit
findings and failing criteria to explain causes. When all categories average ≥ 90, it gives
measured positive feedback and may suggest a stretch goal. Set to `null` when no Lighthouse
data is available.

`recommendations.executive_summary` is a plain string (max 600 characters) giving an overall
verdict on the evaluation — whether the site is doing well, main failing areas, and what to
prioritise. `recommendations.top_5` is an array of up to 5 criterion IDs that failed and would
add the most points if fixed, ranked by potential gain (checkboxes with more unchecked options
rank higher; other types count as 1).


Present the output to the user with a summary: how many criteria were evaluated, how many need
human review, and any notable pass/fail highlights.

---

## Eco-Specs Mode Workflow

Discovery runs once; both writers consume its output. No flags — every run produces both
`workspace/dev-specs.md` and `workspace/eco-review.md`.

### Step 1: Collect inputs and detect path

- Accept optional context: project name, CMS in use, known tech stack, target audience
- **Check whether the user provided any `figma.com` URLs:**
  - If yes → **Figma path**
  - If no → **Code path** (current working directory)

### Step 2: Build the inventory

**Figma path** — run `phases/eco-specs/figma-inventory.md` with the frame URLs. Per frame it calls
`get_screenshot` and `get_design_context` once, extracts the annotation index first, then fills
remaining categories by visual detection.

**Code path** — run `phases/eco-specs/code-inventory.md` against the current working directory. It
runs project-wide grep passes for boolean presence, then selects 2–3 representative page templates
and scans each individually as a "screen".

Either writes `workspace/element-inventory.json`. Do not proceed until it exists.

### Step 3: Write both outputs

The two writers are independent of each other — delegate them in parallel where the host supports
it, otherwise run them in sequence. Neither re-inspects Figma or the codebase; both read only the
inventory JSON.

| Phase | Reads | Writes |
|---|---|---|
| `phases/eco-specs/dev-specs-writer.md` | inventory `project.detected` + `references/ecodesign-requirements-concise.md` + `references/sustainability-checklist.md` | `workspace/dev-specs.md` |
| `phases/eco-specs/designer-review-writer.md` | inventory `screens[]` + `references/eco-design-principles-for-designers.md` + `references/design-sobriety-principles.md` | `workspace/eco-review.md` |

The dev-specs writer does **not** run WebSearch — every reference it emits comes from the
`**Documentation**` blocks already curated in `references/ecodesign-requirements-concise.md`.

### Step 4: Report

Present all three paths: the inventory JSON, `dev-specs.md`, and `eco-review.md`. Summarize in one
line how many screens were analyzed and how many element categories were detected.

---

## Evaluate Debug Workflow (`evaluate --debug`)

Measurement-only path. The coordinator runs this directly — it does **not** run the evaluator
phase, load criteria, or run any audit phase. Goal: confirm auth + weight/Lighthouse measurement
work, then stop so the user can inspect the result and fix the pipeline.

1. **Collect URLs** — take the URL(s) explicitly provided by the user, in order. No journey
   discovery, no crawling.
2. **Run the shared pipeline** (`references/auth-measure-pipeline.md`):
   - **Phase A — Auth Setup**: detect a login redirect; if found, log in and write
     `workspace/auth-state.json`. For a public site this is a no-op.
   - **Phase B — Measure**: run `/measure-page-weight <url...> --out workspace/debug-weights.json`.
3. **Set `meta.source` to `"debug"`** in the written file (same per-page schema as
   `page-weights.json`: the 8 keys `url`, `title`, `performance`, `accessibility`, `best_practices`,
   `seo`, `initial_weight_kb`, `deferred_weight_kb`).
4. **Print the per-page summary** (initial/deferred KB + the 4 scores) and stop. Do not load
   criteria, do not write `lowwwimpact-evaluation.json`, do not run the synthesizer.

`workspace/debug-weights.json` is intentionally a separate file — it never overwrites a real
`workspace/page-weights.json` cache.

---

## Playwright CLI Quick Reference

Each phase uses a named session to avoid conflicts:

```bash
# Open session
playwright-cli -s=images-audit open <url>

# Navigate
playwright-cli -s=images-audit goto <url>

# Capture network data (critical for sustainability audits)
playwright-cli -s=images-audit network

# Capture page structure
playwright-cli -s=images-audit snapshot --filename=<name>.txt

# Inspect resources via JavaScript
playwright-cli -s=images-audit eval "<js expression>"

# Close session
playwright-cli -s=images-audit close
```

Read `references/playwright-guide.md` for the full command reference with sustainability-specific
eval snippets for resource inspection, header checking, and performance metrics.

---

## Output Structure

### Evaluate

```
workspace/
├── discovery.md                     # Site structure + resource inventory
├── phases/
│   ├── images-audit.md
│   ├── media-fonts-audit.md
│   ├── javascript-audit.md
│   ├── css-html-audit.md
│   ├── network-infra-audit.md
│   └── carbon-performance-audit.md
├── page-weights.json                # Per-page weight + Lighthouse scores
├── sustainability-report.md         # Synthesized, ranked report
└── lowwwimpact-evaluation.json      # Criteria assessment — structure is a hard contract
```

### Evaluate `--debug` (measurement-only)

```
workspace/
├── auth-state.json                  # Saved login state, only when the site requires auth
└── debug-weights.json               # Per-page initial/deferred KB + the 4 Lighthouse scores
```

### Eco-Specs

```
workspace/
├── element-inventory.json           # Shared discovery output, consumed by both writers
├── dev-specs.md                     # Developer-facing eco-design specs
└── eco-review.md                    # Designer-facing per-screen findings + sobriety section
```

---

## Coordinator Responsibilities

1. Identify the mode from the trigger — evaluate, eco-specs, or install. Passive is never invoked.
2. **Evaluate**: ensure Playwright is installed; run discovery; run the six audit phases
   (delegated in parallel where supported, otherwise sequentially); run the synthesizer; load
   criteria; run the evaluator; present both outputs with a summary.
   - Each phase uses its own named session (`-s=<name>`).
   - Clean up sessions when done: `playwright-cli close-all`.
   - **If `--debug` is set**: run the **Evaluate Debug Workflow** instead — auth plus measurement,
     write `workspace/debug-weights.json`, print the per-page summary, stop. Do not load criteria,
     run the evaluator, or run any audit phase.
3. **Eco-specs**: detect whether Figma URLs are present; run the matching inventory phase to write
   `workspace/element-inventory.json`; then run both writers off that JSON. Both outputs are
   always produced — there are no flags.
4. **Install**: run the **Install Workflow** — detect the host, copy `commands/*.md` to its command
   directory, inject `passive.md` into `AGENTS.md` between markers. Do not run any audit phase.

---

## Customization

- **Skipping phases**: "Skip CSS/HTML, focus on images and network"
- **Setting traffic**: "We get 500K pageviews/month" (affects annual carbon estimates)
- **Specifying hosting**: "We're on Vercel" (affects green hosting assessment)
- **Providing context**: "This is a Kirby CMS site with self-hosted fonts"
- **Setting priorities**: "I care most about page weight, less about SEO metadata"
- **Debug measurement only**: `evaluate --debug <url>` — auth + weight + Lighthouse only
- **Custom criteria file**: "Use this criteria file: path/to/custom-criteria.json"

---

## Key Sustainability Budgets

| Metric | Budget | Stretch |
|--------|--------|---------|
| Total page weight | < 1.5 MB | < 500 KB |
| Images | < 500 KB | < 200 KB |
| JavaScript | < 200 KB | < 100 KB |
| CSS | < 70 KB | < 30 KB |
| Fonts | < 50 KB | < 25 KB |
| HTML | < 50 KB | < 20 KB |
| HTTP requests | < 30 | < 15 |
| Third-party domains | < 4 | 0 |
| CO2/pageview (grade A) | < 0.06 g | < 0.02 g |
