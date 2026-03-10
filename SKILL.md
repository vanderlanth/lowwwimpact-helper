# Sustainable Web Review Skill

A multi-agent sustainability audit system that browses live web applications with Playwright CLI
and produces a prioritized, actionable report with carbon impact estimates. Every finding maps
to a specific `/xyz-optim` fix command. Can also evaluate a site against the lowwwimpact
sustainability criteria and produce a structured JSON assessment for human review.

## Prerequisites

Playwright CLI must be installed. If not available, run:

```bash
npm install -g @playwright/cli@latest
playwright-cli install-browser
playwright-cli install --skills
```

Verify with `playwright-cli --help`.

## Inputs

The user provides:

1. **Target URL** (required for review mode, optional for evaluate mode) — The application's entry point
2. **Report file** (required for fix mode, optional for evaluate mode) — Path to an existing sustainability report
3. **Monthly pageviews** (optional) — For annual carbon estimates (default: 10,000)
4. **Focus areas** (optional) — Which audit domains matter most (see Agent Roster below)
5. **Context** (optional) — App description, known constraints, hosting provider
6. **Criteria file** (optional, evaluate mode) — Path to criteria JSON, defaults to `references/lowwwimpact-criteria.json`

If the user doesn't provide optional inputs, use reasonable defaults and note assumptions.

## Three Modes of Operation

### Mode 1: Review

Triggered when the user provides a URL. Browses the live site, runs 6 parallel audit agents,
synthesizes a prioritized sustainability report. Every finding is tagged with the `/xyz-optim`
command to run for the fix.

### Mode 2: Fix

Triggered when the user provides a report file (or references a previous review). Reads the
report's Fix Command Summary and Sprint Plan, then guides the user through running the
appropriate `/xyz-optim` commands in priority order, passing relevant context from the audit.

### Mode 3: Evaluate

Triggered when the user says "evaluate", "lowwwimpact", "assessment", or "criteria". Reads the
27 lowwwimpact sustainability criteria from a JSON reference file, evaluates each one against
an existing Mode 1 report and/or direct Playwright inspection of a live URL, and outputs a
structured JSON file where every criterion has a typed answer and description.

At least one of a Mode 1 report or a live URL must be provided. The evaluator uses reports as
the primary evidence source and falls back to Playwright for criteria the reports don't cover.
Subjective criteria that require human judgment are flagged and left for manual review.

---

## Agent Roster

Each agent has a specialized sustainability lens. All agents use Playwright CLI to inspect the
live site.

### Review Agents (Mode 1)

| # | Agent | Focus | Fix Commands | Reference |
|---|-------|-------|-------------|-----------|
| 1 | **Images** | Formats, compression, responsive, lazy loading, alt text | `/image-optim` | `agents/images-audit.md` |
| 2 | **Media & Fonts** | Video facades, font loading, WOFF2, animations | `/media-optim`, `/typo-optim`, `/animation-optim`, `/cms-media-optim` | `agents/media-fonts-audit.md` |
| 3 | **JavaScript** | Bundle size, loading strategy, native APIs, code splitting | `/native-feature-optim`, `/performance-optim`, `/reusable-components-optim` | `agents/javascript-audit.md` |
| 4 | **CSS & HTML** | CSS size, critical CSS, semantic HTML, dark mode, reduced-motion | `/native-feature-optim`, `/compatibility-optim`, `/seo-optim` | `agents/css-html-audit.md` |
| 5 | **Network & Infrastructure** | Caching, compression, third-party domains, service worker | `/cache-compression-optim`, `/third-party-optim` | `agents/network-infra-audit.md` |
| 6 | **Carbon & Performance** | Page weight budget, carbon calculation, hosting, aggregate metrics | `/performance-optim` | `agents/carbon-performance-audit.md` |
| 7 | **Synthesizer** | Reads all 6 reports → prioritized action plan with fix command mapping | — | `agents/synthesizer.md` |

### Evaluate Agent (Mode 3)

| # | Agent | Focus | Reference |
|---|-------|-------|-----------|
| 8 | **Evaluator** | Maps audit findings to lowwwimpact criteria, produces structured JSON assessment | `agents/evaluator.md` |

### Complete Fix Command Catalogue

These are existing commands in `~/.claude/commands/`. The skill references them by name — it
does not contain fix logic itself.

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

---

## Review Mode Workflow

### Phase 1: Setup

1. Confirm the target URL and any user-provided context
2. Ensure Playwright CLI is installed (`playwright-cli --help`)
3. Open a browser session: `playwright-cli open <url>`
4. Take an initial screenshot: `playwright-cli screenshot --filename=landing.png`
5. Capture network data after full load: `playwright-cli network`
6. Create the workspace directory for outputs:
   ```
   workspace/
   ├── discovery.md
   ├── screenshots/
   ├── agents/
   └── sustainability-report.md
   ```

### Phase 2: Discovery (Main Agent)

Before spawning audit agents, crawl the site to build a shared resource inventory:

