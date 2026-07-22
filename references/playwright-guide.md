# Playwright CLI Reference for Sustainability Audit Agents

Quick reference for the Playwright CLI commands most useful during sustainability audits.
Always use your assigned session name (`-s=<session>`) to avoid conflicts with other agents.

## Session Management

```bash
# Open browser with named session
playwright-cli -s=<session> open <url>

# Navigate to a different page
playwright-cli -s=<session> goto <url>

# Close your session when done
playwright-cli -s=<session> close

# List all active sessions (coordinator only)
playwright-cli list
playwright-cli close-all
```

## Capturing Page State

### Snapshots (Structured Text — Primary Analysis Tool)

Snapshots return the page's accessibility tree with element references (refs).
Use snapshots to inventory page elements: images, scripts, links, iframes, forms, and headings.

```bash
# Capture snapshot to stdout
playwright-cli -s=<session> snapshot

# Save to file for later reference
playwright-cli -s=<session> snapshot --filename=<name>.txt
```

Snapshots contain:
- All visible text content
- Element types (img, video, iframe, script, link, etc.)
- Element references (e.g., `e21`, `e35`) for interaction
- ARIA roles and labels
- Form field states
- Hierarchical structure

### Screenshots (Visual Evidence)

Screenshots capture what the user sees — use for documenting page weight issues, layout shifts, and visual evidence of unoptimized assets.

```bash
# Full page screenshot
playwright-cli -s=<session> screenshot --filename=<name>.png

# Screenshot of a specific element
playwright-cli -s=<session> screenshot <ref> --filename=<name>.png
```

## Network Analysis (Critical for Sustainability Audits)

Network inspection is the primary tool for sustainability agents. It reveals resource sizes,
types, domains, compression, and caching headers.

```bash
# List all network requests (shows URL, status, size, type)
playwright-cli -s=<session> network
```

### JavaScript Evaluation for Network / Resource Inspection

```bash
# Count all resources by type via Performance API
playwright-cli -s=<session> eval "JSON.stringify(performance.getEntriesByType('resource').reduce((acc, r) => { const t = r.initiatorType || 'other'; acc[t] = (acc[t] || 0) + 1; return acc; }, {}))"

# Total transfer size (bytes) from Performance API
playwright-cli -s=<session> eval "performance.getEntriesByType('resource').reduce((sum, r) => sum + (r.transferSize || 0), 0)"

# List resources with sizes > 100 KB
playwright-cli -s=<session> eval "performance.getEntriesByType('resource').filter(r => r.transferSize > 102400).map(r => ({ url: r.name.split('/').pop(), size: Math.round(r.transferSize/1024) + 'KB', type: r.initiatorType }))"

# Count unique third-party domains
playwright-cli -s=<session> eval "new Set(performance.getEntriesByType('resource').map(r => new URL(r.name).hostname).filter(h => h !== location.hostname)).size"

# List third-party domains
playwright-cli -s=<session> eval "[...new Set(performance.getEntriesByType('resource').map(r => new URL(r.name).hostname).filter(h => h !== location.hostname))]"

# Get navigation timing (page load metrics)
playwright-cli -s=<session> eval "const n = performance.getEntriesByType('navigation')[0]; JSON.stringify({ domContentLoaded: Math.round(n.domContentLoadedEventEnd), loadEvent: Math.round(n.loadEventEnd), transferSize: Math.round(n.transferSize/1024) + 'KB' })"
```

## Image Inspection

