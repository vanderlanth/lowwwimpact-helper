# Compatibility — Sustainable Cross-Browser Support

Audit and harden this project for broad compatibility, progressive enhancement, and graceful degradation. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Progressive Enhancement

Build in layers: semantic HTML first, CSS second, JavaScript last. Every layer must be independently functional before the next is applied.

### HTML Layer — Baseline Functionality
- Every interactive element must work as a native HTML control before JavaScript is applied.
- Use the correct semantic element for the job. Flag misuse of `<div>` or `<span>` where a native element exists:

| Wrong | Right |
|---|---|
| `<div onclick="...">` | `<button type="button">` |
| `<div class="link">` | `<a href="...">` |
| `<div class="input">` | `<input type="...">` |
| `<div role="navigation">` | `<nav>` |
| Custom date picker | `<input type="date">` |
| Custom dropdown | `<select>` + `<option>` |

- Forms must be fully submittable via native `<form action="..." method="post">` without JavaScript. Flag any form that relies entirely on a JS `fetch`/`XHR` handler with no `<form>` fallback.
- Navigation must be traversable with keyboard and without JS. Flag `<a href="#">` or `<a href="javascript:void(0)">` used for real navigation.

### CSS Layer — Visual Enhancement
- Core layout and readability must be intact with no CSS at all (plain HTML view).
- Apply CSS enhancements in layers using `@supports` to avoid breaking older browsers:
  ```css
  /* Base layout — works everywhere */
  .grid {
    display: block;
  }

  /* Enhancement — only where Grid is supported */
  @supports (display: grid) {
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.5rem;
    }
  }
  ```
- Never use a CSS feature as the sole means of conveying information (color alone, position alone).

### JavaScript Layer — Behavioural Enhancement
- Treat JS as an enhancement. Every JS feature must have a no-JS fallback defined:

| Feature | No-JS fallback |
|---|---|
| Modal / dialog | Link to a separate page or `<details>` |
| Accordion | `<details>` + `<summary>` |
| Tabs | Anchor links to sections |
| Infinite scroll | Paginated `<a>` navigation links |
| Form validation | Native HTML5 `required`, `type`, `pattern` |
| Lazy-loaded images | `loading="lazy"` attribute (no JS needed) |
| Smooth scroll | `scroll-behavior: smooth` in CSS |

- Use `<noscript>` to surface fallback content or a warning when JS is unavailable and a fallback cannot be fully implemented:
  ```html
  <noscript>
    <p>This feature requires JavaScript. <a href="/static-version">View the static version.</a></p>
  </noscript>
  ```

---

## 2. Avoid Experimental or Poorly-Supported APIs

Flag any Web API, CSS property, or HTML feature with less than **90% global browser support** (per caniuse.com) that is used without a feature check or polyfill.

### JavaScript API Safety
Always check for API existence before use. Never assume availability:
```js
// Unsafe — will throw on older Safari / Firefox
navigator.clipboard.writeText(text);

// Safe — feature-detect first
if (navigator.clipboard?.writeText) {
  await navigator.clipboard.writeText(text);
} else {
  // Fallback: execCommand (deprecated but widely supported)
  const el = document.createElement('textarea');
  el.value = text;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
}
```

Common APIs to always guard:

| API | Risk | Safe alternative |
|---|---|---|
| `navigator.clipboard` | Safari 13.1-, Android WebView | `execCommand('copy')` fallback |
| `IntersectionObserver` | IE 11 | Polyfill or scroll listener fallback |
| `ResizeObserver` | Safari 13.1- | Polyfill or window resize fallback |
| `CSS.supports()` | IE 11 | `@supports` in CSS only |
| `fetch()` | IE 11, old Android | `whatwg-fetch` polyfill or `XMLHttpRequest` |
| `dialog` element | Firefox <98, Safari <15.4 | Custom modal with ARIA |
| `<details>/<summary>` | Old Android | JS-toggled class fallback |
| CSS Container Queries | Safari <16 | `@supports` guard + media query fallback |
| CSS `:has()` | Firefox <121 | `@supports` guard |
| CSS `subgrid` | Chrome <117, Firefox <71 | Nested grid fallback |
| Web Components | IE 11, old Android | Server-rendered HTML fallback |

### Polyfill Strategy
- Only polyfill features you actually use. Do not load a blanket polyfill bundle.
- Prefer conditional loading via `<script type="module">` (modern) and `<script nomodule>` (legacy):
  ```html
  <!-- Modern browsers — ES modules, no polyfills needed -->
  <script type="module" src="/js/app.js"></script>

  <!-- Legacy browsers — polyfilled bundle -->
  <script nomodule src="/js/app.legacy.js"></script>
  ```
