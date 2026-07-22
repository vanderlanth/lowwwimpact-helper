# Sustainable Web Review Skill

A multi-agent sustainability audit system that browses live web applications with Playwright CLI
and produces a prioritized, actionable report with carbon impact estimates. Every finding maps
to a specific `/xyz-optim` fix command. Can also evaluate a site against the lowwwimpact
sustainability criteria, produce a structured JSON assessment for human review, generate
developer-facing eco-design spec files from Figma frames, and produce designer-facing
eco-review PDFs from Figma screens.

## Prerequisites

Playwright CLI must be installed. If not available, run:

```bash
npm install -g @playwright/cli@latest
playwright-cli install-browser
playwright-cli install --skills
```

Verify with `playwright-cli --help`.

**Lighthouse CLI** is used for performance, accessibility, best-practices, and SEO scoring.
Runs via `npx` — no separate installation needed if Node.js ≥ 18 is available.
Verify: `npx lighthouse --version`. If unavailable, Lighthouse scores will be omitted and
noted in the report.

## Inputs

The user provides:

1. **Target URL** (required for review mode, optional for evaluate mode) — The application's entry point
2. **Evaluation file** (required for fix mode) — Path to `workspace/lowwwimpact-evaluation.json` produced by Mode 2. The Mode 1 `workspace/sustainability-report.md` is also read for KB savings data.
3. **Monthly pageviews** (optional) — For annual carbon estimates (default: 10,000)
4. **Focus areas** (optional) — Which audit domains matter most (see Agent Roster below)
5. **Context** (optional) — App description, known constraints, hosting provider
6. **Criteria file** (optional, evaluate mode) — Path to criteria JSON, defaults to `references/lowwwimpact-criteria.json`
7. **User journeys** (optional, evaluate mode) — 1–2 natural-language use cases describing a task a user would perform on the site (e.g. "from the homepage, find a product and add it to the cart, then visit the cart"). If not provided, the skill will ask before proceeding.
8. **Pre-cached weights** (optional, evaluate mode) — `workspace/page-weights.json` produced by `/measure-page-weight` or Mode 1. If present, Mode 2 uses it without re-measuring.

If the user doesn't provide optional inputs, use reasonable defaults and note assumptions.

## Modes of Operation

### Mode 1: Review

Triggered when the user provides a URL. Browses the live site, runs 6 parallel audit agents,
synthesizes a prioritized sustainability report. Every finding is tagged with the `/xyz-optim`
command to run for the fix.

### Mode 2: Evaluate

Triggered when the user says "evaluate", "lowwwimpact", "assessment", or "criteria". Reads the
27 lowwwimpact sustainability criteria from a JSON reference file, evaluates each one against
an existing Mode 1 report and direct Playwright inspection, and outputs a structured JSON file
where every criterion has a typed answer and note.

**Evidence priority chain:**
1. Uses `workspace/page-weights.json` if present (produced by `/measure-page-weight` or Mode 1) for Lighthouse scores and page weight data
2. Uses Mode 1 reports if present (`workspace/sustainability-report.md` + agent reports) for richer criteria evidence across all audit domains
3. Falls back to standalone Lighthouse + direct Playwright inspection if neither is available

Run `/measure-page-weight <url>` first to pre-cache accurate weight and Lighthouse data — recommended when running Mode 2 without Mode 1.

**Debug variant — `evaluate --debug`:** measurement-only. Runs the shared auth + measure
pipeline (`references/auth-measure-pipeline.md`) and writes `workspace/debug-weights.json` —
nothing else. It skips criteria loading, the evaluator agent, and all Mode 1 agents. Use it to
verify that authentication and weight/Lighthouse measurement work (especially on pages behind a
login) before running a full evaluation. See the **Evaluate Debug Workflow** below.

### Mode 3: Fix

