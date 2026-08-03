# Eco-Design Requirements

A set of implementation requirements for building a lower-impact website. It states what
should be done — it is not an audit and makes no claims about any particular project.

## How to use this document

**If you are a developer**, read the blocks that apply to what you are building and ignore
the rest. Each block opens with a scope line telling you when it applies. There is no
expectation that every block is relevant to every project.

**If you work with an AI coding assistant**, add this file to your project's reference
material — put it in `docs/`, or link to it from your `CLAUDE.md` (or equivalent) so the
assistant picks it up. It can then propose implementations that already satisfy the relevant
requirements while you work.

**Everything here is advisory.** These are recommendations, not gates. Project constraints,
deadlines, client requirements, and plain disagreement are all valid reasons to skip an item.
Nothing in this document should block a merge.

Documentation links were accurate when written and are worth re-checking periodically — the
web moves and URLs drift.

---

## Images & graphics

### 1. Raster images / photos

_Applies to: any `<img>`, `<picture>`, CSS `background-image`, or CMS-uploaded photograph._

- Serve AVIF or WebP with a JPEG/PNG fallback via `<picture>` and `<source type="...">`.
- Use `srcset` and `sizes` so each device downloads a width appropriate to its viewport.
- Compress photographs — around 80% quality is usually indistinguishable from the original.
- Resize before upload or on the server; never ship a full-resolution original to be scaled
  down by CSS.
- Add `loading="lazy"` and `decoding="async"` to images below the fold.
- Set `width` and `height` (or `aspect-ratio`) on every image to prevent layout shift.
- Give every meaningful image descriptive `alt` text — not the filename.
- Self-host images rather than pulling them from a third-party domain, unless you are using a
  dedicated image service.
