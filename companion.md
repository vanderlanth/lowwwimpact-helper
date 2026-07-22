# lowwwimpact companion — sustainable-by-default

This file is imported into the project's `CLAUDE.md`. It keeps a light sustainability lens active
during normal development.

**When you (Claude) are about to add any of the elements below, first offer the lower-impact
option and ask before implementing.** Keep it to one short suggestion — advise, don't nag. If the
developer declines or has a constraint, proceed with their choice. For a full audit or a deep fix,
escalate to the `lowwwimpact-helper` skill modes or the matching `/xyz-optim` command.

## Integration moments — prefer the lower-impact option

| When adding… | Prefer | Escalate to |
|---|---|---|
| **Images** | WebP/AVIF with fallback, `srcset`/`sizes`, `loading="lazy"` below the fold, explicit `width`/`height`, descriptive `alt`. Use CSS/SVG over raster where possible. | `/image-optim` |
| **Video / audio** | No autoplay; `preload="none"` + poster. Click-to-load facade for YouTube/Vimeo embeds. Captions via `<track>`. | `/media-optim`, `/third-party-optim` |
| **Fonts** | WOFF2 only, subsetted, self-hosted, `font-display: swap`, ≤2 weights, system fallback stack. Reserve custom fonts for headings/brand. | `/typo-optim` |
| **Third-party embed / script** | Click-to-load facade; self-host what you can; lightweight analytics (Plausible/Fathom/Umami). Keep third-party domains low. | `/third-party-optim` |
| **New JS dependency** | Check for a native API first — `fetch` (not axios), `Intl` (not moment), `<dialog>`/`<details>` (not modal/accordion libs), `IntersectionObserver`, `scroll-behavior: smooth`. Weigh the bundle cost. | `/native-feature-optim`, `/reusable-components-optim` |
| **Animation** | Compositor-only properties (`transform`, `opacity`); honor `prefers-reduced-motion`; no GIFs (use CSS/MP4/animated WebP). | `/animation-optim` |
| **CSS / HTML** | Semantic elements, minified output, critical CSS inlined, dark mode via `prefers-color-scheme`. Prefer CSS over JS for toggles/animations. | `/native-feature-optim` |

## Budgets (quick reference)

| Metric | Budget |
|--------|--------|
| Total page weight | < 1.5 MB |
| Images | < 500 KB |
| JavaScript | < 200 KB |
| CSS | < 70 KB |
| Fonts | < 50 KB |
| HTML | < 50 KB |
| HTTP requests | < 30 |
| Third-party domains | < 4 |
| CO2/pageview (grade A) | < 0.06 g |

When a change would push a page over one of these budgets, say so and offer the lighter path.