Triggered when the user says "fix", "fix plan", or provides the path to a Mode 2 evaluation
file. Reads `workspace/lowwwimpact-evaluation.json` and `workspace/sustainability-report.md`,
then produces a persistent `workspace/fix-plan.md`. Fixes are ranked by KB savings. Each fix
entry lists the lowwwimpact criteria IDs it addresses and includes curated web references found
via live WebSearch.

Requires Mode 2 output.

### Mode 4: Specs

Triggered by keywords "specs", "eco specs", "dev specs", "sustainability specs", or
"figma specs" — with or without Figma frame URLs.

**If `figma.com` frame URLs are present:** Analyzes each Figma frame using the Figma MCP to
detect which element types are present (images, fonts, video, carousels, third-party embeds,
animations, live feeds, cookie consent UI).

**If no `figma.com` URLs are present:** Scans the current project directory to detect the same
element types from the codebase (template files, CSS, JavaScript, package.json).

In both cases: generates a concise developer-facing markdown file of technical sustainability
requirements — the "invisible" specs that designers don't annotate. Each spec section includes
2–3 curated implementation references aimed at junior developers.

Fully independent of Modes 1–3. Does not require Playwright or a live URL.

### Mode 5: Designer Eco-Review

Triggered by keywords "eco review", "designer review", "design review", "eco-design principles",
or "review for designers" — with or without Figma frame URLs.

**Must be checked before Mode 4.** If the intent matches both Mode 4 and Mode 5 trigger words,
prefer Mode 5 when the user explicitly says "designer", "for designers", or "design feedback".

**If `figma.com` frame URLs are present (2–3):** Analyzes each Figma frame using the Figma MCP
against the eco-design principles for designers.

**If no `figma.com` URLs are present:** Scans the current project directory, identifies 2–3 main
page templates as "screens", and analyzes each template's design decisions against the same
eco-design principles.

In both cases: produces a simple, clean PDF report (`workspace/eco-review.pdf`) with per-screen
findings and top cross-screen recommendations. All findings are expressed as design decisions —
no code, no developer jargon.

Fully independent of Modes 1–4. Does not require Playwright or a live URL.

---

## Agent Roster

Each agent has a specialized sustainability lens. All agents use Playwright CLI to inspect the
live site.

### Review Agents (Mode 1)

| # | Agent | Focus | Tools | Fix Commands | Reference |
|---|-------|-------|-------|-------------|-----------|
| 1 | **Images** | Formats, compression, responsive, lazy loading, alt text | Playwright CLI | `/image-optim` | `agents/mode-1-review/images-audit.md` |
| 2 | **Media & Fonts** | Video facades, font loading, WOFF2, animations | Playwright CLI | `/media-optim`, `/typo-optim`, `/animation-optim`, `/cms-media-optim` | `agents/mode-1-review/media-fonts-audit.md` |
| 3 | **JavaScript** | Bundle size, loading strategy, native APIs, code splitting | Playwright CLI | `/native-feature-optim`, `/performance-optim`, `/reusable-components-optim` | `agents/mode-1-review/javascript-audit.md` |
| 4 | **CSS & HTML** | CSS size, critical CSS, semantic HTML, dark mode, reduced-motion | Playwright CLI | `/native-feature-optim`, `/compatibility-optim`, `/seo-optim` | `agents/mode-1-review/css-html-audit.md` |
| 5 | **Network & Infrastructure** | Caching, compression, third-party domains, service worker | Playwright CLI, WebSearch | `/cache-compression-optim`, `/third-party-optim` | `agents/mode-1-review/network-infra-audit.md` |
| 6 | **Carbon & Performance** | Page weight budget, carbon calculation, hosting, aggregate metrics | Playwright CLI, WebFetch | `/performance-optim` | `agents/mode-1-review/carbon-performance-audit.md` |
| 7 | **Synthesizer** | Reads all 6 reports → prioritized action plan with fix command mapping | — | — | `agents/mode-1-review/synthesizer.md` |

### Specs Agents (Mode 4)