```bash
# Count all images and their src attributes
playwright-cli -s=<session> eval "[...document.querySelectorAll('img')].map(i => ({ src: i.src.split('/').pop(), width: i.width, height: i.height, loading: i.loading, decoding: i.decoding, hasWidthAttr: i.hasAttribute('width'), hasHeightAttr: i.hasAttribute('height'), alt: i.alt ? 'yes' : 'missing' }))"

# Check for <picture> elements with modern format sources
playwright-cli -s=<session> eval "document.querySelectorAll('picture').length + ' picture elements; ' + document.querySelectorAll('source[type=\"image/webp\"]').length + ' webp sources; ' + document.querySelectorAll('source[type=\"image/avif\"]').length + ' avif sources'"

# Find images without lazy loading (excluding likely LCP)
playwright-cli -s=<session> eval "[...document.querySelectorAll('img')].filter((img, i) => i > 0 && img.loading !== 'lazy').map(i => i.src.split('/').pop())"

# Check for responsive images (srcset)
playwright-cli -s=<session> eval "[...document.querySelectorAll('img[srcset]')].length + ' images with srcset out of ' + document.querySelectorAll('img').length + ' total'"

# Find CSS background images
playwright-cli -s=<session> eval "[...document.querySelectorAll('*')].filter(el => getComputedStyle(el).backgroundImage !== 'none' && getComputedStyle(el).backgroundImage.includes('url')).length + ' elements with background images'"
```

## Script & CSS Inspection

```bash
# List all script tags with src, async, defer, type attributes
playwright-cli -s=<session> eval "[...document.querySelectorAll('script[src]')].map(s => ({ src: s.src.split('/').pop(), async: s.async, defer: s.defer, type: s.type || 'classic', isModule: s.type === 'module' }))"

# Count render-blocking scripts (no async, no defer, no module)
playwright-cli -s=<session> eval "[...document.querySelectorAll('script[src]')].filter(s => !s.async && !s.defer && s.type !== 'module').length"

# List all stylesheets
playwright-cli -s=<session> eval "[...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.href.split('/').pop())"

# Check for inline critical CSS
playwright-cli -s=<session> eval "document.querySelectorAll('style').length + ' inline style blocks; total chars: ' + [...document.querySelectorAll('style')].reduce((sum, s) => sum + s.textContent.length, 0)"

# Detect known heavy libraries
playwright-cli -s=<session> eval "JSON.stringify({ jquery: typeof jQuery !== 'undefined', moment: typeof moment !== 'undefined', lodashFull: typeof _ !== 'undefined' && typeof _.VERSION !== 'undefined', axios: typeof axios !== 'undefined' })"
```

## Font Inspection

```bash
# List loaded fonts via document.fonts
playwright-cli -s=<session> eval "[...document.fonts].filter(f => f.status === 'loaded').map(f => ({ family: f.family, weight: f.weight, style: f.style }))"

# Check for Google Fonts or external font CDN
playwright-cli -s=<session> eval "performance.getEntriesByType('resource').filter(r => r.name.includes('fonts.googleapis.com') || r.name.includes('fonts.gstatic.com') || r.name.includes('use.typekit.net')).map(r => r.name)"

# Count font files and total size
playwright-cli -s=<session> eval "const fonts = performance.getEntriesByType('resource').filter(r => /\\.(woff2?|ttf|otf|eot)/.test(r.name)); JSON.stringify({ count: fonts.length, totalKB: Math.round(fonts.reduce((s, f) => s + f.transferSize, 0) / 1024) })"
```

## Video & Iframe Inspection

```bash
# List all video elements and their attributes
playwright-cli -s=<session> eval "[...document.querySelectorAll('video')].map(v => ({ autoplay: v.autoplay, preload: v.preload, poster: !!v.poster, muted: v.muted, sources: [...v.querySelectorAll('source')].map(s => s.type) }))"

# List all iframes (potential third-party embeds)
playwright-cli -s=<session> eval "[...document.querySelectorAll('iframe')].map(f => ({ src: f.src, width: f.width, height: f.height, loading: f.loading }))"

# Check for YouTube/Vimeo direct embeds (no facade)
playwright-cli -s=<session> eval "[...document.querySelectorAll('iframe')].filter(f => /youtube|vimeo|youtu\\.be/.test(f.src)).map(f => f.src)"
```

## HTTP Header & Caching Inspection

