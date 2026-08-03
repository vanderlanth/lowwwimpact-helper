# Eco-Design Requirements

Implementation suggestions for building a lower-impact website.

## How to use this


Working with an AI coding assistant? Add this file to your project's reference material
(`docs/`, or linked from `CLAUDE.md`) so it can propose implementations that already fit.

**Everything here is advisory.** Deadlines, client requirements, and disagreement are all valid
reasons to skip an item. Nothing here should block a merge.

---

## Images & graphics

### 1. Raster images / photos

_Applies to: `<img>`, `<picture>`, CSS `background-image`, CMS-uploaded photos._

- Serve AVIF or WebP with a JPEG/PNG fallback via `<picture>`.
- Use `srcset` and `sizes` so each device gets an appropriate width.
- Compress — around 80% quality is usually indistinguishable.
- Resize server-side; never ship an original scaled down by CSS.
- Add `loading="lazy"` and `decoding="async"` below the fold.
- Set `width`/`height` or `aspect-ratio` to prevent layout shift.
- Give meaningful images descriptive `alt` text.
- Self-host, or use an image service like [rokka.io](https://rokka.io/) that handles format,
  resizing, and compression for you.

**Documentation**
- [MDN — Responsive images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)

### 2. Hero & above-the-fold images

_Applies to: the largest image on first paint — hero banners, article lead images._

- Don't lazy-load it. Add `fetchpriority="high"`.
- Preload it when discovered late (CSS background, inside a carousel).
- Never preload and lazy-load the same image.
- Ask whether it needs to be a photo — a gradient, SVG, or bold type costs a fraction.

**Documentation**
- [web.dev — Optimize Largest Contentful Paint](https://web.dev/articles/optimize-lcp)

### 3. Decorative & background images

_Applies to: images carrying no information — textures, dividers, ambient photography._

- Mark as decorative: `alt=""`, or `aria-hidden="true"` where appropriate.
- Replace with CSS where possible — gradients, shadows, borders.
- Crop tighter and blur non-essential areas; both compress far better.
- Drop them entirely on small viewports via `<picture>` `media` or a media query.

**Documentation**
- [MDN — Using CSS gradients](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_images/Using_CSS_gradients)

### 4. Icons & illustrations

_Applies to: icon sets, pictograms, logos, flat illustrations._

- Use SVG, not raster or icon fonts.
- Inline small reused icons; use a sprite or `<use>` for larger sets.
- Add `aria-hidden="true"` to icons beside a visible label.
- Give standalone icon buttons an `aria-label`.

**Documentation**
- [CSS-Tricks — Accessible SVG icons](https://css-tricks.com/accessible-svg-icons/)

### 5. SVG assets

_Applies to: every `.svg` in the project._

- Run through SVGO — exported files carry editor metadata and hidden layers.
- Simplify paths before export; fewer nodes, smaller file.
- Set `viewBox` and let one file scale, rather than exporting per size.
- Never embed raster images inside an SVG.

**Documentation**
- [SVGO](https://www.npmjs.com/package/svgo)

---

## Video, audio & motion

### 6. Self-hosted video

_Applies to: any `<video>` served from your own infrastructure._

- Never autoplay. Use `preload="none"` with a `poster`.
- Always expose native `controls`.
- WebM primary source, MP4 fallback.
- Re-encode and keep clips short — never upload a camera original.
- Add captions via `<track kind="captions">` and a transcript for informational content.
- For explanatory content, a code-driven animation is often a fraction of the weight.

**Documentation**
- [MDN — `<video>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/video)

### 7. YouTube / Vimeo embeds

_Applies to: iframes pointing at a video host._

- Put the embed behind a facade — self-hosted poster plus a play button that swaps in the
  iframe on click. Costs nothing until someone wants it.
- Use `youtube-nocookie.com`, not `youtube.com`.
- Add `loading="lazy"`; restrict `allow` to what's needed.
- The facade must be a real button, keyboard-reachable, named for what it plays.
- Move focus into the player once it loads.

**Documentation**
- [lite-youtube-embed](https://github.com/paulirish/lite-youtube-embed)

### 8. Audio content

_Applies to: `<audio>`, podcast players, embedded audio._

- `preload="none"`, no autoplay, native `controls`.
- Provide a transcript — for audio it's the primary alternative.
- Use a speech-appropriate bitrate for spoken word, not a music-grade encode.
- Platform-hosted audio: use the facade pattern from block 7.

**Documentation**
- [MDN — `<audio>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/audio)

### 9. Animated GIFs

_Applies to: any `.gif` used for motion._

- Don't. Every frame is stored as a full image — the least efficient moving format there is.
- Replace with a muted, looping, `playsinline` `<video>`.
- Use animated WebP where a single image file is genuinely required.
- Use CSS or SVG animation for loading indicators.

**Documentation**
- [web.dev — Replace animated GIFs with video](https://web.dev/articles/replace-gifs-with-videos)

### 10. Animation & motion

_Applies to: CSS transitions and keyframes, JS animation, Lottie, looping UI motion._

- Honour `prefers-reduced-motion: reduce` — but replace the animation, never delete content.
- Animate `transform` and `opacity` only; layout properties force reflow every frame.
- Give looping animations a visible pause control.
- Keep simultaneous animations few — that's what drains a battery, not any single one.
- Motion that guides, confirms, or explains earns its cost. Decoration usually doesn't.

**Documentation**
- [MDN — `prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)

### 11. Scroll effects

_Applies to: parallax, scroll-triggered reveals, scroll-linked animation, infinite scroll._

- Never hijack scrolling — it breaks keyboard use and assistive technology.
- Use CSS scroll-driven animations or `IntersectionObserver`, not a `scroll` handler.
- Disable scroll-triggered motion under `prefers-reduced-motion`.
- Prefer an explicit "load more" to infinite scroll, which keeps fetching content nobody
  reaches and makes the footer unreachable.
- Where infinite scroll is required, announce new content and keep the URL in sync.

**Documentation**
- [MDN — Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)

---

## Typography

### 12. Custom web fonts

_Applies to: every `@font-face` and hosted font service._

- Self-host. A font service adds a third party and removes your control.
- WOFF2 only.
- Subset to the character sets you use — Latin-only is dramatically smaller.
- Load at most two weights; use one variable font if you need more variation.
- Declare a system fallback stack and use `font-display: swap`.
- Preload fonts used in above-the-fold text.
- Consider system fonts for body copy, custom faces for headings and brand.

**Documentation**
- [web.dev — Best practices for fonts](https://web.dev/articles/font-best-practices)

### 13. Icon fonts

_Applies to: FontAwesome, Material Icons, any glyph-based icon system._

- Don't use them — use SVG (block 4). An icon font downloads every glyph for the three you
  use, and announces meaningless characters to screen readers.
- Where one can't be removed: subset it, and mark every icon `aria-hidden="true"`.

**Documentation**
- [CSS-Tricks — Icon fonts vs. SVG](https://css-tricks.com/icon-fonts-vs-svg/)

---

## Third-party

### 14. Third-party embeds & facades

_Applies to: any iframe, script, or widget from a domain you don't control._

- Put non-essential embeds behind a facade — static preview, real thing on click.
- Self-host what you can: fonts, icons, small libraries, static assets.
- Add `loading="lazy"`, a restrictive `sandbox`, and only the `allow` permissions needed.
- Load scripts with `defer` or `async` so a third party can't block rendering.
- Audit periodically — embeds accumulate quietly and outlive their purpose.

**Documentation**
- [Chrome — Third-party facades](https://developer.chrome.com/docs/lighthouse/performance/third-party-facades)

### 15. Maps

_Applies to: Google Maps, Mapbox, OpenStreetMap, any interactive map embed._

- Replace the interactive map with a static image plus a link. Most visitors only need to see
  where something is.
- Provide the address as selectable text — more useful than the map, and free.
- Link out to the user's own map app rather than embedding a canvas for one pin.
- Load tiles only after consent where the provider sets tracking cookies.

**Documentation**
- [OpenStreetMap — Static map images](https://wiki.openstreetmap.org/wiki/Static_map_images)

### 16. Chat widgets & social feeds

_Applies to: live chat, chatbots, social feed embeds, review widgets, share buttons._

- Question whether it belongs. These are among the heaviest third parties on a typical site and
  are used by a small minority of visitors.
- Load chat on click, not on page load.
- Replace feed embeds with server-fetched cached content, or a link to the profile.
- Use plain links for sharing — they cost nothing and don't track your visitors.

**Documentation**
- [Sharing Buttons](https://sharingbuttons.io/)

### 17. Analytics & tag managers

_Applies to: analytics, tag managers, heatmaps, session recording, A/B testing._

- Prefer a lightweight privacy-respecting tool over a full tag manager.
- Load nothing before consent where cookies or personal data are involved.
- Remove tracking you don't use — tag managers outlive the campaigns that filled them.
- Run heatmaps and session recording for a defined period, then remove them.
- Let users stop tracking after accepting.

**Documentation**
- [Plausible](https://plausible.io/) — or [Umami](https://umami.is/), [Matomo](https://matomo.org/)

### 18. Hosted font & asset services

_Applies to: Google Fonts, Adobe Fonts, CDN script tags, icon CDNs._

- Self-host fonts as subsetted WOFF2.
- Self-host libraries. Browsers partition caches per site, so the shared-CDN-cache argument no
  longer holds.
- Bundle small libraries into your own build rather than adding a request.
- Each vendor domain costs a DNS lookup, connection, and TLS handshake before any content.

**Documentation**
- [Chrome — HTTP cache partitioning](https://developer.chrome.com/blog/http-cache-partitioning)

### 19. Cookie consent & consent-gated loading

_Applies to: the cookie banner and everything gated behind it._

- No non-essential cookie and no third-party request before consent.
- Refusing must be as easy as accepting — same prominence, same clicks.
- Fully keyboard-operable and screen-reader accessible, with managed focus.
- Let users review, change, and revoke from a persistent link.
- Wire consent to actual loading, not a flag — on refusal the script is never requested.
- Keep the banner itself light; a heavy script to ask about tracking is a poor trade.

**Documentation**
- [W3C WAI — Modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

---

## Content & interaction patterns

### 20. Carousels, sliders & galleries

_Applies to: hero carousels, product galleries, logo strips, testimonial sliders._

- Load the first slide only; lazy-load the rest on interaction or near-viewport.
- Provide keyboard-operable previous/next controls.
- Auto-rotation needs a pause control, and stops under `prefers-reduced-motion`.
- Reduce the number of slides — a carousel is often an avoided content decision.
- Consider a grid or one strong image instead; both are lighter.

**Documentation**
- [W3C WAI — Carousel pattern](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/)

### 21. Forms

_Applies to: any form. Accessibility requirements are in block 41._

- Ask for the minimum — every field is data to transmit, store, and delete.
- Use native input types (`email`, `tel`, `date`, `url`) and native constraint validation
  before reaching for a library.
- Use `<datalist>` rather than a custom autocomplete.
- Compress and limit file uploads; state accepted formats in the interface.
- Load CAPTCHA on the form that needs it, not on every page.

**Documentation**
- [MDN — Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation)

### 22. Search & navigation

_Applies to: navigation, menus, search, breadcrumbs, internal linking._

- Every failed attempt to find something is an extra page load. Clear navigation is a
  bandwidth decision.
- Surface subcategories in the menu instead of routing people through landing pages.
- Remove gateway and splash pages.
- Provide search on content-heavy sites; keep results server-rendered and paginated rather
  than shipping a client-side index of the whole site.
- Make link text descriptive so users can judge a destination before loading it.

**Documentation**
- [NN/g — Information scent](https://www.nngroup.com/articles/information-scent/)

### 23. Live content & feed refresh

_Applies to: polling, auto-refresh, WebSockets, live tickers, notification badges._

- Fetch on user action rather than on a timer wherever possible.
- Where polling is needed, use the longest interval the content tolerates.
- Stop polling when the tab is hidden; resume on focus.
- Prefer server push (WebSocket, SSE) to frequent short-interval polling.
- Never use `<meta http-equiv="refresh">` to reload on a timer.

**Documentation**
- [MDN — Page Visibility API](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API)

### 24. Dark mode & colour scheme

_Applies to: theming and any light/dark implementation._

- Respect `prefers-color-scheme` by default.
- Design both themes properly — dark is not light inverted.
- Verify contrast in both; palettes that pass in light often fail in dark.
- Use CSS custom properties so a theme is a variable swap, not a second stylesheet.
- Set `color-scheme` so native controls follow the theme.
- Treat the OLED saving as a tiebreaker, not a justification — it's small next to imagery.

**Documentation**
- [MDN — `prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)

### 25. Content lifecycle & retirement

_Applies to: pages, media libraries, uploads, archived campaigns._

- Schedule content reviews like technical maintenance.
- Delete pages nobody needs — stale content is stored, crawled, and navigated around.
- Clean up orphaned media; deleted pages usually leave their uploads on disk.
- Remove unused templates, components, and dependencies as routine work.
- Redirect retired URLs rather than leaving them to 404.
- Set a retention policy for logs, backups, and generated renditions.

**Documentation**
- [W3C — Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/)

---

## CMS

### 26. Media upload constraints

_Applies to: the media library and editor-facing upload fields._

- Enforce maximum upload size and dimensions at field level — editors will upload camera
  originals otherwise.
- Generate renditions automatically and serve the right one per context.
- Convert to AVIF/WebP server-side, keeping a fallback.
- Reject or resize oversized uploads rather than storing them.
- An image service like [rokka.io](https://rokka.io/) removes this class of problem from the
  editor's hands entirely.

**Documentation**
- [rokka.io](https://rokka.io/)

### 27. Content & block edition constraints

_Applies to: page builders, block editors, rich text fields, repeatable structures._

- Set limits: blocks per page, images per gallery, embeds per page, hero media.
- Constrain rich text to elements the design supports — an unrestricted editor produces markup
  nobody styled.
- Encourage shared blocks and shared assets over per-page duplication.
- Make heavy blocks (video, map, carousel, embed) visibly distinct so their cost is apparent.
- Prefer a small set of good blocks to a library of near-duplicates.

**Documentation**
- [W3C — Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/)

### 28. Editor guidance & helper text

_Applies to: field descriptions and help text inside the CMS._

- Add a line to media fields: use media only where it adds meaning, prefer vectors, keep images
  concise.
- State recommended dimensions next to the field, not in a separate document.
- Explain constraints rather than only enforcing them — editors work around rules they don't
  understand.
- Warn when an upload is far larger than needed and offer the resized version.
- One sentence per field. Long CMS documentation goes unread.

**Documentation**
- [W3C — Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/)

---

## Code & delivery

### 29. HTML semantics & document structure

_Applies to: every template and rendered page._

- Use semantic elements — they cost nothing and bring behaviour and accessibility for free.
- Include `<!DOCTYPE html>`, `<html lang>`, `<meta charset>`, `<title>`, viewport meta.
- One `<h1>` per page, no skipped heading levels.
- Provide description and Open Graph tags, and structured data where it applies.
- Minify HTML in production.
- Keep the DOM shallow — nested wrappers cost parse time, memory, and style recalculation.

**Documentation**
- [MDN — HTML element reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements)

### 30. CSS delivery & authoring

_Applies to: stylesheets, CSS-in-JS output, and the build that produces them._

- Minify in production and remove unused rules — the Coverage tab shows what's actually used.
- Inline critical above-the-fold CSS; load the rest asynchronously.
- Use `content-visibility: auto` on long off-screen sections.
- Use a naming methodology to prevent duplication born of uncertainty.
- Prefer CSS to JavaScript for animation, accordions, toggles, tooltips (block 32).
- Don't load a framework for a handful of utilities.

**Documentation**
- [Chrome DevTools — Coverage tab](https://developer.chrome.com/docs/devtools/coverage)

### 31. JavaScript delivery & dependency choice

_Applies to: application code, bundles, everything in `package.json`._

- Minify in production; load every script with `defer`, `async`, or `type="module"`.
- Split per route; dynamically import heavy components so they load on interaction.
- Enable tree-shaking and verify it works — misconfigured builds bundle whole libraries for one
  function.
- Remove unused code.
- Evaluate each dependency before adding it, transitive dependencies included. A few lines of
  your own often beats a general-purpose package.
- Prefer the platform: `fetch` over an HTTP client, `Intl` over a date library, no jQuery for
  selection and events.

**Documentation**
- [web.dev — Reduce JavaScript payloads with code splitting](https://web.dev/articles/reduce-javascript-payloads-with-code-splitting)

### 32. Native browser features over libraries

_Applies to: any custom component reimplementing something the browser provides._

- `<dialog>` instead of a modal library.
- `<details>`/`<summary>` instead of an accordion component.
- `<datalist>` or native `<select>` instead of a custom dropdown.
- Native date, time, and colour inputs instead of picker libraries.
- Popover API instead of a tooltip library; CSS scroll snap instead of a carousel library.
- Native elements arrive with keyboard, screen reader, and mobile behaviour already correct —
  which is where custom reimplementations usually fail.

**Documentation**
- [MDN — `<dialog>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog)

### 33. Component & pattern reuse

_Applies to: the component library, design system, shared templates._

- Reuse rather than building one-off variants — shared code is downloaded once and cached
  across the site.
- Consolidate near-duplicates. Three slightly different cards means three sets of everything.
- Keep shared styles and scripts in stable long-cached bundles.
- Push decisions into tokens and variables rather than per-component overrides.
- Delete components nothing uses.

**Documentation**
- [MDN — Using CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascading_variables/Using_CSS_custom_properties)

### 34. Caching strategy

_Applies to: server and CDN cache headers, service workers._

- Cache hashed static assets long and immutable — the filename changes on deploy.
- Serve HTML with `no-cache` plus an `ETag` so browsers revalidate instead of re-downloading.
- Cache images and media for a long period.
- Configure server-side caching — page cache, reverse proxy, or static generation.
- Never `Cache-Control: no-store` on HTML; it disables the back/forward cache.

**Documentation**
- [MDN — HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)

### 35. Compression

_Applies to: server and CDN configuration for text responses._

- Enable Brotli for HTML, CSS, JS, JSON, SVG; GZIP as fallback.
- Verify `Content-Encoding` is actually present — compression configured but not applied is a
  common invisible failure.
- Check SVG and JSON are included; they're often missed for not looking like text.
- Don't re-compress images, video, or WOFF2 — CPU for no gain.

**Documentation**
- [MDN — `Content-Encoding`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Encoding)

### 36. Hosting & infrastructure

_Applies to: the provider, server configuration, delivery infrastructure._

- Choose a provider on renewable energy — verify it rather than trusting marketing copy.
- Host in the region where your audience is.
- Use a CDN for static assets.
- Right-size to actual need rather than a peak that never arrives.
- Enforce HTTPS with HTTP/2 or HTTP/3.
- Block bots and malicious traffic — unwanted traffic still costs energy to serve.
- Clean up unused data, old backups, and redundant generated assets on a schedule.

**Documentation**
- [Green Web Foundation — Green Web Check](https://www.thegreenwebfoundation.org/green-web-check/)

---

## Accessibility

Accessible markup is usually lighter markup — native elements replace custom components,
semantics replace wrapper divs. And a page someone can't use is a page load entirely wasted.

These blocks cover what intersects most with weight and delivery. For full conformance, use the
[WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/) filtered to level AA.

### 37. Keyboard navigation

_Applies to: every interactive element._

- Everything interactive must be reachable and operable by keyboard alone.
- Provide "skip to content" as the first focusable element where navigation repeats.
- Keep a clearly visible focus indicator; never remove the outline without replacing it.
- Keep tab order matching visual order; avoid positive `tabindex`.
- Move focus into dialogs and menus on open, return it to the trigger on close, and make
  everything escapable.
- Use `<button>` and `<a>` rather than click handlers on `<div>`.

**Documentation**
- [WebAIM — Keyboard accessibility](https://webaim.org/techniques/keyboard/)

### 38. Screen reader & semantics

_Applies to: page structure, controls, anything conveyed visually._

- Use landmark elements so users can jump between regions.
- Keep headings correct — they're the primary navigation for screen reader users.
- Give every control an accessible name.
- Make link text meaningful alone; "read more" repeated tells a screen reader user nothing.
- Prefer native HTML to ARIA — ARIA changes announcement but adds no behaviour, and incorrect
  ARIA is worse than none.
- Hide decorative content with `aria-hidden="true"`; use live regions sparingly.

**Documentation**
- [W3C WAI — ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)

### 39. Accessibility of deferred content

_Applies to: lazy-loaded content, facades, click-to-load embeds, infinite scroll._

- Facades must be real buttons named for what they load — "Play video: [title]".
- Move focus into loaded content once a facade activates.
- Announce dynamically loaded content via a live region, or move focus to it.
- Keep lazy-loaded content reachable by screen readers and in-page search.
- Communicate loading states in text, not only a spinner.
- Never let lazy loading remove content from the accessibility tree.

**Documentation**
- [MDN — ARIA live regions](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions)

### 40. Colour & contrast (WCAG AA)

_Applies to: the palette, text over images, UI states, both themes._

- At least 4.5:1 for body text, 3:1 for large text.
- At least 3:1 for component boundaries, icons, and focus indicators.
- Verify in every theme — passing in light says nothing about dark.
- Never use colour as the only carrier of meaning.
- Check text over images at its worst point, not its best; a scrim is usually needed.
- Ensure the design still works in forced-colours mode.

**Documentation**
- [WCAG 2.2 — Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

### 41. Forms & error handling

_Applies to: every form. Weight requirements are in block 21._

- Every field needs a visible `<label>` associated via `for`/`id`.
- Placeholders are not labels — they vanish on typing and usually fail contrast.
- Group related fields with `<fieldset>` and `<legend>`.
- Add `autocomplete` to personal data fields.
- Identify errors in text, say how to fix them, and associate each with its field via
  `aria-describedby`.
- Move focus to the first error or an error summary linking to each field.
- Never signal an error by colour alone.
- Avoid time limits; allow extension where unavoidable.

**Documentation**
- [W3C WAI — Forms tutorial](https://www.w3.org/WAI/tutorials/forms/)

---

Further reading: *Sustainable Web Design* by Tom Greenwood (A Book Apart, 2021), and
[sustainablewebdesign.org](https://sustainablewebdesign.org/).