| # | Agent | Input | Focus | Tools | Reference |
|---|-------|-------|-------|-------|-----------|
| 9 | **Figma Specs** | Figma frame URLs | Detects element types in Figma frames → maps to eco-design technical specs → writes dev-facing markdown with curated references | Figma MCP, WebSearch | `agents/mode-4-specs/figma-specs-agent.md` |
| 9b | **Code Specs** | Project directory | Detects element types in codebase via grep → maps to eco-design technical specs → writes dev-facing markdown with curated references | Bash, WebSearch | `agents/mode-4-specs/code-specs-agent.md` |

### Designer Eco-Review Agents (Mode 5)

| # | Agent | Input | Focus | Tools | Reference |
|---|-------|-------|-------|-------|-----------|
| 10 | **Eco-Designer Review** | Figma frame URLs | Analyzes 2–3 Figma screens against eco-design principles for designers → writes per-screen findings + top recommendations → exports PDF | Figma MCP, Bash | `agents/mode-5-designer-review/eco-designer-review-agent.md` |
| 10b | **Code Eco-Review** | Project directory | Identifies 2–3 main templates as screens, analyzes design decisions in codebase against eco-design principles → writes per-screen findings + exports PDF | Bash | `agents/mode-5-designer-review/code-eco-review-agent.md` |

### Evaluate Agent (Mode 2)

| # | Agent | Focus | Tools | Reference |
|---|-------|-------|-------|-----------|
| 8 | **Evaluator** | Maps audit findings to lowwwimpact criteria, produces structured JSON assessment | Playwright CLI, WebFetch | `agents/mode-2-evaluate/evaluator.md` |

### Complete Fix Command Catalogue

These commands live in `commands/` in this repository and are symlinked to `~/.claude/commands/`
during installation. The skill references them by name — it does not contain fix logic itself.

| Command | Domain |
|---------|--------|
| `/image-optim` | Image formats, responsive, lazy loading, compression, CLS |
| `/media-optim` | Video/audio: autoplay, preload, formats, facades, accessibility |
| `/cms-media-optim` | CMS upload constraints, auto-processing, editor guardrails |
| `/typo-optim` | WOFF2, subsetting, self-hosting, font-display, system fallback |
| `/animation-optim` | GPU-safe properties, prefers-reduced-motion, no GIFs, will-change |
| `/third-party-optim` | Facade pattern for YouTube/Vimeo/Maps/Calendly/social, max 4 domains |
| `/native-feature-optim` | Replace JS with native HTML/CSS: dialog, details, scroll-snap, popover |
| `/cache-compression-optim` | .htaccess: Gzip, Cache-Control, hashed filenames |
| `/performance-optim` | Page weight budget, Lighthouse, bundle analysis, CI enforcement |
| `/reusable-components-optim` | Duplicate CSS/JS detection, shared utilities, unused exports |
| `/compatibility-optim` | Progressive enhancement, @supports, polyfills, degradation |
| `/seo-optim` | Titles, descriptions, canonical, Open Graph, JSON-LD |
| `/measure-page-weight` | Pre-cache page weight + Lighthouse scores to `workspace/page-weights.json` |

---

## Review Mode Workflow

### Phase 1: Setup

1. Confirm the target URL and any user-provided context
2. Ensure Playwright CLI is installed (`playwright-cli --help`)
3. Create the workspace directory for outputs:
   ```
   workspace/
   ├── discovery.md
   ├── agents/
   └── sustainability-report.md
   ```

### Phase 2: Discovery (Main Agent)

Before spawning audit agents, crawl the site to build a shared resource inventory.
**Each page is measured in a fresh session** (no cache from previous pages):

1. For each page to discover (landing page + 3–5 key inner pages):
   a. Open a new named session: `playwright-cli -s=disc-N open <url>`
      Then immediately set the standard audit viewport: `playwright-cli -s=disc-N resize 1440 760`
   b. Wait for the page to fully load + 3 seconds (catches late-triggered resources):
      ```bash
      playwright-cli -s=disc-N eval "new Promise(r => { if (document.readyState === 'complete') r(); else window.addEventListener('load', r, {once: true}); })"
      playwright-cli -s=disc-N eval "new Promise(r => setTimeout(r, 3000))"
      ```
   c. Capture network data and snapshot (no screenshots in Mode 1/2/3)
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
> carbon-performance agent provide the authoritative figures.

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