- Consider an image service such as [rokka.io](https://rokka.io/), which handles format
  negotiation, on-the-fly resizing, and compression for you — it satisfies most of the above
  without per-image manual work.

**Documentation**
- [MDN — Responsive images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images) — `srcset`, `sizes`, and `<picture>` explained with worked examples
- [web.dev — Browser-level image lazy loading](https://web.dev/articles/browser-level-image-lazy-loading) — when `loading="lazy"` helps and when it hurts
- [rokka.io](https://rokka.io/) — image service handling format, resizing, and compression

### 2. Hero & above-the-fold images

_Applies to: the largest image visible on first paint — hero banners, article lead images,
product shots above the fold._

- Do not lazy-load the hero. Use `loading="eager"` or omit the attribute entirely.
- Add `fetchpriority="high"` to the LCP image so the browser fetches it early.
- Preload it with `<link rel="preload" as="image">` when it is discovered late (for example
  a CSS background or an image inside a carousel).
- Keep the hero image markedly lighter than the rest — it blocks the perceived load.
- Ask whether the hero needs to be a photograph at all: a CSS gradient, an SVG, or bold
  typography costs a fraction and often reads better.
- Never lazy-load and preload the same image — the two cancel each other out.

**Documentation**
- [web.dev — Optimize Largest Contentful Paint](https://web.dev/articles/optimize-lcp) — how the LCP image is discovered and prioritised
- [MDN — `fetchPriority`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/fetchPriority) — signalling resource priority to the browser
- [rokka.io](https://rokka.io/) — generating correctly sized hero renditions per breakpoint

### 3. Decorative & background images

_Applies to: images that carry no information — textures, dividers, ambient photography,
CSS `background-image` used for styling._

- Mark them as decorative: `alt=""` on `<img>`, or `aria-hidden="true"` where appropriate, so
  screen readers skip them.
- Replace them with CSS where you can — gradients, `box-shadow`, borders, and blend modes are
  free by comparison.
- Blur or crop deliberately: softened and tightly cropped images compress much better, and
  whitespace often makes a smaller image feel more deliberate, not less.
- Consider skipping decorative imagery entirely on small viewports via `media` attributes in
  `<picture>` or a CSS media query.
- Question each one before optimising it — the cheapest decorative image is the one you don't
  ship.

**Documentation**
- [MDN — Images in HTML: decorative images](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/HTML_images) — `alt=""` conventions
- [MDN — CSS gradients](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_images/Using_CSS_gradients) — replacing raster backgrounds with generated ones

### 4. Icons & illustrations

_Applies to: any icon set, pictogram, logo, or flat illustration._

- Use SVG rather than raster formats or icon fonts.
- Inline small, frequently reused icons; use a sprite or `<use>` reference for larger sets.
- Add `aria-hidden="true"` to icons that sit next to a visible text label — otherwise screen
  readers announce them twice.
- Give standalone icon buttons an accessible name via `aria-label` or visually hidden text.
- Prefer flat, few-colour illustrations over photographic ones — they vectorise cleanly and
  stay crisp at any size.

**Documentation**
- [MDN — SVG element reference](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element) — inline SVG, `<use>`, and sprite patterns
- [CSS-Tricks — Accessible SVG icons](https://css-tricks.com/accessible-svg-icons/) — labelling patterns for icons and icon buttons

### 5. SVG assets

_Applies to: every `.svg` file in the project, whether inline, referenced, or uploaded._

- Run SVGs through [SVGO](https://www.npmjs.com/package/svgo) to strip editor metadata, hidden
  layers, and unused definitions — exported files are typically far larger than they need to be.
- Simplify paths in the design tool before export; fewer nodes means a smaller file.
- Ensure SVGs are served with Brotli or GZIP — they are text and compress very well.
- Set `viewBox` and let the SVG scale, rather than exporting one file per size.
- Do not embed raster images inside an SVG — that defeats the purpose.

**Documentation**
- [SVGO](https://www.npmjs.com/package/svgo) — the standard SVG optimiser, available as CLI and build plugin
- [MDN — SVG `viewBox`](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/viewBox) — making a single asset scale to every size

---

## Video, audio & motion

### 6. Self-hosted video

_Applies to: any `<video>` element served from your own infrastructure._

- Never autoplay. Use `preload="none"` with a `poster` image so nothing downloads until the
  user presses play.
- Always expose native `controls` — play, pause, volume, fullscreen.
- Provide WebM as the primary source with an MP4 fallback via multiple `<source>` elements.
- Compress hard and keep clips short; re-encode rather than uploading a camera original.
- Provide captions with `<track kind="captions">` and a WebVTT file.
- Provide a text transcript for informational content — it is cheaper to read than to watch,
  and it is indexable.
- Wrap video in `<figure>` with a `<figcaption>` where it needs a caption.
- For explanatory content, consider a lightweight code-driven animation instead — it is often
  a fraction of the weight with better accessibility.

**Documentation**
- [MDN — `<video>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/video) — attributes, sources, and fallback behaviour
- [MDN — `<track>` and WebVTT](https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API) — adding captions and subtitles
- [FFmpeg](https://ffmpeg.org/) — re-encoding and compressing video for the web

### 7. YouTube / Vimeo embeds

_Applies to: any `<iframe>` pointing at youtube.com, youtube-nocookie.com, vimeo.com, or a
similar video host._

- Put the embed behind a facade: a self-hosted poster image and a play button that swap in
  the real iframe only when clicked. The embed then costs nothing until someone wants it.
- Use `youtube-nocookie.com` rather than `youtube.com` so no tracking cookie is set before
  playback.
- Add `loading="lazy"` to the iframe, and restrict `allow` to the permissions actually needed.
- Make the facade accessible: it must be a real button, reachable by keyboard, with a name
  that says what it plays.
- Move focus into the player once the iframe loads, so keyboard users are not stranded.
- Load the embed only after cookie consent where the vendor sets tracking cookies.

**Documentation**
- [Chrome — Third-party facades](https://developer.chrome.com/docs/lighthouse/performance/third-party-facades) — the pattern, its trade-offs, and ready-made implementations
- [lite-youtube-embed](https://github.com/paulirish/lite-youtube-embed) — a drop-in facade component for YouTube

### 8. Audio content

_Applies to: any `<audio>` element, podcast player, or embedded audio widget._

- Set `preload="none"` and never autoplay.
- Expose native `controls`.
- Provide a transcript — for most audio content, it is the primary accessible alternative.
- Prefer a compressed, speech-appropriate bitrate over a music-grade encode for spoken word.
- Where audio is hosted by a platform, apply the facade pattern from block 7.

**Documentation**
- [MDN — `<audio>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/audio) — attributes and accessible usage
- [W3C WAI — Audio description and transcripts](https://www.w3.org/WAI/media/av/transcripts/) — what a usable transcript contains

### 9. Animated GIFs

_Applies to: any `.gif` used for motion — reaction clips, screen recordings, loading
indicators, product demos._

- Do not use animated GIF. Every frame is stored as a full image, which makes it the least
  efficient moving format available.
- Replace with a muted, looping, `playsinline` `<video>` (WebM with MP4 fallback), which is
  usually a small fraction of the weight.
- Use animated WebP where a single image file is genuinely required.
- Use a CSS or SVG animation for loading indicators and simple UI motion.
- Screen recordings compress far better as video than as GIF — re-encode rather than export.

**Documentation**
- [web.dev — Replace animated GIFs with video](https://web.dev/articles/replace-gifs-with-videos) — conversion steps and the size difference
- [MDN — WebP image format](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Image_types#webp) — animation support and browser coverage

### 10. Animation & motion

_Applies to: CSS transitions and keyframes, JavaScript animation, Lottie, and any looping
motion in the interface._

- Honour `prefers-reduced-motion: reduce` — disable or substantially reduce non-essential
  motion when the user has opted out.
- Never let reduced motion remove information; replace the animation, don't delete the content.
- Animate `transform` and `opacity` only. Animating layout properties forces reflow on every
  frame and burns CPU.
- Give continuous or looping animations a visible pause control.
- Keep the number of simultaneous animations low — several running at once is what drains a
  battery, not any single one.
- Ask what each animation does for the user. Motion that guides, confirms, or explains earns
  its cost; motion that decorates usually does not.
- Prefer CSS to JavaScript for animation — the compositor can often run it off the main thread.

**Documentation**
- [MDN — `prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion) — detecting and respecting the preference
- [web.dev — Animations guide](https://web.dev/articles/animations-guide) — which properties are cheap to animate and why
- [WCAG 2.2 — Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) — the accessibility requirement behind reduced motion

### 11. Scroll effects

_Applies to: parallax, scroll-triggered reveals, sticky transformations, scroll-linked
animation, and infinite scroll._

- Do not hijack scrolling. Overriding native scroll behaviour breaks keyboard use, assistive
  technology, and user expectation.
- Use CSS scroll-driven animations or `IntersectionObserver` rather than a `scroll` event
  handler that runs work on every frame.
- Disable scroll-triggered motion under `prefers-reduced-motion`.
- Prefer paginated loading with an explicit "load more" control over infinite scroll. Infinite
  scroll keeps fetching content the user may never look at, and makes the footer unreachable.
- Where infinite scroll is required, announce newly loaded content to assistive technology and
  keep the URL in sync so a position can be shared or restored.
- Ask whether long scrolling pages could be shorter: content nobody reaches still costs
  bandwidth for everyone who loads the page.

**Documentation**
- [MDN — `IntersectionObserver`](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API) — efficient viewport detection without scroll handlers
- [MDN — CSS scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations) — scroll-linked motion handled by the browser
- [Smashing Magazine — Infinite scroll UX](https://www.smashingmagazine.com/2022/03/designing-better-infinite-scroll/) — when pagination is the better pattern

---

## Typography

### 12. Custom web fonts

_Applies to: every `@font-face` declaration and any font loaded from a hosted font service._

- Self-host font files. A hosted font service adds a third-party connection and takes
  optimisation out of your hands.
- Use WOFF2 only. Every browser you need to support handles it, and it is the most compressed
  format available.
- Subset fonts to the character sets you actually use — Latin-only subsets are dramatically
  smaller than full multi-script files.
- Load at most two weights. If you need more variation, use one variable font instead of many
  static files.
- Declare a system font fallback stack in `font-family` so text is readable before the custom
  font arrives.
- Use `font-display: swap` so text renders immediately in the fallback.
- Preload the fonts used in above-the-fold text with `<link rel="preload" as="font" crossorigin>`.
- Consider system fonts for body copy and reserve the custom face for headings and brand
  elements — this captures most of the design value at a fraction of the cost.

**Documentation**
- [web.dev — Best practices for fonts](https://web.dev/articles/font-best-practices) — subsetting, preloading, `font-display`, and fallback matching
- [MDN — `@font-face`](https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face) — declaration syntax and descriptors
- [glyphhanger](https://github.com/zachleat/glyphhanger) — subsetting fonts to the characters a site actually uses

### 13. Icon fonts

_Applies to: FontAwesome, Material Icons, custom icon fonts, and any glyph-based icon system._

- Do not use icon fonts. Use SVG instead — see block 4.
- An icon font downloads every glyph in the file even when you use three of them, and it
  renders as text to assistive technology, which announces meaningless characters.
- Where an icon font is already in place and cannot be removed, subset it to the glyphs in use
  and mark every icon element `aria-hidden="true"`.

**Documentation**
- [CSS-Tricks — Icon fonts vs. SVG](https://css-tricks.com/icon-fonts-vs-svg/) — the accessibility and weight comparison
- [SVGO](https://www.npmjs.com/package/svgo) — optimising the SVG icons you replace them with

---

## Third-party

### 14. Third-party embeds & facades

_Applies to: any `<iframe>`, script tag, or widget served from a domain you do not control._

- Put every non-essential third-party embed behind a facade — a self-hosted static preview and
  a control that loads the real thing on click.
- Self-host what you can. Fonts, icons, small libraries, and static assets rarely need to come
  from a vendor domain.
- Add `loading="lazy"` to third-party iframes.
- Apply a restrictive `sandbox` attribute and grant only the `allow` permissions the embed
  actually needs.
- Load scripts with `defer` or `async` so a third party cannot block your rendering.
- Audit periodically and remove embeds nobody uses — they accumulate quietly across a project's
  life.
- Give users a way to turn off non-essential third-party services.

**Documentation**
- [Chrome — Third-party facades](https://developer.chrome.com/docs/lighthouse/performance/third-party-facades) — the pattern and existing implementations
- [MDN — `<iframe>` sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe#sandbox) — restricting embed permissions
- [web.dev — Optimize third-party JavaScript](https://web.dev/articles/optimizing-content-efficiency-loading-third-party-javascript) — loading strategies and their trade-offs

### 15. Maps

_Applies to: Google Maps, Mapbox, OpenStreetMap, and any interactive map embed._

- Replace the interactive map with a static map image plus a link or button that loads the
  interactive version on demand. Most visitors only need to see where something is.
- Where a static image is not viable, apply the facade pattern from block 14.
- Provide the address as selectable text alongside the map — it is more useful than the map for
  many people, and it works without any embed loading at all.
- Link out to the user's own map application rather than embedding a full interactive canvas
  for a single pin.
- Load map tiles only after consent where the provider sets tracking cookies.

**Documentation**
- [Chrome — Third-party facades](https://developer.chrome.com/docs/lighthouse/performance/third-party-facades) — includes a map facade example
- [OpenStreetMap static maps](https://wiki.openstreetmap.org/wiki/Static_map_images) — generating a static map image

### 16. Chat widgets & social feeds

_Applies to: live chat, chatbots, Instagram/X/LinkedIn feed embeds, review widgets, and social
share buttons._

- Question whether the widget belongs at all. Chat widgets and social feeds are among the
  heaviest third parties on a typical site and are often used by a small minority of visitors.
- Load chat on interaction only — render a lightweight button that fetches the widget when
  clicked.
- Replace social feed embeds with server-fetched, cached, self-hosted content, or with a plain
  link to the profile.
- Use plain links for sharing rather than vendor share-button scripts — a link costs nothing
  and does not track your visitors.
- Defer everything in this category until after the page is interactive.

**Documentation**
- [web.dev — Optimize third-party JavaScript](https://web.dev/articles/optimizing-content-efficiency-loading-third-party-javascript) — deferring and gating vendor scripts
- [Simple sharing buttons](https://sharingbuttons.io/) — share links with no scripts and no tracking

### 17. Analytics & tag managers

_Applies to: Google Analytics, tag managers, heatmaps, session recording, A/B testing, and any
measurement script._

- Prefer a lightweight, privacy-respecting analytics tool — Plausible, Fathom, Umami, or a
  self-hosted Matomo — over a full tag manager.
- Load nothing before consent where the tool sets cookies or transmits personal data.
- Remove tracking you do not actively use. Tag managers accumulate tags that outlive the
  campaigns that added them.
- Keep tracking limited to what answers a question someone actually asks.
- Session recording and heatmaps are heavy and privacy-invasive — run them for a defined period
  and then remove them, rather than leaving them on permanently.
- Give users a way to stop tracking after they have accepted it.

**Documentation**
- [Plausible](https://plausible.io/) / [Umami](https://umami.is/) — lightweight, cookie-free analytics alternatives
- [Matomo](https://matomo.org/) — self-hostable analytics with full data ownership

### 18. Hosted font & asset services

_Applies to: Google Fonts, Adobe Fonts, jQuery/CDN script tags, icon CDNs, and any static asset
loaded from a vendor domain._

- Self-host fonts as subsetted WOFF2 files rather than loading them from a font service.
- Self-host libraries rather than pulling them from a public CDN. Cross-site CDN caching no
  longer works — browsers partition their caches per site — so the shared-cache argument for
  CDNs no longer holds.
- Bundle small libraries into your own build output instead of adding a separate request.
- Each vendor domain costs a DNS lookup, a TCP connection, and a TLS handshake before a single
  byte of content arrives.
- Self-hosting also removes a third-party dependency, a privacy exposure, and a point of
  failure.

**Documentation**
- [web.dev — Best practices for fonts](https://web.dev/articles/font-best-practices) — self-hosting and subsetting
- [Chrome — HTTP cache partitioning](https://developer.chrome.com/blog/http-cache-partitioning) — why shared CDN caching no longer applies

### 19. Cookie consent & consent-gated loading

_Applies to: the cookie banner and everything whose loading depends on it._

- Set no non-essential cookie and fire no third-party request before consent is given.
- Make refusing as easy as accepting — same prominence, same number of clicks, no dark
  patterns.
- Make the banner fully keyboard-operable and screen-reader accessible, with focus managed
  correctly on open and close.
- Let users review, change, and revoke their choice at any time from a persistent link.
- Keep the banner itself lightweight — a consent tool that ships a large script to ask about
  tracking is a poor trade.
- Wire consent to actual loading, not just to a flag: on refusal the vendor script must never
  be requested.

**Documentation**
- [W3C WAI — Modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) — focus management and keyboard behaviour for consent overlays
- [EDPB guidelines on deceptive design](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en) — what makes a consent flow manipulative

---

## Content & interaction patterns

### 20. Carousels, sliders & galleries

_Applies to: any multi-slide component — hero carousels, product galleries, logo strips,
testimonial sliders._

- Load the first slide only. Lazy-load the rest on interaction or as they approach the viewport.
- Never download every image in a gallery upfront — most visitors see the first slide and
  nothing else.
- Provide keyboard-operable previous/next controls and make the slide region navigable.
- Give auto-rotating carousels a pause control, and stop rotation under
  `prefers-reduced-motion`.
- Reduce the number of slides. A carousel is often a way of avoiding a content decision, and
  each additional slide costs bandwidth for content few people reach.
- Consider a grid or a single strong image instead — both are lighter and generally perform
  better.

**Documentation**
- [W3C WAI — Carousel pattern](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) — keyboard, labelling, and auto-rotation requirements
- [web.dev — Browser-level image lazy loading](https://web.dev/articles/browser-level-image-lazy-loading) — deferring off-screen slide images

### 21. Forms

_Applies to: any form — contact, search, checkout, filters, newsletter signup. See block 41 for
the accessibility requirements._

- Ask for the minimum. Every field is data to transmit, validate, store, and eventually delete.
- Use native input types (`email`, `tel`, `date`, `number`, `url`) rather than JavaScript
  widgets — they are free, accessible, and give mobile users the right keyboard.
- Validate with native constraint validation (`required`, `pattern`, `type`) before reaching for
  a validation library.
- Avoid heavy form libraries for simple forms; a plain `<form>` with a server round-trip is
  often all that is needed.
- Compress and limit file uploads, and state the accepted formats and size in the interface.
- Use `<datalist>` for suggestion lists instead of a custom autocomplete component.
- Do not load a CAPTCHA on every page — load it on the form that needs it, and prefer a
  lightweight or privacy-respecting option.

**Documentation**
- [MDN — Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) — native validation before libraries
- [MDN — `<input>` types](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input) — the full set of native inputs

### 22. Search & navigation

_Applies to: site navigation, menus, search, breadcrumbs, and internal linking._

- Make navigation clear enough that users find things on the first attempt. Every failed
  attempt is an extra page load.
- Surface subcategories directly in the menu rather than routing people through decorative
  landing pages to reach what they want.
- Provide a prominent search box on content-heavy sites — it is often the shortest path.
- Remove gateway and splash pages that exist only to be clicked through.
- Watch for journeys where users repeatedly return to the homepage: that is a wayfinding
  problem, and each round-trip is a wasted load.
- Keep search results server-rendered and paginated rather than shipping a client-side index of
  the whole site.
- Make link text descriptive so users can judge a destination before loading it.

**Documentation**
- [Nielsen Norman Group — Information scent](https://www.nngroup.com/articles/information-scent/) — why clear labelling reduces wasted navigation
- [MDN — `<nav>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/nav) — semantics for navigation regions

### 23. Live content & feed refresh

_Applies to: polling, auto-refresh, WebSockets, live tickers, notification badges, and any
timer-driven request._

- Fetch on user action rather than on a timer wherever the content allows it.
- Where polling is genuinely needed, use the longest interval the content tolerates.
- Stop polling when the tab is hidden — check `document.visibilityState` and resume on focus.
- Prefer a server-push mechanism (WebSocket, SSE) over frequent short-interval polling when
  updates are genuinely real-time.
- Do not use `<meta http-equiv="refresh">` to reload a page on a timer.
- Ask how fresh the data really needs to be. A dashboard refreshed every few seconds usually
  serves a habit rather than a need.

**Documentation**
- [MDN — Page Visibility API](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API) — pausing work in hidden tabs
- [MDN — Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) — push updates without polling

### 24. Dark mode & colour scheme

_Applies to: theming, colour palettes, and any light/dark implementation._

- Respect `prefers-color-scheme` and follow the user's system setting by default.
- Design both themes properly — a dark theme is not a light one with inverted values.
- Verify contrast holds in both themes; dark backgrounds frequently fail where light ones passed.
- Offer a manual toggle in addition to the system preference if you want to give users explicit
  control.
- Use CSS custom properties for colour so a theme is a variable swap, not a duplicated stylesheet.
- Set `color-scheme` so native form controls and scrollbars follow the theme.
- Treat the OLED energy saving of dark themes as a tiebreaker rather than a justification — it
  is real but small next to imagery and scripts.

**Documentation**
- [MDN — `prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme) — detecting the user's preference
- [MDN — `color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme) — making native UI follow the theme
- [web.dev — prefers-color-scheme](https://web.dev/articles/prefers-color-scheme) — implementation patterns and common pitfalls

### 25. Content lifecycle & retirement

_Applies to: the content the site accumulates over its life — pages, media libraries, uploads,
archived campaigns._

- Schedule content reviews the same way you schedule technical maintenance.
- Delete pages that no longer serve anyone. Stale content consumes storage, gets crawled, and
  makes the site harder to navigate.
- Clean up orphaned media — uploads whose pages were deleted usually remain on disk.
- Remove unused templates, components, and dependencies as part of routine work.
- Redirect retired URLs rather than leaving them to 404, so links and crawlers do not waste
  requests.
- Set a retention policy for logs, backups, and generated renditions.

**Documentation**
- [W3C — Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) — see the guidelines on data and content management
- [Google Search Central — Redirects](https://developers.google.com/search/docs/crawling-indexing/301-redirects) — retiring URLs without breaking links

---

## CMS

### 26. Media upload constraints

_Applies to: the CMS media library and any editor-facing upload field._

- Enforce a maximum upload size and maximum dimensions at the field level. Editors will
  otherwise upload camera originals.
- Generate renditions automatically on upload (thumbnail, medium, large) and serve the
  appropriate one per context — never rely on the editor to pick.
- Convert to AVIF or WebP server-side, with a fallback format retained.
- Reject or resize oversized uploads rather than accepting and storing them.
- Consider an image service such as [rokka.io](https://rokka.io/), which generates renditions
  and negotiates formats on the fly — it removes the whole class of problem from the editor's
  hands.
- State the recommended aspect ratio for each image field in the interface.

**Documentation**
- [rokka.io](https://rokka.io/) — upload once, serve every rendition and format automatically
- [MDN — Responsive images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images) — what the generated renditions need to support

### 27. Content & block edition constraints

_Applies to: page builders, block editors, rich text fields, and repeatable content structures._

- Set limits that prevent page bloat: maximum number of blocks per page, maximum images per
  gallery, maximum embeds per page, maximum hero media.
- Constrain rich text to the elements the design supports — an unrestricted editor produces
  markup nobody styled.
- Encourage reuse of shared blocks and shared assets rather than duplicating content per page.
- Make heavy blocks (video, map, carousel, embed) visibly distinct in the editor so their cost
  is apparent when choosing one.
- Prefer a small set of well-designed blocks over a large library of near-duplicates.

**Documentation**
- [W3C — Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) — guidance on content authoring constraints
- [MDN — Semantic HTML](https://developer.mozilla.org/en-US/docs/Glossary/Semantics#semantics_in_html) — what rich text output should be limited to

### 28. Editor guidance & helper text

_Applies to: field descriptions, help text, and editor documentation inside the CMS._

- Add short helper text to media fields: use media only where it adds meaning, prefer vector
  graphics and icons, keep images concise.
- State the recommended dimensions and aspect ratio next to the field, not in a separate
  document.
- Explain the constraints rather than only enforcing them — editors work around rules they do
  not understand.
- Warn when an upload is much larger than needed, and offer the resized version.
- Keep guidance to a sentence per field. Long documentation in a CMS goes unread.

**Documentation**
- [W3C — Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) — content contributor guidance
- [Nielsen Norman Group — Help and documentation](https://www.nngroup.com/articles/help-and-documentation/) — writing help text people actually read

---

## Code & delivery

### 29. HTML semantics & document structure

_Applies to: every template and rendered page._

- Use semantic elements — `<nav>`, `<main>`, `<article>`, `<section>`, `<header>`, `<footer>`,
  `<button>`, `<a>`. They cost nothing and give behaviour and accessibility for free.
- Include the required document elements: `<!DOCTYPE html>`, `<html lang>`, `<meta charset>`,
  `<title>`, and the viewport meta tag.
- Keep the heading hierarchy correct — one `<h1>` per page, no skipped levels.
- Provide description and Open Graph meta tags so shared links render without a fetch of the
  whole page.
- Add structured data where it applies, so search results answer questions without a visit.
- Minify HTML in production.
- Keep the DOM shallow. Deeply nested wrapper markup costs parse time, memory, and style
  recalculation on every interaction.

**Documentation**
- [MDN — HTML element reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements) — the semantic elements and their meanings
- [MDN — Structured data](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Microdata) — marking up content for search results

### 30. CSS delivery & authoring

_Applies to: stylesheets, CSS-in-JS output, and the build pipeline that produces them._

- Minify CSS in production.
- Remove unused CSS. Frameworks and long-lived projects accumulate rules nothing matches —
  the Chrome Coverage tab shows what is actually used.
- Inline critical above-the-fold CSS and load the rest asynchronously.
- Use `content-visibility: auto` on long off-screen sections so the browser skips rendering
  work until they are needed.
- Use a naming methodology (BEM or similar) to prevent the duplication that comes from
  uncertainty about what a class already does.
- Prefer CSS to JavaScript for animation, accordions, toggles, and tooltips — see block 32.
- Avoid loading a full framework for a handful of utilities.

**Documentation**
- [web.dev — `content-visibility`](https://web.dev/articles/content-visibility) — skipping rendering for off-screen content
- [Chrome DevTools — Coverage tab](https://developer.chrome.com/docs/devtools/coverage) — finding unused CSS and JavaScript
- [MDN — CSS performance optimization](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Performance/CSS) — delivery and authoring practices

### 31. JavaScript delivery & dependency choice

_Applies to: application code, bundles, and every dependency in `package.json`._

- Minify JavaScript in production.
- Load every script with `defer`, `async`, or `type="module"` — no render-blocking scripts.
- Split code per route so a page loads only what it needs.
- Dynamically import heavy components so they load on interaction rather than on page load.
- Enable tree-shaking and verify it works — a misconfigured build often bundles whole libraries
  for one imported function.
- Remove unused JavaScript; the Coverage tab shows what never executes.
- Evaluate each dependency before adding it: check its transitive dependencies, and prefer a
  small focused package or a few lines of your own code over a large general one.
- Prefer the platform: `fetch` over an HTTP client library, `Intl` over a date-formatting
  library, and no jQuery for selection and events.

**Documentation**
- [web.dev — Reduce JavaScript payloads with code splitting](https://web.dev/articles/reduce-javascript-payloads-with-code-splitting) — route and component splitting
- [Chrome DevTools — Coverage tab](https://developer.chrome.com/docs/devtools/coverage) — identifying unused code
- [Bundlephobia](https://bundlephobia.com/) — the real cost of a dependency before you add it

### 32. Native browser features over libraries

_Applies to: any custom component that reimplements something the browser already provides._

- Use `<dialog>` instead of a modal library.
- Use `<details>` and `<summary>` instead of an accordion component.
- Use `<datalist>` or native `<select>` instead of a custom dropdown.
- Use the native date, time, and colour inputs instead of picker libraries.
- Use the Popover API instead of a tooltip or popover library.
- Use CSS scroll snap instead of a carousel library where the interaction is simple.
- Native elements arrive with keyboard support, screen reader support, and mobile behaviour
  already correct — which is usually where custom reimplementations fail.

**Documentation**
- [MDN — `<dialog>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog) — native modal dialogs
- [MDN — Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API) — native popovers and tooltips
- [MDN — CSS scroll snap](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll_snap) — carousel behaviour without JavaScript

### 33. Component & pattern reuse

_Applies to: the component library, design system, and shared templates._

- Reuse existing components rather than building one-off variants. Shared code is downloaded
  once and cached across the whole site.
- Consolidate near-duplicate components — three slightly different card components mean three
  sets of markup, styles, and behaviour to download and maintain.
- Keep shared styles and scripts in stable, long-cached bundles so navigating between pages
  reuses what is already cached.
- Push design-system decisions into tokens and variables rather than per-component overrides.
- Delete components nothing uses.

**Documentation**
- [MDN — CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascading_variables/Using_CSS_custom_properties) — sharing values across components
- [web.dev — HTTP caching](https://web.dev/articles/http-cache) — how shared bundles benefit from long-lived caching

### 34. Caching strategy

_Applies to: server and CDN cache headers, and any service worker._

- Give hashed static assets (CSS, JS, fonts) a long-lived immutable cache policy — they can be
  cached effectively forever because the filename changes on every deploy.
- Serve HTML with `no-cache` plus an `ETag` so browsers can revalidate cheaply instead of
  re-downloading.
- Cache images and other media for a long period.
- Configure server-side caching — a page cache, a reverse proxy, or static site generation —
  so repeated requests do not re-render identical pages.
- Do not set `Cache-Control: no-store` on HTML; it disables the back/forward cache and makes
  every back navigation a full reload.
- Consider a service worker for offline access to key pages, if the maintenance cost is
  justified.

**Documentation**
- [MDN — HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching) — headers, revalidation, and cache lifetimes
- [web.dev — bfcache](https://web.dev/articles/bfcache) — what breaks instant back/forward navigation

### 35. Compression

_Applies to: server and CDN configuration for text-based responses._

- Enable Brotli for text assets — HTML, CSS, JavaScript, JSON, SVG.
- Configure GZIP as a fallback for clients that do not accept Brotli.
- Verify `Content-Encoding` is actually present on responses; compression configured but not
  applied is a common and invisible failure.
- Confirm SVG and JSON are included — they are frequently missed because they are not obviously
  "text".
- Do not re-compress already-compressed formats (images, video, WOFF2); it wastes CPU for no
  gain.
- Compare transferred size against resource size in DevTools to confirm compression is working.

**Documentation**
- [MDN — `Content-Encoding`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Encoding) — negotiating and verifying compression
- [web.dev — Reduce network payloads using text compression](https://web.dev/articles/reduce-network-payloads-using-text-compression) — enabling and checking Brotli and GZIP

### 36. Hosting & infrastructure

_Applies to: the hosting provider, server configuration, and delivery infrastructure._

- Choose a provider running on renewable energy — verify it with the Green Web Foundation
  check rather than taking marketing copy at face value.
- Prefer providers that publish sustainability metrics and hold verifiable certifications.
- Host in the region where your audience is. Data travelling further costs more energy and
  more latency.
- Use a CDN for static assets so they are served close to the user.
- Right-size the infrastructure to actual need rather than provisioning for a peak that never
  arrives.
- Enforce HTTPS with HTTP/2 or HTTP/3.
- Keep automated deployment in place so infrastructure changes are cheap to make and reverse.
- Block bots and malicious traffic — traffic you did not want still consumes energy to serve.
- Clean up unused data, old backups, and redundant generated assets on a schedule.

**Documentation**
- [Green Web Foundation — Green Web Check](https://www.thegreenwebfoundation.org/green-web-check/) — verifying whether a host runs on renewable energy
- [W3C — Web Sustainability Guidelines](https://w3c.github.io/sustainableweb-wsg/) — the hosting and infrastructure section
- [MDN — HTTP/2 and HTTP/3](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Evolution_of_HTTP) — protocol differences and what they change

---

## Accessibility

Accessibility belongs in an eco-design document for two reasons. Accessible markup is usually
lighter markup — native elements replace custom components, semantic structure replaces wrapper
divs, and text alternatives replace images of text. And a page someone cannot use is a page load
entirely wasted, along with everything it took to serve it.

The blocks below cover the requirements that most often intersect with weight and delivery
decisions. They are not a complete WCAG conformance checklist — for the full set, use the
[WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/) filtered to level AA.

### 37. Keyboard navigation

_Applies to: every interactive element — links, buttons, forms, menus, dialogs, carousels,
custom widgets._

- Make everything interactive reachable and operable by keyboard alone.
- Provide a "skip to content" link as the first focusable element on pages with repeated
  navigation.
- Keep a clearly visible focus indicator. Never remove the outline without replacing it with
  something at least as visible.
- Keep the tab order matching the visual order; avoid positive `tabindex` values.
- Move focus into dialogs and menus when they open, trap it while they are open, and return it
  to the trigger on close.
- Ensure nothing traps focus permanently — every component must be escapable.
- Use `<button>` and `<a>` for actions and navigation rather than click handlers on `<div>`,
  which get keyboard support for free.

**Documentation**
- [MDN — Keyboard-navigable JavaScript widgets](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Keyboard-navigable_JavaScript_widgets) — focus and key handling for custom components
- [W3C WAI — ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/) — expected keyboard behaviour per pattern
- [WebAIM — Keyboard accessibility](https://webaim.org/techniques/keyboard/) — testing without a mouse

### 38. Screen reader & semantics

_Applies to: page structure, controls, and anything conveyed visually._

- Use landmark elements (`<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`) so users can jump
  between regions.
- Keep a correct heading hierarchy — headings are the primary navigation mechanism for screen
  reader users.
- Give every control an accessible name: visible text, `aria-label`, or a properly associated
  `<label>`.
- Make link text meaningful on its own; "read more" repeated across a page tells a screen reader
  user nothing.
- Prefer native HTML to ARIA. ARIA changes how an element is announced but adds no behaviour —
  incorrect ARIA is worse than none.
- Use live regions sparingly and only for genuinely important updates.
- Hide purely decorative content from assistive technology with `aria-hidden="true"`.

**Documentation**
- [MDN — ARIA guides](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA) — roles, states, and when not to use them
- [W3C WAI — ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) — correct patterns for common components
- [WebAIM — Screen reader testing](https://webaim.org/articles/screenreader_testing/) — verifying with actual assistive technology

### 39. Accessibility of deferred content

_Applies to: lazy-loaded content, facades, click-to-load embeds, infinite scroll, and
progressively enhanced components._

- Facades must be real buttons with names that say what they load — "Play video: [title]",
  "Load map of [location]".
- Move focus into the loaded content once a facade activates, so keyboard users are not left
  behind.
- Announce dynamically loaded content through a live region, or move focus to it.
- Keep lazy-loaded images and content reachable by screen readers and by in-page search.
- Communicate loading states in text, not only through a spinner.
- Ensure content is still reachable when JavaScript fails — at minimum, provide a link to the
  underlying resource.
- Never let lazy loading remove content from the accessibility tree entirely.

**Documentation**
- [MDN — ARIA live regions](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions) — announcing dynamic content
- [W3C WAI — Modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) — focus handling when content loads into view

### 40. Colour & contrast (WCAG AA)

_Applies to: the colour palette, text over images, UI states, and both light and dark themes._

- Meet a contrast ratio of at least 4.5:1 for body text and 3:1 for large text.
- Meet at least 3:1 for interactive component boundaries, icons, and focus indicators.
- Verify contrast in every theme. A palette that passes in light mode frequently fails in dark.
- Never use colour as the only way of conveying information — pair it with text, an icon, or a
  pattern.
- Check text placed over images and gradients at their worst point, not their best. An overlay
  or scrim is usually needed.
- Verify focus indicators against every background they can appear on.
- Ensure the design still works with a forced-colours or high-contrast mode active.

**Documentation**
- [WCAG 2.2 — Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — the AA requirement and how to measure it
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) — checking pairs quickly
- [MDN — WCAG colour and contrast](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Understanding_WCAG/Perceivable/Color_contrast) — practical guidance

### 41. Forms & error handling

_Applies to: every form. See block 21 for the weight and payload requirements._

- Give every field a `<label>` that is visible and programmatically associated via `for` and
  `id`.
- Do not use placeholder text as a label — it disappears on typing and generally fails contrast.
- Group related fields with `<fieldset>` and `<legend>`, particularly radio groups and
  checkboxes.
- Add `autocomplete` attributes to fields collecting personal data so browsers can fill them.
- Identify errors in text, describe how to fix them, and associate each message with its field
  via `aria-describedby`.
- Move focus to the first error, or to an error summary listing every problem with links to the
  fields.
- Never rely on colour alone to indicate an error state.
- Avoid time limits; where one is unavoidable, allow it to be extended.
- Keep required-field marking explicit in text, not only with an asterisk.

**Documentation**
- [W3C WAI — Forms tutorial](https://www.w3.org/WAI/tutorials/forms/) — labels, grouping, validation, and error messages
- [MDN — `autocomplete` attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/autocomplete) — the full list of field values
- [WCAG 2.2 — Error Identification](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html) — what an accessible error message contains

---

## Design principles

The blocks above are technical requirements. The principles below are judgment calls — they
shape decisions made before any of the requirements become relevant, and they are usually where
the largest savings are found.

**Justify every element.** The default should be absence, not presence. Rather than asking
whether something would be nice to add, ask whether the page can do its job without it — and
when the answer is unclear, leave it out. Every image, block, page, and script has to earn its
place. Minimal does not mean bare; it means nothing is present that is not pulling its weight.

**Simplify the journey, not just the page.** Total data moved is page weight multiplied by
visitors multiplied by pages per visit. Shortening the path to what users actually want attacks
the last factor directly, and it scales across every visitor who takes that path. Remove gateway
pages, surface destinations in the navigation, and watch for journeys where people bounce back to
the homepage to reorient — that is a wayfinding problem costing a page load every time.

**Make imagery lightweight.** Images are the largest contributor on most sites, so this is the
highest-leverage decision available. Question each image before optimising it: stock photography
and decorative filler rarely add value that text and space could not deliver more cheaply. Reach
for vectors, gradients, and CSS where they can replace raster imagery entirely. Crop tighter,
and remember that generous whitespace often makes a smaller image feel more deliberate.

**Weigh the cost of colour.** More colour variation means larger image files, so monochrome and
duotone imagery is consistently lighter across the whole network. On OLED screens each pixel is
its own light source, so darker palettes draw less power — real, but modest next to imagery.
Treat it as a tiebreaker between otherwise equal options, not as a mandate.

**Be mindful with motion.** Motion can sharpen an experience or drain a battery, and the
difference is whether it does something for the user. Video in particular tends to dominate a
page's footprint once present — skip it when it is not the point, and when content genuinely
wants to be watched, keep it short and put a play button in front of it. Hover effects, scroll
animations, and fade-ins feel weightless but accumulate real CPU cost; keep the ones that improve
the experience and drop the rest.

**Use typography efficiently.** Fonts already installed on the device cost nothing at all.
Headings and navigation carry more visual weight than body copy, so a distinctive display face
there with system fonts for body text captures most of the design value at a fraction of the
cost. Cut the number of weights — few designs genuinely need five — and where wide variation is
needed, one variable font can replace many static files.

Further reading: *Sustainable Web Design* by Tom Greenwood (A Book Apart, 2021), and
[sustainablewebdesign.org](https://sustainablewebdesign.org/).

---

## A note on scope

This document covers what can be built into a website. Two things it deliberately leaves out are
organisational rather than technical: taking planetary limits into account when scoping a project
in the first place, and validating assumptions through user testing. Both matter, both are
handled at project level, and neither belongs in a developer handover — their absence here is not
an oversight.