- For individual API polyfills, load only when missing:
  ```js
  if (!window.IntersectionObserver) {
    await import('/polyfills/intersection-observer.js');
  }
  ```

---

## 3. Functionality Without JavaScript

Audit the project and classify every interactive feature as:
- **JS-free** — works natively (forms, links, `<details>`, `loading="lazy"`)
- **JS-enhanced** — works without JS, better with it
- **JS-dependent** — broken without JS (must add fallback or native alternative)

Flag all JS-dependent features and apply one of these resolutions:

### Native HTML Alternatives
Replace custom JS widgets with native HTML where possible:

**Accordion — replace with `<details>`:**
```html
<details>
  <summary>Section Title</summary>
  <p>Content visible when expanded, no JS required.</p>
</details>
```

**Tooltip — replace with `<abbr>` or `title`:**
```html
<abbr title="Cascading Style Sheets">CSS</abbr>
```

**Progress — replace with `<progress>`:**
```html
<progress value="60" max="100">60%</progress>
```

**Inline validation — use native HTML5 constraints:**
```html
<input
  type="email"
  required
  pattern="[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$"
  autocomplete="email"
  aria-describedby="email-hint"
/>
```

### Server-Side Rendering Fallback
- Any content rendered client-side via JS must also be renderable server-side. Flag single-page app routes that return an empty HTML shell — add server rendering or static pre-rendering.
- Pagination, filtering, and sorting must work via URL parameters and server response when JS is disabled:
  ```html
  <!-- JS-free sort: form submits GET request -->
  <form method="get" action="/products">
    <select name="sort" onchange="this.form.submit()">
      <option value="price-asc">Price: Low to High</option>
      <option value="price-desc">Price: High to Low</option>
    </select>
    <noscript><button type="submit">Sort</button></noscript>
  </form>
  ```

---

## 4. Testing Targets

### Low-End Android Devices
Simulate a low-end Android device in Chrome DevTools:
- Open DevTools → Performance → CPU throttling: **6× slowdown**
- Network throttling: **Slow 3G** (40 Kbps down, 750ms RTT)
- Device emulation: select a low-end Android preset (e.g. Moto G4)

Flag any page that:
- Takes > 5 seconds to first meaningful interaction on 6× CPU slowdown
- Loads more than 1.5 MB of JavaScript
- Triggers more than 3 seconds of main-thread blocking during load
- Uses CSS animations that drop below 30 fps on throttled CPU

Audit checklist for low-end devices:
- [ ] Total JS payload < 150 KB compressed
- [ ] No synchronous `document.write()` calls
- [ ] No `setTimeout` chains used for layout
- [ ] Images served with `loading="lazy"` below the fold
- [ ] No web fonts loaded before first paint (use `font-display: swap`)

### Older Safari Versions
Target **Safari 14+** as the minimum (iOS 14 = released 2020, still in significant use).

Flag usage of these Safari-specific pain points:

| Feature | Safari issue | Fix |
|---|---|---|
| `position: sticky` in overflow containers | Requires `-webkit-` prefix in Safari <13 | Add `-webkit-sticky` fallback |
| CSS `gap` in Flexbox | Safari <14.1 has partial support | Use `margin` fallback or `@supports` |
| `aspect-ratio` | Safari <15 | Add padding-bottom hack fallback |
| `inert` attribute | Safari <15.5 | Polyfill |
| `<dialog>` | Safari <15.4 | Custom ARIA modal fallback |
| `:focus-visible` | Safari <15.4 | `focus-visible` polyfill |
| Web Push API | iOS Safari <16.4 | Do not rely on it; offer email fallback |
| CSS `dvh`/`svh`/`lvh` | Safari <15.4 | Use `vh` with `-webkit-fill-available` fallback |
| Scroll-driven animations | Safari <18 | `@supports` guard + static fallback |

**iOS Safari specific:**
- Test on a real iOS device or Xcode Simulator — Chrome DevTools emulation does not replicate iOS Safari rendering.
- Flag any `position: fixed` element that overlaps the iOS Safari bottom toolbar — add `env(safe-area-inset-bottom)` padding:
  ```css
  .sticky-footer {
    padding-bottom: max(1rem, env(safe-area-inset-bottom));
  }
  ```

### Slow 3G Mode
Simulate in Chrome DevTools → Network → Slow 3G (40 Kbps, 2000ms latency).

