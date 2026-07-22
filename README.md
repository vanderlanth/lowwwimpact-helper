# lowwwimpact-helper

An AI agent skill for auditing web sustainability. It browses live websites with Playwright, produces prioritized carbon-impact reports, and evaluates sites against the [lowwwimpact](https://lowwwimpact.com/) assessment criteria. Includes modes for generating developer eco-design specs and designer eco-review PDFs — from Figma frames or directly from a code project.

Built for [Cursor](https://cursor.com/) (Agent Skills) and [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Skills).

## What it does

Five modes of operation:

| Mode | Trigger | Prompt example | Output |
|------|---------|----------------|--------|
| **1 - Review** | Provide a URL | `Use /lowwwimpact-helper in mode 1 to review https://www.liip.ch` | Sustainability report with carbon grade, page weight breakdown, and prioritized findings |
| **2 - Evaluate** | Say "evaluate" / "lowwwimpact" / "assessment" / "criteria" + URL. Prompts for 1-2 optional user journeys before starting. | `Use /lowwwimpact-helper in mode 2 to evaluate https://www.liip.ch. User journey: from the homepage, find a blog post and read it.` | JSON assessment of 27 lowwwimpact criteria with pass/fail/partial answers, plus per-journey page weight data. Works standalone — run `/measure-page-weight <url>` first for best accuracy, or provide Mode 1 output for full evidence. |
| **3 - Fix** | Say "fix" / "fix plan" | `Use /lowwwimpact-helper in mode 3 to generate a fix plan` | Persistent `fix-plan.md` ranked by KB savings, with criteria IDs and curated web references. Requires Mode 1 + Mode 2 output. |
| **4 - Specs** | "specs" / "dev specs" / "eco specs" — with Figma frame URLs or without (inspects current project) | With Figma: `Use /lowwwimpact-helper in mode 4 to generate eco specs from these Figma frames: https://figma.com/design/...` · With code: `Use /lowwwimpact-helper in mode 4 to generate eco specs for this project` | Developer-facing `dev-specs.md` with technical sustainability requirements per element type and curated references |
| **5 - Designer Eco-Review** | "eco review" / "designer review" — with Figma frame URLs or without (inspects current project) | With Figma: `Use /lowwwimpact-helper in mode 5 to do an eco review for designers: https://figma.com/design/...` · With code: `Use /lowwwimpact-helper in mode 5 to do an eco review for this project` | Designer-facing `eco-review.md` + PDF with per-screen findings against eco-design principles |

### Mode 1 - Review

6 specialized audit agents run in parallel (images, media and fonts, JavaScript, CSS and HTML, network and infrastructure, carbon and performance) then a synthesizer agent produces the final report. Every finding is tagged with the specific fix command to run.

### Mode 2 - Evaluate

Evaluates a site against the 27 MVP criteria from the [W3C Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) as curated by the lowwwimpact project. Uses a priority chain for evidence: `workspace/page-weights.json` (from `/measure-page-weight` or Mode 1) → Mode 1 reports → standalone Lighthouse + Playwright inspection. Supports 1-2 user journeys to measure page weight across a real task flow. Outputs a structured JSON file for human review.

### Mode 3 - Fix

Reads `workspace/lowwwimpact-evaluation.json` and `workspace/sustainability-report.md`, builds a fix index ranked by KB savings, searches for authoritative references per fix command, and writes a persistent `workspace/fix-plan.md`.

### Mode 4 - Specs

Fully independent of Modes 1-3. Detects which element types are present (images, fonts, video, carousels, third-party embeds, animations, live feeds, cookie consent) and generates a concise developer-facing markdown file of technical sustainability requirements. Each spec section includes 2-3 curated implementation references aimed at junior developers.

**Two input paths:**
- **Figma frames:** Provide one or more `figma.com` frame URLs — uses the Figma MCP for visual and structural analysis
- **Code project:** Provide no URLs — scans the current project directory using grep across template files, CSS, JavaScript, and `package.json`

### Mode 5 - Designer Eco-Review

Fully independent of Modes 1-4. Analyzes 2-3 screens against eco-design principles for designers, and produces a clean PDF report with per-screen findings and a Design Sobriety section drawn from the Sustainable Web Design reference. All findings are expressed as design decisions: no code, no developer jargon.

**Two input paths:**
- **Figma frames:** Provide 2-3 `figma.com` frame URLs — uses the Figma MCP for visual and structural analysis
- **Code project:** Provide no URLs — identifies 2-3 main page templates in the current project and treats each as a screen

## Installation

Clone into your skills directory:

```bash
# Cursor
git clone https://gitlab.liip.ch/nicolas.lanthemann/lowwwimpact-helper.git ~/.cursor/skills/lowwwimpact-helper

# Claude Code
git clone https://gitlab.liip.ch/nicolas.lanthemann/lowwwimpact-helper.git ~/.claude/skills/lowwwimpact-helper
```

Then symlink the companion commands so they appear in your commands list:

```bash
# Claude Code
for f in ~/.claude/skills/lowwwimpact-helper/commands/*.md; do
  ln -sf "$f" ~/.claude/commands/$(basename "$f")
done

# Cursor
for f in ~/.cursor/skills/lowwwimpact-helper/commands/*.md; do
  ln -sf "$f" ~/.cursor/commands/$(basename "$f")
done
```

### Prerequisites

**Playwright CLI** used by Modes 1-3 for live site inspection:

```bash
npm install -g @playwright/cli@latest
playwright-cli install-browser
playwright-cli install --skills
```

**Lighthouse CLI** used by Mode 1 for performance, accessibility, best-practices, and SEO scoring. Runs via `npx` - no separate installation needed if Node.js >= 18 is available. Verify: `npx lighthouse --version`.

**Figma MCP** required for Modes 4 and 5 when using Figma frame URLs. Not needed when running those modes on a code project. Must be configured in your Claude Code or Cursor settings.

## File structure

```
lowwwimpact-helper/
├── SKILL.md                                    # Machine entry point - the coordinator
├── README.md                                   # This file
├── CHANGELOG.md
├── commands/                                   # Companion fix commands (symlinked to ~/.claude/commands/)
│   ├── animation-optim.md
│   ├── cache-compression-optim.md
│   ├── cms-media-optim.md
│   ├── compatibility-optim.md
│   ├── image-optim.md
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
│   ├── mode-4-specs/
│   │   ├── figma-specs-agent.md                # Mode 4 (Figma path) - developer eco-design spec writer
│   │   └── code-specs-agent.md                 # Mode 4 (code path) - developer eco-design spec writer
│   └── mode-5-designer-review/
│       ├── eco-designer-review-agent.md        # Mode 5 (Figma path) - designer eco-review and PDF
│       └── code-eco-review-agent.md            # Mode 5 (code path) - designer eco-review and PDF
└── references/
    ├── lowwwimpact-criteria.json               # 27 MVP criteria with defaults
    ├── playwright-guide.md                     # Playwright CLI reference for agents
    ├── report-template.md                      # Report format specification
    ├── sustainability-checklist.md             # General sustainability checklist
    ├── carbon-measurement.md                   # SWD carbon model reference
    ├── code-efficiency.md                      # Code-level efficiency patterns
    ├── media-optimization.md                   # Image/video/font optimization reference
    ├── performance-budgets.md                  # Page weight budgets
    ├── figma-specs.md                          # Spec content per element type (Mode 4)
    ├── eco-design-principles-for-designers.md  # Per-screen eco-design checklist (Mode 5)
    └── design-sobriety-principles.md           # Design Sobriety principles reference (Mode 5)
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
├── dev-specs.md                     # Developer-facing eco-design spec file (Mode 4)
├── eco-review.md                    # Designer eco-review source markdown (Mode 5)
└── eco-review.pdf                   # Exported PDF for designer handoff (Mode 5)
```

## Companion commands

These commands live in `commands/` in this repository and are symlinked to `~/.claude/commands/`
during installation (see symlink step above). The skill references them by name.

| Command | Domain |
|---------|--------|
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