```bash
# Check response headers for the current page
playwright-cli -s=<session> eval "fetch(location.href, {method: 'HEAD'}).then(r => JSON.stringify(Object.fromEntries(r.headers)))"

# Check Cache-Control header for a specific resource URL
playwright-cli -s=<session> eval "fetch('<resource-url>', {method: 'HEAD'}).then(r => r.headers.get('cache-control'))"

# Check if Brotli or Gzip is active
playwright-cli -s=<session> eval "fetch(location.href, {method: 'HEAD'}).then(r => 'content-encoding: ' + r.headers.get('content-encoding'))"
```

## HTML Structure Inspection

```bash
# Check meta tags
playwright-cli -s=<session> eval "JSON.stringify({ lang: document.documentElement.lang, charset: document.characterSet, viewport: document.querySelector('meta[name=viewport]')?.content, title: document.title, description: document.querySelector('meta[name=description]')?.content })"

# Check heading hierarchy
playwright-cli -s=<session> eval "[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => h.tagName + ': ' + h.textContent.trim().substring(0, 60))"

# Check semantic landmarks
playwright-cli -s=<session> eval "JSON.stringify({ nav: document.querySelectorAll('nav').length, main: document.querySelectorAll('main').length, aside: document.querySelectorAll('aside').length, footer: document.querySelectorAll('footer').length, header: document.querySelectorAll('header').length, article: document.querySelectorAll('article').length })"

# Check for service worker
playwright-cli -s=<session> eval "navigator.serviceWorker?.controller ? 'Service worker active' : 'No service worker'"

# Check for preload/preconnect hints
playwright-cli -s=<session> eval "[...document.querySelectorAll('link[rel=preload], link[rel=preconnect], link[rel=dns-prefetch]')].map(l => ({ rel: l.rel, href: l.href, as: l.as || '' }))"
```

## CSS Feature Detection

```bash
# Check for prefers-reduced-motion support in stylesheets
playwright-cli -s=<session> eval "[...document.styleSheets].some(ss => { try { return [...ss.cssRules].some(r => r.cssText?.includes('prefers-reduced-motion')); } catch { return false; } })"

# Check for prefers-color-scheme (dark mode) support
playwright-cli -s=<session> eval "[...document.styleSheets].some(ss => { try { return [...ss.cssRules].some(r => r.cssText?.includes('prefers-color-scheme')); } catch { return false; } })"

# Check for content-visibility usage
playwright-cli -s=<session> eval "[...document.querySelectorAll('*')].filter(el => getComputedStyle(el).contentVisibility === 'auto').length + ' elements with content-visibility: auto'"
```

## Navigation

```bash
# Go back/forward
playwright-cli -s=<session> go-back
playwright-cli -s=<session> go-forward

# Reload (useful to capture fresh network data)
playwright-cli -s=<session> reload
```

## Viewport

```bash
# Desktop (standard audit viewport)
playwright-cli -s=<session> resize 1440 760

# Tablet
playwright-cli -s=<session> resize 768 1024

# Mobile
playwright-cli -s=<session> resize 375 812
```

> **Standard audit viewport**: always call `resize 1440 760` immediately after `open` in every audit session. This ensures consistent measurements across Playwright and Lighthouse (see Lighthouse flag block below).

## Scrolling

```bash
# Scroll down one viewport
playwright-cli -s=<session> eval "window.scrollBy(0, window.innerHeight)"

# Scroll to top
playwright-cli -s=<session> eval "window.scrollTo(0, 0)"

# Scroll to bottom
playwright-cli -s=<session> eval "window.scrollTo(0, document.body.scrollHeight)"
```

## DevTools / Diagnostics

```bash
# Check console for errors
playwright-cli -s=<session> console error

# List network requests
playwright-cli -s=<session> network

# View all console messages
playwright-cli -s=<session> console
```

## Tabs

```bash
# Open new tab
playwright-cli -s=<session> tab-new <url>

# List tabs
playwright-cli -s=<session> tab-list

# Switch tab
playwright-cli -s=<session> tab-select <index>

# Close tab
playwright-cli -s=<session> tab-close <index>
```