This discovery output is shared with all audit agents as context.

### Phase 3: Parallel Audit (Sub-agents)

Spawn agents 1-6 in parallel. Each agent receives:

- The target URL
- The discovery file (`workspace/discovery.md`)
- Their specific agent instructions (from `agents/mode-*/*.md`)
- The Playwright CLI reference (`references/playwright-guide.md`)
- The relevant sustainability references (from `references/`)
- An output directory for their findings (`workspace/agents/`)

Each agent:
1. Opens the site in its own Playwright CLI session (`-s=<agent-name>`)
2. Navigates through relevant pages
3. Inspects resources, network data, DOM structure, and response headers
4. Takes snapshots as evidence (do NOT take screenshots — not needed in Mode 1/2/3)
5. Writes findings to their output file with estimated KB savings and fix command tags

If sub-agents are not available, run each audit sequentially in the main loop.

### Phase 4: Synthesis

After all audits complete, the Synthesizer agent:

1. Reads all 6 agent reports
2. Deduplicates overlapping findings (does not double-count savings)
3. Calculates the sustainability grade using the SWD carbon model
4. Builds the page weight breakdown table
5. Maps every finding to its `/xyz-optim` fix command
6. Ranks findings by bandwidth savings (KB) and implementation effort
7. Creates the Fix Command Summary table
8. Creates the Sprint Plan
9. Calculates improvement potential (projected grade after fixes)
10. Produces the final report

### Phase 5: Output

Generate the final report following `references/report-template.md`.

Save to `workspace/sustainability-report.md` and present to the user.

---

## Fix Mode Workflow

### Step 1: Load Evidence

Read both files:
- `workspace/lowwwimpact-evaluation.json` — criteria pass/fail state and notes (Mode 2 output)
- `workspace/sustainability-report.md` — Fix Command Summary table with KB savings per command (Mode 1 output)

If either file is missing, stop and tell the user which mode to run first:
- Missing `sustainability-report.md` → run Mode 1 (Review)
- Missing `lowwwimpact-evaluation.json` → run Mode 2 (Evaluate)

### Step 2: Build the Fix Index

For each `/xyz-optim` command found in the Fix Command Summary:

1. Record its total KB savings from the report
2. Scan the evaluation JSON for criteria where `answer` is `false` or an incomplete
   checkboxes array, and map them to this command using the domain table below
3. Pull the relevant findings from the Mode 1 report for this command
4. Build an entry: `command → { kb_savings, criteria_ids[], findings[] }`

Criteria-to-command domain mapping:

| Criteria prefix | Command(s) |
|-----------------|------------|
| 1.4 (images) | `/image-optim` |
| 1.5 (media/video) | `/media-optim`, `/cms-media-optim` |
| 1.6 (fonts) | `/typo-optim` |
| 1.7 (animation) | `/animation-optim` |
| 2.1 (caching/compression) | `/cache-compression-optim` |
| 2.2 (JS) | `/native-feature-optim`, `/performance-optim`, `/reusable-components-optim` |
| 2.3 (CSS/HTML) | `/native-feature-optim`, `/compatibility-optim`, `/seo-optim` |
| 2.5 (third-party) | `/third-party-optim` |
| 3.x (carbon/performance) | `/performance-optim` |

### Step 3: Research References

For each command that has at least one failing criterion or finding, run a **WebSearch** to
find 2–3 authoritative references (MDN, web.dev, WHATWG, W3C, Smashing Magazine, CSS-Tricks).
Prefer links specific to the failing criteria notes rather than generic documentation.
Run searches per command — do not batch into a single global search.

### Step 4: Write fix-plan.md

Save to `workspace/fix-plan.md`. Order fix entries by KB savings descending.

