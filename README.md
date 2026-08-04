# lowwwimpact-helper

A sustainability skill for web projects. It audits live sites with Playwright and evaluates them
against the [lowwwimpact](https://lowwwimpact.com/) criteria, generates paired eco-design
deliverables from Figma frames or a codebase, and keeps a light sustainability lens active during
everyday development.

Plain markdown throughout, so it runs in [Claude Code](https://docs.anthropic.com/en/docs/claude-code),
[opencode](https://opencode.ai/), and [Cursor](https://cursor.com/) — see
[Host and model support](#host-and-model-support).

## Modes

Three modes. Named, not numbered.

| Mode | Trigger | Output |
|------|---------|--------|
| **Passive** | Always on after install — never invoked | Lower-impact suggestions at the moment you add an image, font, embed, dependency, or animation |
| **Evaluate** | `/lowwwimpact-evaluate <url>` | `sustainability-report.md` + `lowwwimpact-evaluation.json` |
| **Eco-Specs** | `/lowwwimpact-eco-specs [figma urls]` | `dev-specs.md` + `eco-review.md` |

### Passive

Installed into the project's `AGENTS.md`, so it is in context for every session without being
invoked. At integration moments it offers the lower-impact option and points at the relevant block
of `references/ecodesign-requirements-concise.md`.

It is advisory only. It never blocks, and it proceeds with your choice if you decline. It also only
fires when the assistant is writing the code — it does not review code you wrote yourself. For that,
run Evaluate.

### Evaluate

One command, one pipeline: crawl the site, run six audit phases in parallel, synthesize a ranked
report, measure page weight and Lighthouse, then evaluate all 27 lowwwimpact criteria — the MVP set
from the [W3C Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/).

Supports 1–2 user journeys to measure cumulative page weight across a real task flow, and pages
behind a login.

**Every run measures cold.** There is no caching or artifact reuse: the measurement semantics depend
on genuine cold loads, and reused numbers would not be comparable between runs.

`workspace/lowwwimpact-evaluation.json` has a **hard structural contract** defined by
`references/valid-example.json`. Validate any run with:

```bash
python3 scripts/validate-evaluation.py workspace/lowwwimpact-evaluation.json
```

`/lowwwimpact-evaluate --debug <url>` is the measurement-only variant — auth plus weight and
Lighthouse, nothing else. Use it to confirm a login flow works before a full run.

### Eco-Specs

Runs discovery once and writes two audience-specific files from it. No flags — every run produces
both. No Playwright, no live URL needed.

- **Figma frames:** pass one or more `figma.com` frame URLs. Uses the Figma MCP, reading designer
  annotations first and filling gaps visually.
- **Code project:** pass no URLs. Greps the project, then scans 2–3 representative page templates
  individually as "screens".

Either path writes `workspace/element-inventory.json`; both writers read it, so nothing is inspected
twice.

| Output | Audience | Content |
|--------|----------|---------|
| `dev-specs.md` | Developers | Technical requirements per detected element type, from `references/ecodesign-requirements-concise.md` with its curated documentation links |
| `eco-review.md` | Designers | Per-screen findings against the eco-design principles, top actions, and a Design Sobriety section. Design decisions only — no code, no jargon. |

## Installation

Install **per project**, so the skill and its guidance are versioned with the repo and teammates
inherit the same behavior. Two steps: clone, then init.

**Step 1 — clone into the project**, at the path your tool expects:

```bash
# Claude Code
git clone <repo> .claude/skills/lowwwimpact-helper

# opencode
git clone <repo> .opencode/lowwwimpact-helper

# Cursor
git clone <repo> .cursor/skills/lowwwimpact-helper
```

**Step 2 — initialize:**

```
Initialize lowwwimpact in this project
```

Init detects which host it is running under, copies the commands into that host's command directory,
and injects passive mode into `AGENTS.md` between marker comments. On Claude Code it also adds a
single `@AGENTS.md` line to `CLAUDE.md` so both files stay in sync. Once the commands are installed
you can re-run it as `/lowwwimpact-init`.

Nothing is written outside the project.

### Updating

Re-clone or overwrite the skill folder, then re-run `/lowwwimpact-init`. This refreshes both the
copied commands and the passive block in `AGENTS.md`.

Passive content is **injected rather than imported**, because `@path` imports are Claude Code syntax
and the `AGENTS.md` convention has no portable import mechanism. The trade-off is that the block
goes stale until you re-run init.

## Host and model support

Host compatibility and model capability are separate questions.

**Hosts.** Everything is plain markdown. Commands carry no YAML frontmatter, so the same file works
unchanged in `.claude/commands/`, `.opencode/commands/`, and `.cursor/commands/`. Phases declare
their inputs and outputs and pass no parameters, so a host without subagents runs them in sequence
and gets the same result — only slower.

**Models.** The phases are not equally demanding:

| Phase | Instruction weight | Runs on a modest local model? |
|---|---|---|
| Each audit phase | ~2k tokens | Yes |
| Eco-specs inventory and writers | ~2k + 6.5k reference | Yes |
| **Criteria evaluation** | **~20.5k tokens** before any page data | **No** — needs a large-context, capable model |

The criteria evaluation loads the evaluator instructions plus the 27-criteria file, ingests network
data, and must emit a strictly-shaped JSON. A small local model will handle eco-specs and the
individual audits, and will not produce a trustworthy evaluation JSON. Run the validator to find
out rather than assuming.

## Auditing pages behind a login

**1. Supply credentials via `.env`** at the project root. The skill reads `*_USER` / `*_LOGIN` /
`*_EMAIL` for the username and `*_PASS` / `*_PASSWORD` for the password:

```env
SITE_USER=you@example.com
SITE_PASS=your-password
```

If no matching variables are found, it asks interactively.

**2. Run an audit.** On the first run the skill detects the login redirect, logs in, and saves the
session to `workspace/auth-state.json` (Playwright `storageState` format). Later measurements load
it automatically. On a public site this is a no-op.

**3. Verify auth in isolation first (recommended):**

```
/lowwwimpact-evaluate --debug https://example.com/dashboard
```

Runs auth plus measurement only, writes `workspace/debug-weights.json`, prints a per-page summary.
If measurement lands on the login page, re-run to overwrite `auth-state.json`.

> Keep `.env` and `workspace/auth-state.json` out of version control — they hold credentials and a
> live session.

## Prerequisites

**Playwright CLI** — required by Evaluate only:

```bash
npm install -g @playwright/cli@latest
playwright-cli install-browser
playwright-cli install --skills
```

**Lighthouse** — runs via `npx`, no install needed with Node.js ≥ 18. Verify:
`npx lighthouse --version`. If unavailable, scores are omitted and noted.

**Figma MCP** — required by Eco-Specs only when passing Figma frame URLs.

**Python 3** — for the evaluation validator.

## File structure

```
lowwwimpact-helper/
├── SKILL.md                                    # Entry point and coordinator
├── README.md
├── CHANGELOG.md
├── passive.md                                  # Passive mode — injected into project AGENTS.md
├── scripts/
│   └── validate-evaluation.py                  # Enforces the evaluation output contract
├── commands/
│   ├── lowwwimpact-init.md                     # Install into the current project
│   ├── lowwwimpact-evaluate.md                 # Run the evaluate pipeline
│   ├── lowwwimpact-eco-specs.md                # Run the eco-specs pipeline
│   ├── measure-page-weight.md
│   └── …12 /xyz-optim fix commands
├── phases/
│   ├── evaluate/
│   │   ├── images-audit.md
│   │   ├── media-fonts-audit.md
│   │   ├── javascript-audit.md
│   │   ├── css-html-audit.md
│   │   ├── network-infra-audit.md
│   │   ├── carbon-performance-audit.md
│   │   ├── synthesizer.md                      # Merges the six reports
│   │   └── evaluator.md                        # Criteria assessment
│   └── eco-specs/
│       ├── figma-inventory.md
│       ├── code-inventory.md
│       ├── dev-specs-writer.md
│       └── designer-review-writer.md
└── references/
    ├── lowwwimpact-criteria.json               # The 27 criteria
    ├── valid-example.json                      # Output contract — never edit
    ├── ecodesign-requirements-concise.md       # 41 requirement blocks with curated links
    ├── eco-design-principles-for-designers.md
    ├── design-sobriety-principles.md
    ├── auth-measure-pipeline.md                # Shared auth + measurement
    ├── playwright-guide.md
    ├── report-template.md
    ├── sustainability-checklist.md
    ├── carbon-measurement.md
    ├── code-efficiency.md
    ├── media-optimization.md
    └── performance-budgets.md
```

## Workspace outputs

```
workspace/
├── discovery.md                     # Site structure + resource inventory (Evaluate)
├── phases/                          # Per-phase audit reports (Evaluate)
├── page-weights.json                # Page weights + Lighthouse scores (Evaluate)
├── sustainability-report.md         # Ranked audit report (Evaluate)
├── lowwwimpact-evaluation.json      # Criteria assessment — hard contract (Evaluate)
├── debug-weights.json               # Measurement-only output (--debug)
├── auth-state.json                  # Saved login session, when needed
├── element-inventory.json           # Shared discovery output (Eco-Specs)
├── dev-specs.md                     # Developer specs (Eco-Specs)
└── eco-review.md                    # Designer review (Eco-Specs)
```

## Fix commands

Copied into your host's command directory by init. The skill references them by name — it contains
no fix logic itself.

| Command | Domain |
|---------|--------|
| `/lowwwimpact-init` | Install into the current project |
| `/lowwwimpact-evaluate` | Run the evaluate pipeline |
| `/lowwwimpact-eco-specs` | Run the eco-specs pipeline |
| `/measure-page-weight` | Page weight + Lighthouse → `workspace/page-weights.json` |
| `/image-optim` | Image formats, responsive, lazy loading, compression |
| `/media-optim` | Video/audio: autoplay, preload, formats, facades |
| `/cms-media-optim` | CMS upload constraints, auto-processing |
| `/typo-optim` | WOFF2, subsetting, self-hosting, font-display |
| `/animation-optim` | GPU-safe properties, prefers-reduced-motion |
| `/third-party-optim` | Facades for YouTube/Vimeo/Maps/social |
| `/native-feature-optim` | Native HTML/CSS over JS |
| `/cache-compression-optim` | Gzip/Brotli, Cache-Control, hashed filenames |
| `/performance-optim` | Page weight budget, Lighthouse, bundle analysis |
| `/reusable-components-optim` | Duplicate detection, shared utilities |
| `/compatibility-optim` | Progressive enhancement, @supports, polyfills |
| `/seo-optim` | Titles, descriptions, canonical, Open Graph, JSON-LD |

## Credits

- Criteria based on the [W3C Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/)
  and the [lowwwimpact](https://lowwwimpact.com/) assessment framework
- Designer eco-review principles from
  [Sustainable Web Design](https://abookapart.com/products/sustainable-web-design) by Tom Greenwood
  (A Book Apart, 2021)
- Built at [Liip](https://www.liip.ch/en) as part of our digital sustainability practice

## License

MIT
