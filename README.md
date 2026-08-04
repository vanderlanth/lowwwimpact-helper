# lowwwimpact-helper

An AI agent skill for auditing web sustainability. It browses live websites with Playwright, produces prioritized carbon-impact reports, and evaluates sites against the [lowwwimpact](https://lowwwimpact.com/) assessment criteria. It also generates paired eco-design deliverables — developer specs and a designer review — from Figma frames or directly from a code project.

Built for [Cursor](https://cursor.com/) (Agent Skills) and [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Skills).

## What it does

Four modes of operation:

| Mode | Trigger | Prompt example | Output |
|------|---------|----------------|--------|
| **0 - Init** | Say "init" / "setup" / "install in this project" | `Initialize lowwwimpact in this project` (or `/lowwwimpact-init` once installed) | Fix commands copied into `.claude/commands/` + companion block wired into `CLAUDE.md` |
| **1 - Review** | Provide a URL | `Use /lowwwimpact-helper in mode 1 to review https://www.liip.ch` | Sustainability report with carbon grade, page weight breakdown, and prioritized findings |
| **2 - Evaluate** | Say "evaluate" / "lowwwimpact" / "assessment" / "criteria" + URL. Prompts for 1-2 optional user journeys before starting. | `Use /lowwwimpact-helper in mode 2 to evaluate https://www.liip.ch. User journey: from the homepage, find a blog post and read it.` | JSON assessment of 27 lowwwimpact criteria with pass/fail/partial answers, plus per-journey page weight data. Works standalone — run `/measure-page-weight <url>` first for best accuracy, or provide Mode 1 output for full evidence. |
| **3 - Fix** | Say "fix" / "fix plan" | `Use /lowwwimpact-helper in mode 3 to generate a fix plan` | Persistent `fix-plan.md` ranked by KB savings, with criteria IDs and curated web references. Requires Mode 1 + Mode 2 output. |
| **4 - Specs & Review** | "specs" / "dev specs" / "eco specs" / "eco review" / "designer review" — with Figma frame URLs or without (inspects current project) | With Figma: `Use /lowwwimpact-helper in mode 4 on these Figma frames: https://figma.com/design/...` · With code: `Use /lowwwimpact-helper in mode 4 for this project` | Two files from one discovery run: developer-facing `dev-specs.md` (technical requirements per element type) and designer-facing `eco-review.md` (per-screen findings against eco-design principles) |

### Mode 1 - Review

6 specialized audit agents run in parallel (images, media and fonts, JavaScript, CSS and HTML, network and infrastructure, carbon and performance) then a synthesizer agent produces the final report. Every finding is tagged with the specific fix command to run.

### Mode 2 - Evaluate

Evaluates a site against the 27 MVP criteria from the [W3C Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) as curated by the lowwwimpact project. Uses a priority chain for evidence: `workspace/page-weights.json` (from `/measure-page-weight` or Mode 1) → Mode 1 reports → standalone Lighthouse + Playwright inspection. Supports 1-2 user journeys to measure page weight across a real task flow. Outputs a structured JSON file for human review.

### Mode 3 - Fix

Reads `workspace/lowwwimpact-evaluation.json` and `workspace/sustainability-report.md`, builds a fix index ranked by KB savings, searches for authoritative references per fix command, and writes a persistent `workspace/fix-plan.md`.

### Mode 4 - Specs & Review

Fully independent of Modes 1-3. Runs discovery once and writes two audience-specific files from it. There are no flags and no sub-modes — every run produces both.

**Two input paths:**
- **Figma frames:** Provide one or more `figma.com` frame URLs — uses the Figma MCP, reading designer annotations first and filling the gaps visually
- **Code project:** Provide no URLs — greps the current project directory project-wide, then scans 2-3 representative page templates individually as "screens"

Either path writes `workspace/element-inventory.json`. Both writers then read that file — nothing is inspected twice:

| Output | Audience | Content |
|--------|----------|---------|
| `dev-specs.md` | Developers | Technical sustainability requirements per detected element type, sourced from `references/ecodesign-requirements-concise.md` with its curated documentation links |
| `eco-review.md` | Designers | Per-screen findings against the eco-design principles, top cross-screen actions, and a Design Sobriety section drawn from the Sustainable Web Design reference. All findings are design decisions: no code, no developer jargon. |

## Auditing pages behind a login

Modes that measure page weight (Evaluate, and the `/measure-page-weight` command) can audit pages
that sit behind authentication. You provide credentials once; the skill logs in, saves the session,
and reuses it for every measurement.

**1. Supply credentials via a `.env` file.** Place a `.env` at the project root (or the workspace
parent). The skill reads variables matching `*_USER` / `*_LOGIN` / `*_EMAIL` for the username and
`*_PASS` / `*_PASSWORD` for the password:

```env
SITE_USER=you@example.com
SITE_PASS=your-password
```

If no matching variables are found, the skill asks for the username and password interactively.

**2. Run an audit.** On the first run the skill detects the login redirect, logs in, and saves the
session to `workspace/auth-state.json` (cookies + per-origin localStorage, Playwright
`storageState` format). Later measurements load it automatically — no re-login. For a public site
this is a no-op and no `auth-state.json` is written.

**3. Verify auth in isolation first (recommended).** Before a full evaluation, confirm login +
measurement work on a protected page:

```
evaluate --debug https://example.com/dashboard
```

This runs auth + weight/Lighthouse measurement only, writes `workspace/debug-weights.json`, and
prints a per-page summary — nothing else. If measurement lands on the login page, re-run to
overwrite `workspace/auth-state.json`.

> Keep `.env` and `workspace/auth-state.json` out of version control — they hold credentials and a
> live session.

## Installation

Install **per project** — the skill, its fix commands, and the companion guidance all live in the
repo and are versioned with it, so teammates inherit the same behavior. Setup is two steps:
clone → init.

**Step 1 — Clone the skill into the project** (from the project root):

```bash
# Claude Code
git clone https://gitlab.liip.ch/nicolas.lanthemann/lowwwimpact-helper.git \
  .claude/skills/lowwwimpact-helper

# Cursor
git clone https://gitlab.liip.ch/nicolas.lanthemann/lowwwimpact-helper.git \
  .cursor/skills/lowwwimpact-helper
```

**Step 2 — Initialize the project.** The skill is auto-discovered from `.claude/skills/`, so just
ask Claude to initialize it:

```
Initialize lowwwimpact in this project
```

Init (Mode 0) copies the fix commands into `.claude/commands/` and wires the companion block into
`CLAUDE.md`. Once the commands are installed, you can re-run it with `/lowwwimpact-init`.

Nothing is written to `~/.claude` — everything stays in the project.

### Companion mode

After init, `CLAUDE.md` imports the companion guidance:

```markdown
@.claude/skills/lowwwimpact-helper/companion.md
```

This keeps a light sustainability lens active during normal development: when Claude is about to
add images, video, fonts, third-party scripts, a new JS dependency, or animation, it offers the
lower-impact option before implementing. It is a soft nudge (only when Claude writes the code) and
scoped to those integration moments — for a full audit or deep fix, escalate to the skill modes
(Review/Evaluate/Fix) or the matching `/xyz-optim` command.

### Updating

Plain copy — re-clone or overwrite the skill folder, then re-run init to refresh the copied
commands:

```bash
rm -rf .claude/skills/lowwwimpact-helper
git clone https://gitlab.liip.ch/nicolas.lanthemann/lowwwimpact-helper.git \
  .claude/skills/lowwwimpact-helper
# then, in Claude Code:
#   /lowwwimpact-init
```

`companion.md` lives inside the skill folder and is pulled in via the `@import`, so the companion
guidance updates automatically — no re-paste into `CLAUDE.md`.

### Prerequisites

**Playwright CLI** used by Modes 1-3 for live site inspection:

```bash
npm install -g @playwright/cli@latest
playwright-cli install-browser
playwright-cli install --skills
```

**Lighthouse CLI** used by Mode 1 for performance, accessibility, best-practices, and SEO scoring. Runs via `npx` - no separate installation needed if Node.js >= 18 is available. Verify: `npx lighthouse --version`.

**Figma MCP** required for Mode 4 when using Figma frame URLs. Not needed when running Mode 4 on a code project. Must be configured in your Claude Code or Cursor settings.

## File structure

```
lowwwimpact-helper/
├── SKILL.md                                    # Machine entry point - the coordinator
├── README.md                                   # This file
├── CHANGELOG.md
├── companion.md                                # Always-on nudge guidance (imported into project CLAUDE.md)
├── commands/                                   # Fix commands (copied to <project>/.claude/commands/ by init)
│   ├── animation-optim.md
│   ├── cache-compression-optim.md
│   ├── cms-media-optim.md
│   ├── compatibility-optim.md
│   ├── image-optim.md
│   ├── lowwwimpact-init.md                      # Mode 0 - project setup (copy commands + wire companion)
│   ├── media-optim.md
│   ├── measure-page-weight.md                  # Pre-cache page weight + Lighthouse scores
│   ├── native-feature-optim.md
│   ├── performance-optim.md
│   ├── reusable-components-optim.md
│   ├── seo-optim.md
│   ├── third-party-optim.md
│   └── typo-optim.md
├── agents/
│   ├── mode-1-review/
│   │   ├── images-audit.md                     # Image formats, compression, lazy loading
│   │   ├── media-fonts-audit.md                # Video facades, font loading, animations
│   │   ├── javascript-audit.md                 # Bundle size, loading strategy, native APIs
│   │   ├── css-html-audit.md                   # CSS size, semantic HTML, dark mode
│   │   ├── network-infra-audit.md              # Caching, compression, third-party domains
│   │   ├── carbon-performance-audit.md         # Page weight, carbon calculation, hosting
│   │   └── synthesizer.md                      # Merges 6 reports into final assessment
│   ├── mode-2-evaluate/
│   │   └── evaluator.md                        # Mode 2 - lowwwimpact criteria assessment
│   └── mode-4-specs-review/
│       ├── figma-inventory-agent.md            # Mode 4 (Figma path) - builds element-inventory.json
│       ├── code-inventory-agent.md             # Mode 4 (code path) - builds element-inventory.json
│       ├── dev-specs-writer.md                 # Mode 4 - developer specs from the inventory
│       └── designer-review-writer.md           # Mode 4 - designer review from the inventory
└── references/
    ├── lowwwimpact-criteria.json               # 27 MVP criteria with defaults
    ├── playwright-guide.md                     # Playwright CLI reference for agents
    ├── report-template.md                      # Report format specification
    ├── sustainability-checklist.md             # General sustainability checklist
    ├── carbon-measurement.md                   # SWD carbon model reference
    ├── code-efficiency.md                      # Code-level efficiency patterns
    ├── media-optimization.md                   # Image/video/font optimization reference
    ├── performance-budgets.md                  # Page weight budgets
    ├── ecodesign-requirements-concise.md       # 41 eco-design requirement blocks with curated links (Mode 4 dev specs)
    ├── eco-design-principles-for-designers.md  # Per-screen eco-design checklist (Mode 4 designer review)
    └── design-sobriety-principles.md           # Design Sobriety principles reference (Mode 4 designer review)
```

## Workspace outputs

Each mode writes to a `workspace/` directory in the current project:

```
workspace/
├── discovery.md                     # Site structure + resource inventory (Mode 1)
├── screenshots/                     # Visual evidence (Mode 1)
├── agents/                          # Per-agent audit reports (Mode 1)
├── sustainability-report.md         # Final synthesized report (Mode 1)
├── page-weights.json                # Cached page weights + Lighthouse scores (Mode 1 or /measure-page-weight)
├── lowwwimpact-evaluation.json      # Criteria assessment for human review (Mode 2)
├── fix-plan.md                      # Ranked fix plan with references (Mode 3)
├── element-inventory.json           # Shared discovery output, consumed by both writers (Mode 4)
├── dev-specs.md                     # Developer-facing eco-design specs (Mode 4)
└── eco-review.md                    # Designer-facing eco-review (Mode 4)
```

## Companion commands

These commands live in `commands/` in this repository. Init (Mode 0) copies them into the
project's `.claude/commands/` so they appear in your commands list. The skill references them by
name.

| Command | Domain |
|---------|--------|
| `/lowwwimpact-init` | Project setup: copy fix commands to `.claude/commands/` + wire companion `@import` into `CLAUDE.md` |
| `/measure-page-weight` | Pre-cache page weight + Lighthouse scores to `workspace/page-weights.json` |
| `/image-optim` | Image formats, responsive, lazy loading, compression |
| `/media-optim` | Video/audio: autoplay, preload, formats, facades |
| `/cms-media-optim` | CMS upload constraints, auto-processing |
| `/typo-optim` | WOFF2, subsetting, self-hosting, font-display |
| `/animation-optim` | GPU-safe properties, prefers-reduced-motion |
| `/third-party-optim` | Facade pattern for YouTube/Vimeo/Maps/social |
| `/native-feature-optim` | Replace JS with native HTML/CSS |
| `/cache-compression-optim` | Gzip/Brotli, Cache-Control, hashed filenames |
| `/performance-optim` | Page weight budget, Lighthouse, bundle analysis |
| `/reusable-components-optim` | Duplicate detection, shared utilities |
| `/compatibility-optim` | Progressive enhancement, @supports, polyfills |
| `/seo-optim` | Titles, descriptions, canonical, Open Graph, JSON-LD |

## Credits

- Criteria based on the [W3C Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) and the [lowwwimpact](https://lowwwimpact.com/) assessment framework
- Designer eco-review principles from [Sustainable Web Design](https://abookapart.com/products/sustainable-web-design) by Tom Greenwood (A Book Apart, 2021)
- Built at [Liip](https://www.liip.ch/en) as part of our digital sustainability practice

## License

MIT