```markdown
# Fix Plan — [Site Name]

Generated: [date] | Based on: sustainability-report.md + lowwwimpact-evaluation.json

## Summary

| Priority | Command | KB Savings | Criteria Addressed |
|----------|---------|------------|--------------------|
| 1 | `/image-optim` | 320 KB | 1.4.a, 1.4.b, 1.4.c |
| 2 | `/third-party-optim` | 180 KB | 2.5.a, 2.5.b |
| … | … | … | … |

## Fixes

### 1. `/image-optim` — 320 KB savings

**Criteria addressed:** 1.4.a, 1.4.b, 1.4.c

**Findings:**
- 8 images served as PNG instead of WebP (est. −180 KB)
- 5 below-fold images missing `loading="lazy"` (est. −60 KB)
- Hero image has no `srcset` for mobile (est. −80 KB)

**References:**
- [Title](url)
- [Title](url)

**Run:** `/image-optim`

---

[repeat for each command, ranked by KB savings descending]

## Next Steps

After applying fixes, re-run Mode 1 to measure improvement, then re-run Mode 2 to update
the evaluation JSON and compare criteria scores.
```

---

## Evaluate Debug Workflow (`evaluate --debug`)

Measurement-only path. The coordinator runs this directly — it does **not** spawn the evaluator
agent, load criteria, or run any Mode 1 agent. Goal: confirm auth + weight/Lighthouse measurement
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

## Evaluate Mode Workflow

### Step 0: Collect User Journeys

If no journeys were provided in the prompt, ask the user:

> "Do you have 1–2 user journeys to include in this evaluation?
> Example: 'From the homepage, find a product and add it to the cart, then visit the cart.'
> You can also say **skip** to proceed without journey data."

If the user says skip (or equivalent), set journeys = [] and continue.
If journeys are provided, proceed — they will be resolved in Step 1.5 of the evaluator agent.

### Step 1: Load Criteria

Read the criteria file (default: `references/lowwwimpact-criteria.json`). Parse the `criteria`
array. Skip any entries where `id` starts with `TODO` — these are placeholders the user has
not yet filled in from their spreadsheet export.

### Step 2: Load Evidence Sources

Check for `workspace/page-weights.json` first (Step 1.9 in the evaluator agent). If present,
Lighthouse scores and page weights are loaded from there without re-measuring.

If `workspace/sustainability-report.md` exists, read it and the individual agent reports in
`workspace/agents/` for criteria evidence. If absent, proceed — criteria evidence will be
limited to direct Playwright inspection.

Each criterion has a `report_mapping` field that points to the relevant agent report(s).

The URL is taken from the Mode 1 report if available, from `workspace/page-weights.json` if
not, or asked of the user if neither exists.

### Step 3: Evaluate Each Criterion

The evaluator agent processes each criterion based on its `automatable` flag and `type`:

- **`automatable: false`** → `answer: null`, note explains why human judgment is needed
- **`automatable: true`** → Evaluate from report evidence and/or Playwright inspection
- **`automatable: "partial"`** → Answer what can be confirmed, leave uncertain parts for human review

Answer types:
- **boolean** → `true` or `false`
- **range** → a number based on measurable data
- **numeric** → a count based on measurable data
- **checkboxes** → array of strings from the `answers` list that are confirmed true

### Step 4: Write Output

Save to `workspace/lowwwimpact-evaluation.json`:

