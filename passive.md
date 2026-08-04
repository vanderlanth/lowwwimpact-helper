## Sustainable by default (lowwwimpact passive mode)

When you are about to add any of the elements below, **first offer the lower-impact option and ask
before implementing**. One short suggestion — advise, don't nag. If the developer declines or has a
constraint, proceed with their choice. This never blocks.

Full guidance lives in `references/ecodesign-requirements-concise.md` inside the skill folder, in
41 numbered blocks. Read the relevant block before proposing an implementation — this table only
says which one applies.

| When adding… | Read block | Then run |
|---|---|---|
| **Images** | 1 Raster images · 2 Hero/above-fold · 3 Decorative | `/image-optim` |
| **Icons, illustrations, SVG** | 4 Icons · 5 SVG assets · 13 Icon fonts | `/image-optim` |
| **Video or audio** | 6 Self-hosted video · 7 YouTube/Vimeo · 8 Audio · 9 Animated GIFs | `/media-optim` |
| **Animation or scroll effects** | 10 Animation & motion · 11 Scroll effects | `/animation-optim` |
| **Fonts** | 12 Custom web fonts · 18 Hosted font services | `/typo-optim` |
| **Third-party embed, map, chat, social, analytics** | 14 Embeds & facades · 15 Maps · 16 Chat & social · 17 Analytics · 19 Cookie consent | `/third-party-optim` |
| **Carousel, form, search, live content** | 20 Carousels · 21 Forms · 22 Search & navigation · 23 Live content | `/native-feature-optim` |
| **Dark mode or theming** | 24 Dark mode & colour scheme · 40 Colour & contrast | — |
| **A new JS dependency** | 31 JS delivery & dependency choice · 32 Native features over libraries | `/native-feature-optim` |
| **CSS or markup** | 29 HTML semantics · 30 CSS delivery · 33 Component reuse | `/reusable-components-optim` |
| **Caching, compression, hosting** | 34 Caching · 35 Compression · 36 Hosting | `/cache-compression-optim` |
| **CMS fields or block config** | 26 Upload constraints · 27 Edition constraints · 28 Editor guidance | `/cms-media-optim` |

The blocks are advisory. Deadlines, client requirements, and disagreement are all valid reasons to
skip one. Nothing here should block a merge.

### Budgets

When a change would push a page over one of these, say so and offer the lighter path.

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

For a full audit run `/lowwwimpact-evaluate <url>`; for design-stage specs run
`/lowwwimpact-eco-specs`.
