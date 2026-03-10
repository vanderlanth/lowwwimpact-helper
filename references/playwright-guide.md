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
# Desktop
playwright-cli -s=<session> resize 1440 900

# Tablet
playwright-cli -s=<session> resize 768 1024

# Mobile
playwright-cli -s=<session> resize 375 812
```

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

## Best Practices for Sustainability Audit Agents

1. **Always capture network data first** — Run `network` after page fully loads to get the resource inventory
2. **Use Performance API for sizes** — `performance.getEntriesByType('resource')` gives accurate transfer sizes
3. **Snapshot before inspecting** — Know the DOM structure before running eval queries
4. **Screenshot for evidence** — Capture visual proof of issues (unoptimized images, layout shifts)
5. **Check response headers** — Cache-Control and Content-Encoding headers are critical for infra audits
6. **Reload for fresh data** — If you navigated from another page, reload to get clean network timing
7. **Count third-party domains** — Every external domain is a sustainability concern
8. **Close your session** — Always clean up when done