```json
{
  "meta": {
    "url": "https://example.com",
    "urls": ["https://example.com", "https://example.com/about"],
    "date": "2026-03-10",
    "report": "workspace/sustainability-report.md",
    "lighthouse": "carbon-performance-audit",
    "criteria_version": "lowwwimpact v1",
    "total_criteria": 27,
    "evaluated": 20,
    "skipped_subjective": 5,
    "skipped_na": 2,
    "skipped_todo": 0
  },
  "evaluation": [
    {
      "id": "1.4.c",
      "type": "boolean",
      "question": "Is lazy loading used to ensure that image assets are only loaded when they are needed?",
      "answer": true,
      "note": "Pass — 14 of 16 below-fold images use loading=\"lazy\""
    }
  ],
  "pages": {
    "page-1": {
      "url": "https://example.com",
      "title": "Home — Example",
      "performance": 72,
      "accessibility": 91,
      "best_practices": 83,
      "seo": 95,
      "initial_weight_kb": 820,
      "deferred_weight_kb": 1340
    }
  },
  "lighthouse_recap": "Performance is the weakest area (avg. 72/100). The audit found render-blocking JS and unoptimised images as the main causes — criteria 1.4.b and 2.2.a confirm unminified assets. Running /performance-optim and /image-optim would likely bring scores above 85.",
  "recommendations": {
    "executive_summary": "The site handles infrastructure and font loading well but fails on image optimisation and third-party script management. Seven criteria failed outright, with images and JS weight being the most impactful gaps. A focused sprint on /image-optim and /third-party-optim would address the majority of the issues.",
    "top_5": ["1.4.b", "1.5.c", "2.5.c", "2.2.a", "3.2.a"]
  },
  "journeys": {
    "journey-1": {
      "description": "From homepage, find a product, add to cart, visit the cart",
      "pages": [
        { "url": "https://example.com", "name": "Home", "kb": 420 },
        { "url": "https://example.com/shop", "name": "Shop catalogue", "kb": 380 },
        { "url": "https://example.com/shop/running-shoes", "name": "Running Shoes", "kb": 520 },
        { "url": "https://example.com/cart", "name": "Cart", "kb": 290 }
      ]
    }
  }
}
```

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

`meta.lighthouse` is `"carbon-performance-audit"` when data came from a Mode 1 report,
`"standalone"` when Lighthouse was run directly in Mode 3, or `null` (with `pages` omitted)
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

Present the output to the user with a summary: how many criteria were evaluated, how many
need human review, and any notable pass/fail highlights.

---

## Specs Mode Workflow (Mode 4)

### Step 1: Collect Inputs and Detect Path

- Accept optional context: project name, CMS in use, known tech stack
- **Check whether the user provided any `figma.com` URLs:**
  - If yes → **Figma path**: follow Steps 2a–4 below (Figma MCP inspection)
  - If no → **Code path**: follow Steps 2b–4 below (codebase scan)

### Step 2a: Figma Path — Analyse Frames

- Accept 1–N Figma frame URLs from the user
- Read `references/figma-specs.md` and `references/sustainability-checklist.md` before starting
- Spawn the Figma Specs agent (`agents/mode-4-specs/figma-specs-agent.md`). For each Figma URL:

1. Call `get_design_context` (Figma MCP) with the frame's `fileKey` and `nodeId`
2. Call `get_screenshot` if a visual confirmation is needed for ambiguous layers
3. Build an element inventory — which of the following are present across *all* analyzed frames:


| Element type | Detection signals |
|---|---|
| Raster images / photos | Background image fills, JPEG/PNG/WebP layers, media placeholders |
| Icons | Small image layers, icon components, SVG frames |
| Video / audio | Player UI components, media frames, play-button overlays |
| Carousel / slider | Multiple slide layers, pagination dots, prev/next navigation |
| Custom fonts | Non-system typefaces in text layers (anything not Arial, Helvetica, Georgia, system-ui, etc.) |
| Third-party embeds | Map widgets, YouTube/Vimeo frames, social feed components, chat widgets |
| Animation cues | Transition annotations, motion labels, animated component names |
| Live / feed content | News tickers, live badges, feed cards, polling indicators |
| Cookie consent UI | Cookie banners, GDPR overlays, consent modals, privacy preference dialogs |

### Step 2b: Code Path — Scan Codebase

- Read `references/figma-specs.md` and `references/sustainability-checklist.md` before starting
- Spawn the Code Specs agent (`agents/mode-4-specs/code-specs-agent.md`) with the current working directory as input
- The agent scans template files, CSS, JavaScript, and `package.json` to detect which element
  types are implemented, using grep passes for each category (images, fonts, video, third-party,
  animation, carousel, live content, cookie consent)

