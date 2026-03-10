# Code Efficiency for Sustainable Web Design

## Minification Rules

All source code must be minified in production builds:

| File Type | Minification | Notes |
|---|---|---|
| HTML | Remove whitespace, comments, optional tags | Use html-minifier or framework built-in |
| CSS | Remove whitespace, comments, merge rules | Use cssnano, Lightning CSS, or framework built-in |
| JavaScript | Remove whitespace, comments, shorten variables | Use Terser, esbuild, or SWC |
| JSON | Remove whitespace | Applies to API responses and data files |
| SVG | Remove metadata, comments, unused attributes | Use SVGO with safe preset |

## Native API Alternatives

Replace heavy third-party libraries with native browser APIs:

| Instead of | Use | Savings |
|---|---|---|
| axios (~13 KB gzipped) | `fetch()` API | ~13 KB |
| moment.js (~72 KB gzipped) | `Intl.DateTimeFormat` + `Intl.RelativeTimeFormat` | ~72 KB |
| lodash (~72 KB full, ~4 KB per method) | Native array/object methods (`map`, `filter`, `reduce`, `structuredClone`, `Object.groupBy`) | 4-72 KB |
| jQuery (~30 KB gzipped) | `document.querySelector`, `addEventListener`, `fetch` | ~30 KB |
| Modal library | `<dialog>` element (native) | 5-30 KB |
| Smooth scroll library | `scroll-behavior: smooth` (CSS) | 2-10 KB |
| Tooltip library | CSS `::after` + `[data-tooltip]` or Popover API | 5-20 KB |
| Date picker library | `<input type="date">` (native) | 10-50 KB |
| Intersection observer polyfill | `IntersectionObserver` (native, universal support) | 2-5 KB |
| Animate on scroll library | `@starting-style` + `transition` or `IntersectionObserver` + CSS | 5-15 KB |
| Color picker library | `<input type="color">` (native) | 10-30 KB |
| Form validation library | Constraint Validation API (`setCustomValidity`, `:invalid`) | 5-20 KB |

## Tree-Shaking and Code Splitting

### Tree-shaking
- Use ES module `import { specific } from 'library'` — never `import * as lib` or `require()`
- Ensure `"sideEffects": false` in `package.json` for tree-shakeable packages
- Audit bundles with `npx vite-bundle-visualizer` or `webpack-bundle-analyzer`

### Code splitting
- Split routes/pages into separate chunks (SvelteKit/Next.js/Nuxt do this automatically)
- Dynamically import heavy components:
  ```javascript
  const HeavyComponent = () => import('./HeavyComponent.svelte');
  ```
- Dynamically import non-critical third-party code:
  ```javascript
  button.addEventListener('click', async () => {
    const { confetti } = await import('canvas-confetti');
    confetti();
  });
  ```

## Script Loading

| Strategy | Attribute | Use When |
|---|---|---|
| Deferred | `<script defer src="...">` | Default for all scripts — downloads in parallel, executes after HTML parsing |
| Async | `<script async src="...">` | Independent scripts (analytics) that don't depend on DOM or other scripts |
| Module | `<script type="module" src="...">` | ES modules — deferred by default, supports `import`/`export` |
| Inline critical | `<script>...</script>` in `<head>` | Only for tiny critical-path scripts (<1 KB) |

### Rules
- Never use render-blocking `<script src="...">` without `defer` or `async`
- Place non-critical scripts at the end of `<body>` or use `defer`
- Use `type="module"` for modern ES module scripts (automatically deferred)
- Inline only truly critical JavaScript (<1 KB); everything else should be external and cacheable

## CSS Methodology

### Critical CSS
- Inline critical above-the-fold CSS in a `<style>` tag in `<head>` (<14 KB)
- Load remaining CSS asynchronously:
  ```html
  <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="styles.css"></noscript>
  ```

### CSS organization
- Use BEM naming (`.block__element--modifier`) or similar methodology to avoid duplication
- Use `content-visibility: auto` on long off-screen sections to skip rendering:
  ```css
  .below-fold-section {
    content-visibility: auto;
    contain-intrinsic-size: auto 500px;
  }
  ```
- Remove unused CSS — audit with Chrome DevTools Coverage tab
- Prefer CSS solutions over JavaScript (animations, toggles, accordions via `:has()` and `<details>`)
- Use CSS custom properties for theming to avoid duplicate rule sets

### Dark mode (energy savings on OLED screens)

```css
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --text: #e0e0e0;
  }
}
```

OLED energy impact data (from Google):
- Night mode on Google Maps reduced screen power draw by 63%
- Black is the most efficient color on OLED (pixels are off)
- White is the most energy-intensive color on OLED
- Blue pixels consume ~25% more energy than green or red