1. Capture the landing page network data and snapshot
2. Identify primary navigation links from the snapshot
3. Visit 3-5 key pages (follow nav links), capturing network data and snapshots for each
4. Build a resource inventory:
   - Total page weight per page
   - Resource count by type (images, JS, CSS, fonts, other)
   - Third-party domains list
   - Transfer sizes for all resources
5. Build a simple sitemap of discovered pages
6. Save to `workspace/discovery.md`

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
- Their specific agent instructions (from `agents/*.md`)
- The Playwright CLI reference (`references/playwright-guide.md`)
- The relevant sustainability references (from `references/`)
- An output directory for their findings (`workspace/agents/`)

Each agent:
1. Opens the site in its own Playwright CLI session (`-s=<agent-name>`)
2. Navigates through relevant pages
3. Inspects resources, network data, DOM structure, and response headers
4. Takes snapshots and screenshots as evidence
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

### Step 1: Load the Report

Read the sustainability report (from a previous review or user-provided file).

### Step 2: Parse Priorities

Extract:
- The Fix Command Summary table (which commands to run, in what order)
- The Sprint Plan (grouped by timeline)
- Individual findings with their fix command tags

### Step 3: Execute in Priority Order

For each command in the Fix Command Summary, ordered by total savings:

1. Show the user which findings this command addresses
2. Show estimated savings
3. Suggest running the command: "Run `/xyz-optim` to address these [N] findings"
4. After the command completes, move to the next

### Step 4: Post-Fix Assessment

After all priority commands have been run, suggest:
- Re-running the review (Mode 1) to measure improvement
- Comparing the new grade against the original

---

## Evaluate Mode Workflow

### Step 1: Load Criteria

Read the criteria file (default: `references/lowwwimpact-criteria.json`). Parse the `criteria`
array. Skip any entries where `id` starts with `TODO` — these are placeholders the user has
not yet filled in from their spreadsheet export.

### Step 2: Load Evidence Sources

Gather evidence from one or both sources:

**From Mode 1 reports** (primary — if a workspace/report path is provided):
- Read `workspace/sustainability-report.md`
- Read individual agent reports in `workspace/agents/`
- Each criterion has a `report_mapping` field that points to the relevant agent report(s)

**From live URL** (supplementary — if a URL is provided):
- Open a Playwright session: `playwright-cli -s=evaluator open <url>`
- Capture network data and snapshot
- Used for criteria that are `automatable: true` but not covered by the report

### Step 3: Evaluate Each Criterion

The evaluator agent processes each criterion based on its `automatable` flag and `type`:

- **`automatable: false`** → `answer: null`, description explains why human judgment is needed
- **`automatable: true`** → Evaluate from report evidence and/or Playwright inspection
- **`automatable: "partial"`** → Answer what can be confirmed, leave uncertain parts for human review

Answer types:
- **Boolean** → `true` or `false`
- **Range** → a number based on measurable data
- **Checkboxes** → array of strings from the `answers` list that are confirmed true

### Step 4: Write Output

Save to `workspace/lowwwimpact-evaluation.json`:

```json
{
  "meta": {
    "url": "https://example.com",
    "date": "2026-03-10",
    "report": "workspace/sustainability-report.md",
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
      "type": "Boolean",
      "question": "Is lazy loading used to ensure that image assets are only loaded when they are needed?",
      "answer": true,
      "description": "Pass — 14 of 16 below-fold images use loading=\"lazy\""
    }
  ]
}
```

Present the output to the user with a summary: how many criteria were evaluated, how many
need human review, and any notable pass/fail highlights.

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

# Take screenshot
playwright-cli -s=images-audit screenshot --filename=<name>.png

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
├── screenshots/                     # Visual evidence
│   ├── landing.png
│   └── ...
├── agents/
│   ├── images-audit.md
│   ├── media-fonts-audit.md
│   ├── javascript-audit.md
│   ├── css-html-audit.md
│   ├── network-infra-audit.md
│   └── carbon-performance-audit.md
└── sustainability-report.md         # Final synthesized report
```

### Evaluate Mode (additional)

```
workspace/
└── lowwwimpact-evaluation.json      # Structured criteria assessment for human review
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
9. In fix mode: guide the user through running `/xyz-optim` commands in priority order
10. In evaluate mode: load criteria, run the evaluator agent with available evidence, present JSON output with summary

---

## Customization

The user can customize the review by:

- **Skipping agents**: "Skip CSS/HTML, focus on images and network"
- **Setting traffic**: "We get 500K pageviews/month" (affects annual carbon estimates)
- **Specifying hosting**: "We're on Vercel" (affects green hosting assessment)
- **Providing context**: "This is a Kirby CMS site with self-hosted fonts"
- **Setting priorities**: "I care most about page weight, less about SEO metadata"
- **Focusing on fix mode**: "Here's my last review — just run the fixes"
- **Running evaluation**: "Evaluate against lowwwimpact criteria" (uses Mode 1 report + live URL)
- **Custom criteria file**: "Use this criteria file: path/to/custom-criteria.json"

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