### Step 3: Build Spec Sections

For each detected element type, include the matching spec block (see the spawned agent's file for
full mapping). Then run **WebSearch** to find 2–3 authoritative implementation references for
that section. Prefer MDN, web.dev, W3C, Smashing Magazine, CSS-Tricks, or official spec docs.
Target practical how-to guides over generic overviews — useful for junior developers.

### Step 4: Append Always-on Specs

Regardless of input source (Figma or code), always append:

- **CMS Upload Constraints** — max weight/dimensions, auto-renditions, editor guidance
- **CMS Edition Constraints** — block/gallery/embed limits, shared asset reuse
- **Keyboard Accessibility** — skip-to-content, full keyboard nav

Add **Cookies** only if no cookie consent UI (Figma path) or cookie consent library (code path)
was detected.

Each always-on section also includes 2–3 WebSearch-sourced references.

### Step 5: Write Output

Save to `workspace/dev-specs.md` following the template below.
Append a metadata footer with estimated token consumption.
Present the file to the user.

```markdown
# Dev Eco-Design Specs — [Project / Screen name]

> Analyzed frames: [frame name 1], [frame name 2] | [date]

---

## [Element type, e.g. Images]

- Imperative spec line
- Imperative spec line with `inline code` where relevant

**Resources**
- [Title](url) — why it's relevant
- [Title](url)

---

## Always-on Specs

### CMS Upload Constraints

- Spec lines…

**Resources**
- [Title](url)

### CMS Edition Constraints

- Spec lines…

**Resources**
- [Title](url)

### Keyboard Accessibility

- Spec lines…

**Resources**
- [Title](url)

### Cookies *(no consent UI detected in analyzed screens)*

- Spec lines…

**Resources**
- [Title](url)

---

*Generated by lowwwimpact-helper Mode 4 | [model-id] | Frames analyzed: N | ~X tokens · ~$X*
```

---

## Designer Eco-Review Mode Workflow (Mode 5)

### Step 1: Collect Inputs and Detect Path

- Accept optional context: project name, target audience, or other framing
- **Check whether the user provided any `figma.com` URLs:**
  - If yes → **Figma path**: accept 2–3 Figma frame URLs; follow Step 2a below
  - If no → **Code path**: use the current project directory; follow Step 2b below
- Read `references/eco-design-principles-for-designers.md` before starting

### Step 2a: Figma Path — Analyse Frames

Spawn the Eco-Designer Review agent (`agents/mode-5-designer-review/eco-designer-review-agent.md`). For each Figma URL:

1. Call `get_design_context` (Figma MCP) with the frame's `fileKey` and `nodeId`
2. Call `get_screenshot` if visual confirmation is needed for ambiguous layers
3. Build an element inventory per screen (images, fonts, motion, layout, CTAs, third-party widgets, forms, etc.)

### Step 2b: Code Path — Scan Codebase

Spawn the Code Eco-Review agent (`agents/mode-5-designer-review/code-eco-review-agent.md`) with the current working
directory as input. The agent:

1. Discovers 2–3 main page templates in the project (homepage, listing page, detail page, etc.)
2. Treats each template as a "screen" — reads its code and related CSS/JS to build a design inventory
3. Uses grep passes to detect images, fonts, animation, third-party embeds, interaction patterns,
   and layout signals

### Step 3: Analyze and Write

The spawned agent walks through every category in `references/eco-design-principles-for-designers.md`,
produces per-screen findings (skipping compliant or non-applicable categories), writes a
global Key Actions section, a Design Sobriety section drawn from the Sustainable Web Design
reference, and saves to `workspace/eco-review.md`.

### Step 4: Export PDF

Run:

```bash
npx md-to-pdf workspace/eco-review.md
```

Produces `workspace/eco-review.pdf`. If the command fails, report the markdown path and note
that the user can convert manually.

Present both file paths to the user on completion.

---