## Weight Measurement Protocol

### Why fresh sessions are required for `pages` measurements

Each `playwright-cli -s=<name> open <url>` creates an isolated in-memory browser context
(equivalent to incognito). When you navigate with `goto` in the same session, the browser
reuses its cache from previous pages — subsequent pages appear artificially lighter than
they are for a real first-time visitor. Always open a **new named session** per page
when measuring cold-load weight (for `initial_weight_kb` and `deferred_weight_kb`).

### Why `run-code` + `requestfinished` is required for accurate weight measurement

The Performance API (`performance.getEntriesByType('resource')`) returns `transferSize: 0` for
any cross-origin resource without a `Timing-Allow-Origin` header. Third-party services (analytics,
consent managers, CDN fonts, YouTube iframes) almost never send this header, so their bytes are
silently dropped. On a typical tracked site this causes a severe undercount — testing showed 25 KB
reported vs 4 MB actual.

The correct approach uses `page.context().on('requestfinished')` + `request.sizes()`, which
operates at the Playwright/CDP level and captures all requests from all frames including
cross-origin iframes. Summed `responseBodySize` bytes are divided by 1000 to report KB.

**The listener must be registered before navigation** — use `run-code` so you can set it up
prior to `page.goto()`. Opening with a URL first and then navigating inside `run-code` results
in a cached reload that silently undercounts by 30–50%.

### Standard weight measurement pattern

Both `initial_weight_kb` and `deferred_weight_kb` are captured in a single `run-code` call.
**Open the session with NO URL** so the listener is attached before the first navigation:

```bash
# CRITICAL: no URL here — navigation happens inside run-code
playwright-cli -s=measure-<slug> open
playwright-cli -s=measure-<slug> resize 1440 760
playwright-cli -s=measure-<slug> run-code "async (page) => {
  const requests = [];
  page.context().on('requestfinished', (req) => requests.push(req));
  await page.goto('<url>', { waitUntil: 'load' });
  await page.waitForTimeout(5000);
  const getKB = async (reqs) => {
    const sizes = await Promise.all(reqs.map(r => r.sizes().catch(() => null)));
    const bytes = sizes.reduce((s, v) => s + (v?.responseBodySize > 0 ? v.responseBodySize : 0), 0);
    return Math.round(bytes / 1000);
  };
  const initial_weight_kb = await getKB(requests.slice());
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.25));
  await page.waitForTimeout(500);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.5));
  await page.waitForTimeout(500);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.75));
  await page.waitForTimeout(500);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(3000);
  const deferred_weight_kb = await getKB(requests.slice());
  return { initial_weight_kb, deferred_weight_kb };
}"
# → session is now at <url>; continue with eval-based inspection as normal
```

`deferred_weight_kb` is the **total** bytes transferred after scrolling to the bottom
(initial bytes + lazy-loaded additions). It is NOT a delta.

### Journey measurement — accumulated cache, delta per step

Journey `kb` uses a single `run-code` call across all steps. The listener accumulates requests
across the whole journey; each step's `kb` is the delta bytes since the previous step. Unlike the
standalone weight pass it **keeps the HTTP cache** (no `clearBrowserCache`) so steps 2+ count only
newly downloaded bytes — but it matches the standalone pass on everything else: 1440×760 viewport,
Retina DPR 2, `state-load` for authed journeys, and cookie consent accepted on step 1.