## Cache-Control Headers

| Asset Type | `Cache-Control` | `max-age` | Notes |
|---|---|---|---|
| HTML pages | `no-cache` | — | Always revalidate; use `ETag` for conditional requests |
| CSS with hash | `public, immutable` | `31536000` (1 year) | Filename hash ensures cache-busting on change |
| JS with hash | `public, immutable` | `31536000` (1 year) | Filename hash ensures cache-busting on change |
| Images | `public` | `2592000` (30 days) | Use content-hashed filenames for longer caching |
| Fonts | `public, immutable` | `31536000` (1 year) | Fonts rarely change; immutable is safe |
| JSON API responses | `private, no-cache` | — | Revalidate with `ETag`; cache per-user data only privately |
| Favicon | `public` | `604800` (7 days) | Changes infrequently |

## Service Worker for Offline Caching

```javascript
const CACHE_NAME = 'v1';
const PRECACHE_URLS = [
  '/',
  '/styles.css',
  '/app.js',
  '/offline.html'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => caches.match('/offline.html'))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request).then((response) => {
        if (response.ok && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      });
    })
  );
});
```

## Server Compression Configuration

### Apache (.htaccess) — Brotli with GZIP fallback

```apache
# Enable Brotli compression
<IfModule mod_brotli.c>
  AddOutputFilterByType BROTLI_COMPRESS text/html text/plain text/xml
  AddOutputFilterByType BROTLI_COMPRESS text/css text/javascript application/javascript
  AddOutputFilterByType BROTLI_COMPRESS application/json application/xml
  AddOutputFilterByType BROTLI_COMPRESS image/svg+xml
  AddOutputFilterByType BROTLI_COMPRESS application/font-woff2
</IfModule>

# GZIP fallback
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml
  AddOutputFilterByType DEFLATE text/css text/javascript application/javascript
  AddOutputFilterByType DEFLATE application/json application/xml
  AddOutputFilterByType DEFLATE image/svg+xml
</IfModule>

# Cache-Control headers
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/avif "access plus 1 month"
  ExpiresByType image/webp "access plus 1 month"
  ExpiresByType image/jpeg "access plus 1 month"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
  ExpiresByType font/woff2 "access plus 1 year"
</IfModule>
```

### Nginx — Brotli with GZIP fallback

```nginx
# Brotli compression
brotli on;
brotli_types text/html text/plain text/xml text/css
             text/javascript application/javascript
             application/json application/xml
             image/svg+xml application/font-woff2;
brotli_comp_level 6;

# GZIP fallback
gzip on;
gzip_types text/html text/plain text/xml text/css
           text/javascript application/javascript
           application/json application/xml
           image/svg+xml;
gzip_min_length 256;

# Static asset caching
location ~* \.(css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(avif|webp|jpg|jpeg|png|svg|gif|ico)$ {
    expires 30d;
    add_header Cache-Control "public";
}

location ~* \.(woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Third-Party Management

### Facade Pattern

Load third-party content only when the user interacts with it. This applies to:
- Embedded maps (Google Maps, Mapbox) — show a static image with a "Load map" button
- Video embeds (YouTube, Vimeo) — show a poster image with a play button
- Social media embeds (Twitter, Instagram) — show a screenshot or quote with a "View on..." link
- Chat widgets — show a "Start chat" button, load the widget on click
- Comment sections (Disqus) — show a "Load comments" button

### Self-Hosting Decision Matrix

| Third-Party Resource | Self-Host? | Reason |
|---|---|---|
| Google Fonts | Yes | Eliminates DNS lookup + connection to fonts.googleapis.com; host as subsetted WOFF2 |
| Analytics (GA 17 KB) | Replace | Use lightweight self-hosted alternative (Plausible ~1 KB, Fathom ~1.2 KB, Umami) |
| Google Maps | Facade | Show static map image; load interactive map only on user interaction |
| YouTube video | Facade | Show poster image; load iframe only on play click |
| Icon library (Font Awesome 60+ KB) | Replace | Use individual SVG icons inline; only include icons you actually use |
| jQuery (30 KB) | Remove | Replace with native browser APIs |
| CSS framework (Bootstrap ~22 KB) | Evaluate | Consider if you use >30% of the framework; otherwise, write custom CSS |

### Self-hosting rules
- Self-host all fonts — never load from third-party CDNs (eliminates extra DNS + connection overhead)
- Self-host analytics if possible — use privacy-friendly lightweight alternatives
- For content that must remain third-party (YouTube, maps), always use a click-to-load facade
- Audit third-party impact: each additional third-party domain adds DNS lookup (50-200ms) + TLS handshake (100-300ms)
- Maximum 4 third-party domains (target), 2 (stretch goal)