## Playwright CLI Quick Reference for Agents

Each agent uses a named session to avoid conflicts:

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

### Review Mode

```
workspace/
├── discovery.md                     # Site structure + resource inventory from Phase 2
├── agents/
│   ├── images-audit.md
│   ├── media-fonts-audit.md
│   ├── javascript-audit.md
│   ├── css-html-audit.md
│   ├── network-infra-audit.md
│   └── carbon-performance-audit.md
└── sustainability-report.md         # Final synthesized report
```

### Evaluate Mode — Mode 2 (additional)

```
workspace/
└── lowwwimpact-evaluation.json      # Structured criteria assessment for human review
```

### Evaluate Debug Mode — `evaluate --debug` (measurement-only)

```
workspace/
├── auth-state.json                  # Saved login state (only when the site requires auth)
└── debug-weights.json               # Per-page initial/deferred KB + 4 Lighthouse scores
```

### Fix Mode — Mode 3 (additional)

```
workspace/
└── fix-plan.md                      # Persistent fix plan with criteria links and web references
```

### Figma Specs Mode — Mode 4

```
workspace/
└── dev-specs.md                     # Developer-facing eco-design spec file generated from Figma frames
```

### Designer Eco-Review Mode — Mode 5

```
workspace/
├── eco-review.md                    # Source markdown: per-screen findings + top recommendations
└── eco-review.pdf                   # Exported PDF for designer handoff
```

---

## Coordinator Responsibilities

1. Handle Playwright CLI installation if needed
2. Run the discovery phase to build shared context (resource inventory + sitemap)
3. Spawn audit agents in parallel (or sequentially if no sub-agents)
4. Ensure each agent uses its own named session (`-s=<name>`)
5. Collect all agent reports
6. Run the synthesizer to produce the final report
7. Clean up browser sessions: `playwright-cli close-all`
8. Present the final report to the user
9. In evaluate mode (Mode 2): load criteria, run the evaluator agent with available evidence, present JSON output with summary
   - **If `--debug` is set**: run the **Evaluate Debug Workflow** directly instead — execute the shared auth + measure pipeline, write `workspace/debug-weights.json`, present the per-page summary, and stop. Do NOT load criteria, spawn the evaluator, or run any Mode 1 agent.
10. In fix mode (Mode 3): load evaluation JSON + sustainability report, build fix index, research references via WebSearch, write `workspace/fix-plan.md`
11. In specs mode (Mode 4): detect whether Figma URLs are present; if yes spawn Figma Specs agent, if no spawn Code Specs agent; write `workspace/dev-specs.md`
12. In designer eco-review mode (Mode 5): detect whether Figma URLs are present; if yes spawn Eco-Designer Review agent, if no spawn Code Eco-Review agent; write `workspace/eco-review.md` and export PDF

---

## Customization

The user can customize the review by:

- **Skipping agents**: "Skip CSS/HTML, focus on images and network"
- **Setting traffic**: "We get 500K pageviews/month" (affects annual carbon estimates)
- **Specifying hosting**: "We're on Vercel" (affects green hosting assessment)
- **Providing context**: "This is a Kirby CMS site with self-hosted fonts"
- **Setting priorities**: "I care most about page weight, less about SEO metadata"
- **Running evaluation (Mode 2)**: "Evaluate against lowwwimpact criteria" (uses Mode 1 report + live URL)
- **Debug measurement only**: "evaluate --debug <url>" (auth + weight + Lighthouse only → `workspace/debug-weights.json`, no criteria)
- **Custom criteria file**: "Use this criteria file: path/to/custom-criteria.json"
- **Generating fix plan (Mode 3)**: "Generate a fix plan" (uses Mode 2 evaluation JSON + Mode 1 report)
- **Generating Figma specs (Mode 4)**: "Generate eco specs from this Figma frame" or provide figma.com URLs with spec/recommendation intent (fully independent — no prior modes needed)

Adapt the agent roster and instructions accordingly.

---

## Key Sustainability Budgets (Quick Reference)

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