```bash
playwright-cli -s=journey-N open
playwright-cli -s=journey-N resize 1440 760
# Authed journey: inject saved login state before the first navigation.
[ -f workspace/auth-state.json ] && playwright-cli -s=journey-N state-load workspace/auth-state.json
playwright-cli -s=journey-N run-code "async (page) => {
  const requests = [];
  page.context().on('requestfinished', (req) => requests.push(req));
  const getKB = async (reqs) => {
    const sizes = await Promise.all(reqs.map(r => r.sizes().catch(() => null)));
    const bytes = sizes.reduce((s, v) => s + (v?.responseBodySize > 0 ? v.responseBodySize : 0), 0);
    return Math.round(bytes / 1000);
  };
  // Retina DPR + viewport, applied once. NO clearBrowserCache — cache is kept across steps.
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 760, deviceScaleFactor: 2, mobile: false });
  const urls = [/* step URLs from Phase A */];
  const results = [];
  for (let i = 0; i < urls.length; i++) {
    const prevCount = requests.length;
    await page.goto(urls[i], { waitUntil: 'load' });
    await page.waitForTimeout(i === 0 ? 5000 : 3000);
    if (i === 0) {
      for (const re of [/accept all/i, /allow all/i, /accept/i, /agree/i, /got it/i, /i accept/i]) {
        try { const b = page.getByRole('button', { name: re }); if (await b.first().isVisible({ timeout: 400 })) { await b.first().click(); await page.waitForTimeout(1500); break; } } catch (e) {}
      }
    }
    const title = await page.title();
    const kb = await getKB(requests.slice(prevCount));
    results.push({ url: urls[i], name: title, kb });
  }
  return results;
}"
playwright-cli -s=journey-N close
```

- Step 1 is a cold load (fresh session = empty cache); consent accepted here counts toward step 1.
- Steps 2+ reflect only newly fetched bytes — cached assets are not re-counted.
- The 5s wait on step 1 (vs 3s on subsequent steps) lets deferred analytics settle on the cold load.
- DPR 2 makes image-heavy steps count their 2x variants, consistent with `initial/deferred_weight_kb`.

---

## Injecting a third-party script under CSP (e.g. axe-core)

Injecting an external library with `eval` + `document.createElement('script')` + `await new
Promise(r => s.onload = r)` is **unsafe**: most production sites set a Content-Security-Policy
that refuses the external `<script>`, so `onload` never fires and the eval **hangs until the CLI
timeout** — with no error. Never use that pattern.

Use `run-code` instead, disable CSP at the CDP level, and rely on `addScriptTag`'s bounded
timeout (it *throws* on failure rather than hanging). Always wrap in `try/catch` and return a
sentinel so a failure can never block:

```bash
# fetch the library once, up front (local file avoids per-page CDN dependency)
curl -sL https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js -o workspace/axe.min.js

playwright-cli -s=<session> run-code "async (page) => {
  try {
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Page.setBypassCSP', { enabled: true });
    await page.reload({ waitUntil: 'load', timeout: 20000 }); // bypass takes effect on next load
    await page.addScriptTag({ path: 'workspace/axe.min.js', timeout: 20000 });
    return await page.evaluate(async () => { /* library is now global; use it */ });
  } catch (e) {
    return { error: String(e && e.message || e) };
  }
}"
```

`Page.setBypassCSP` is the same mechanism Playwright's `bypassCSP` context option uses; it takes
effect on the next navigation, which is why the `reload` is required. If the local file is missing,
pass `{ url: '<cdn-url>', timeout: 20000 }` to `addScriptTag` — CSP is already off, so the CDN loads
too. On `{ error }`, do not retry — fall back to another signal.

---

## Best Practices for Sustainability Audit Agents

1. **Fresh session per page** — Never reuse a session across URLs for weight measurement; each new named session starts with empty cache
2. **Use `run-code` for weight measurement** — Register `page.context().on('requestfinished')` before navigation; Performance API misses cross-origin resources entirely
3. **Always wait for load + 3s** — `new Promise(r => { if (document.readyState === 'complete') r(); else window.addEventListener('load', r, {once: true}); })` then `setTimeout(r, 3000)`
4. **Snapshot before inspecting** — Know the DOM structure before running eval queries
5. **Screenshot for evidence** — Capture visual proof of issues (unoptimized images, layout shifts)
6. **Check response headers** — Cache-Control and Content-Encoding headers are critical for infra audits
7. **Count third-party domains** — Every external domain is a sustainability concern
8. **Close your session** — Always clean up when done
