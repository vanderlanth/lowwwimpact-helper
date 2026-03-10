# lowwwimpact-helper

An AI agent skill for auditing web sustainability. It browses live websites with Playwright, produces prioritized carbon-impact reports, and evaluates sites against the [lowwwimpact](https://lowwwimpact.com/) assessment criteria — all from your IDE.

Built for [Cursor](https://cursor.com/) (Agent Skills) and [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Skills).

## What it does

Three modes of operation:

| Mode | Trigger | Output |
|------|---------|--------|
| **Review** | Provide a URL | Sustainability report with carbon grade, page weight breakdown, and prioritized findings |
| **Fix** | Provide a previous report | Guided walkthrough of fix commands in priority order |
| **Evaluate** | Say "evaluate" or "lowwwimpact" + URL | JSON assessment of 27 lowwwimpact criteria with pass/fail/partial answers |

### Review (Mode 1)

6 specialized audit agents run in parallel — images, media & fonts, JavaScript, CSS & HTML, network & infrastructure, carbon & performance — then a synthesizer agent produces the final report. Every finding is tagged with the specific fix command to run.

### Fix (Mode 2)

Reads a previous review report and walks you through running the appropriate `/xyz-optim` commands in priority order, starting with the highest bandwidth savings.

### Evaluate (Mode 3)

Evaluates a site against the 27 MVP criteria from the [W3C Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) as curated by the lowwwimpact project. Each criterion is pre-classified as automatable, partially automatable, or manual-only. The evaluator confirms or overrides pre-filled defaults using live Playwright inspection and outputs a structured JSON file for human review.

## Installation

Clone into your skills directory:

```bash
# Cursor
git clone https://gitlab.liip.ch/nicolas.lanthemann/lowwwimpact-helper.git ~/.cursor/skills/lowwwimpact-helper

# Claude Code
git clone https://gitlab.liip.ch/nicolas.lanthemann/lowwwimpact-helper.git ~/.claude/skills/lowwwimpact-helper
```

### Prerequisites

- **Playwright CLI** for live site inspection (used by all three modes)
- **`/xyz-optim` commands** (optional, for Fix mode) — 12 specialized fix playbooks. See [Companion Commands](#companion-commands) below.

## File structure

```
lowwwimpact-helper/
├── SKILL.md                              # Machine entry point — the coordinator
├── README.md                             # This file
├── CHANGELOG.md
├── agents/
│   ├── images-audit.md                   # Image formats, compression, lazy loading
│   ├── media-fonts-audit.md              # Video facades, font loading, animations
│   ├── javascript-audit.md               # Bundle size, loading strategy, native APIs
│   ├── css-html-audit.md                 # CSS size, semantic HTML, dark mode
│   ├── network-infra-audit.md            # Caching, compression, third-party domains
│   ├── carbon-performance-audit.md       # Page weight, carbon calculation, hosting
│   ├── synthesizer.md                    # Merges 6 reports into final assessment
│   └── evaluator.md                      # Mode 3 — lowwwimpact criteria assessment
└── references/
    ├── lowwwimpact-criteria.json          # 27 MVP criteria with defaults
    ├── playwright-guide.md               # Playwright CLI reference for agents
    ├── report-template.md                # Report format specification
    ├── sustainability-checklist.md        # General sustainability checklist
    ├── carbon-measurement.md             # SWD carbon model reference
    ├── code-efficiency.md                # Code-level efficiency patterns
    ├── media-optimization.md             # Image/video/font optimization reference
    └── performance-budgets.md            # Page weight budgets
```

## Companion commands

Fix mode delegates to these commands (installed separately in `~/.claude/commands/`):

| Command | Domain |
|---------|--------|
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
- Built at [Liip](https://www.liip.ch/en) as part of our digital sustainability practice

## License

MIT