Flag any page that fails these targets on Slow 3G:
- First Contentful Paint > 3 seconds
- Largest Contentful Paint > 5 seconds
- Total page weight > 1 MB on first load
- More than 5 render-blocking resources
- Any image above the fold not using `fetchpriority="high"`

Checklist:
- [ ] Critical CSS inlined in `<head>` (< 14 KB)
- [ ] Non-critical CSS deferred with `media="print" onload="this.media='all'"`
- [ ] JS deferred with `defer` or `async`
- [ ] Hero image preloaded with `<link rel="preload" as="image">`
- [ ] No third-party scripts loaded synchronously in `<head>`
- [ ] Service worker caches shell on second visit

---

## 5. Avoid Heavy Frameworks for Simple Features

Audit every JS dependency in `package.json` (or inline `<script>` tags) and flag any where a native or lightweight alternative exists.

### Dependency Audit Rules
For each dependency, answer: **could this be replaced by native browser APIs or < 2 KB of vanilla JS?**

| Heavy usage | Lightweight replacement |
|---|---|
| jQuery (for DOM manipulation) | `document.querySelector`, `fetch`, `classList` |
| jQuery (for AJAX) | `fetch()` API |
| Lodash (full bundle) | Native `Array`, `Object` methods or tree-shaken import |
| Moment.js | `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat`, or `date-fns` (tree-shaken) |
| Axios | `fetch()` with a thin 200-byte wrapper |
| Full React/Vue/Angular app for a marketing page | HTML + vanilla JS or a static site generator |
| A UI component library for one component | Native HTML element or < 100 lines vanilla JS |
| GSAP for a single fade | CSS `transition: opacity` |
| Swiper.js for one carousel | CSS `scroll-snap` + minimal JS for controls |
| Animate.css for one animation | Single `@keyframes` declaration |

### Bundle Size Targets

| Asset type | Target (compressed) | Warning threshold |
|---|---|---|
| Total JS (first load) | < 100 KB | > 150 KB |
| Per-route JS chunk | < 50 KB | > 80 KB |
| Total CSS | < 30 KB | > 50 KB |
| Third-party scripts | < 20 KB | > 40 KB |

Flag any single dependency that contributes more than 20 KB compressed to the bundle without a clear justification.

---

## 6. Baseline Browser Support Policy

Define and document the minimum supported browser versions for this project. Flag any code that targets browsers below the defined baseline.

**Recommended minimum baseline (2024+):**

| Browser | Minimum version | Market share floor |
|---|---|---|
| Chrome / Edge | 109+ | Cover ~85%+ of users |
| Firefox | 115+ (ESR) | Cover ~85%+ of users |
| Safari | 14+ | Cover ~90%+ of Safari users |
| iOS Safari | 14+ | Cover ~85%+ of iOS users |
| Samsung Internet | 19+ | Cover ~80%+ of Samsung users |
| Android WebView | Chrome 109+ | — |

Add a `.browserslistrc` to the project root to enforce this across all build tools (Autoprefixer, Babel, ESBuild):
```
# .browserslistrc
[production]
chrome >= 109
edge >= 109
firefox >= 115
safari >= 14
ios_safari >= 14
samsung >= 19
not ie 11
not op_mini all
```

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied
List every file modified — JS-dependent features converted to native HTML, `@supports` guards added, experimental APIs wrapped in feature checks, heavy dependencies replaced, `.browserslistrc` added.

### ⚠️ Manual Actions Required
List items requiring human testing or decisions — real device testing on iOS Safari, downloading polyfill files, replacing a framework that requires architectural changes. Include exact file paths and steps.

### Testing Checklist
Provide a copy-paste checklist for manual QA:
- [ ] Test on Chrome with CPU 6× throttle + Slow 3G
- [ ] Test on iOS Safari 14 (Xcode Simulator or real device)
- [ ] Test on Android Chrome with network throttling
- [ ] Disable JavaScript in browser and verify core content is readable
- [ ] Run Lighthouse with Mobile preset — target Performance > 80
- [ ] Run `npx browserslist` to confirm supported range matches `.browserslistrc`
- [ ] Check bundle sizes: `npx bundlesize` or build output stats

### 📊 Estimated Impact
Provide a rough before/after summary of:
- JS bundle size reduction (KB)
- Number of experimental/unguarded API calls fixed
- Number of JS-dependent features given native or no-JS fallbacks
- Dependencies removed or replaced
- Browsers newly supported by the changes
