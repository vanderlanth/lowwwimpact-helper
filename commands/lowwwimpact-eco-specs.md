# lowwwimpact — Eco-design specs and review

Produce paired eco-design deliverables from Figma frames or from the current codebase: technical
specs for developers and a design review for designers.

Usage:
- `/lowwwimpact-eco-specs https://figma.com/design/...` — one or more frame URLs
- `/lowwwimpact-eco-specs` — no URLs, scans the current project

Run the **Eco-Specs Mode Workflow** defined in the skill (single source of truth): `SKILL.md` →
section **Eco-Specs Mode Workflow**. The summary below is for orientation.

No Playwright, no live URL needed. No flags — every run produces both outputs.

## Pipeline

1. **Detect the path.** Any `figma.com` URLs present → Figma path. None → code path.
2. **Build the inventory — once.**
   - *Figma path*: `phases/eco-specs/figma-inventory.md`. Per frame, one `get_screenshot` and one
     `get_design_context`. Designer annotations are extracted first and treated as the
     highest-confidence signal; visual detection fills the gaps.
   - *Code path*: `phases/eco-specs/code-inventory.md`. Project-wide grep passes for what exists,
     plus a per-screen scan of 2–3 representative page templates.
   - Either writes `workspace/element-inventory.json`. Do not proceed until it exists.
3. **Write both outputs** from that inventory. The two writers are independent — delegate in
   parallel where supported, otherwise run in sequence. Neither re-inspects Figma or the codebase.

## Outputs

| File | Audience | Content |
|---|---|---|
| `workspace/element-inventory.json` | — | Shared discovery output; both writers read it |
| `workspace/dev-specs.md` | Developers | Technical requirements per detected element type, sourced from `references/ecodesign-requirements-concise.md` with its curated documentation links |
| `workspace/eco-review.md` | Designers | Per-screen findings against the eco-design principles, top cross-screen actions, and a design sobriety section. Design decisions only — no code, no developer jargon. |

## Notes

- **Figma MCP required** for the Figma path only.
- The dev-specs writer does **not** run WebSearch. Every reference it emits comes from the
  `**Documentation**` blocks already curated in `references/ecodesign-requirements-concise.md`,
  which makes the output deterministic and keeps invented links out.
- The two writers are kept separate on purpose: their tone rules contradict each other. The spec
  writer requires inline code for attributes and properties; the review writer forbids mentioning
  file formats, caching, or lazy loading at all.
