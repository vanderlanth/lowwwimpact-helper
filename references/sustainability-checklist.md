# Sustainability Audit Checklist

Use this checklist to audit a web page or project for sustainability. Each item maps to a W3C Web Sustainability Guideline (WSG) ID and includes a measurable threshold where applicable.

## Images

- [ ] Images use modern formats (AVIF preferred, WebP fallback, JPEG last resort) — WSG 2.15
- [ ] All photographs are compressed at 80% quality; recompressing at 80% yields <20% size reduction — WSG 2.15
- [ ] Responsive `srcset` and `sizes` attributes are used with multiple image widths — WSG 2.15
- [ ] `<picture>` with format fallback (`<source type="image/avif">`, `<source type="image/webp">`) — WSG 2.15
- [ ] Total image weight per page is <500 KB (stretch: <200 KB) — WSG 2.15
- [ ] Single hero image is <150 KB (stretch: <80 KB) — WSG 2.15
- [ ] LCP image uses `loading="eager"` (or no attribute); all below-fold images use `loading="lazy"` — WSG 2.15
- [ ] All `<img>` elements include `width` and `height` attributes to prevent CLS — WSG 2.15
- [ ] All `<img>` elements include `decoding="async"` — WSG 2.15
- [ ] All non-decorative images have descriptive `alt` text — WSG 3.5
- [ ] Decorative images use `alt=""` — WSG 3.5
- [ ] SVGs are optimized with SVGO (metadata, unused groups removed) — WSG 2.15
- [ ] SVG icons use `aria-hidden="true"` when paired with text labels — WSG 3.5
- [ ] CSS or SVG is used instead of raster images where possible (icons, illustrations, backgrounds) — WSG 2.15
- [ ] Images are self-hosted (not loaded from third-party CDNs unless using a facade) — WSG 3.7

## Video

- [ ] Videos do not autoplay — use `preload="none"` and a poster image — WSG 2.16
- [ ] YouTube/Vimeo embeds use a click-to-load facade (poster + play button) — WSG 2.16, 3.7
- [ ] Self-hosted videos use `<video>` with WebM primary source and MP4 fallback — WSG 2.16
- [ ] Video files are compressed; recompressing yields <20% size reduction — WSG 2.16
- [ ] Captions are provided via `<track kind="captions">` with WebVTT files — WSG 2.16, 3.5
- [ ] Videos are wrapped in `<figure>` with `<figcaption>` — WSG 2.16
- [ ] Video has playback controls (play, pause, volume, fullscreen) — WSG 2.16
- [ ] Alternative content (text transcripts) is available for all video/audio — WSG 2.16

## Fonts

- [ ] Custom fonts use WOFF2 format exclusively — WSG 2.18
- [ ] Fonts are subsetted to only required character sets — WSG 2.19
- [ ] Single font weight (subsetted WOFF2) is <25 KB (stretch: <10 KB) — WSG 2.18
- [ ] Total font weight is <50 KB (stretch: <20 KB) — WSG 2.18
- [ ] Maximum 2 font weights are loaded — WSG 2.18
- [ ] `font-display: swap` is used in `@font-face` declarations — WSG 2.18
- [ ] System font fallback stack is declared — WSG 2.18
- [ ] Fonts are self-hosted (not loaded via third-party font services) — WSG 2.18, 3.7
- [ ] Body text considers system fonts; custom fonts reserved for headings/brand — WSG 2.18

## Animation

- [ ] CSS animations use compositor-only properties (`transform`, `opacity`) — WSG 2.17
- [ ] `prefers-reduced-motion: reduce` media query removes or minimizes all animation — WSG 2.17
- [ ] Continuous animations have a visible pause/stop control — WSG 2.17
- [ ] No GIF files are used — replaced with animated WebP, CSS animation, or MP4 — WSG 2.17
- [ ] Animations serve a functional purpose (user guidance, feedback) — not purely decorative — WSG 2.17
- [ ] Number of simultaneous animations per page is minimized — WSG 2.17
- [ ] No scroll-jacking or hijacked scroll behavior — WSG 2.17

## JavaScript

- [ ] Total JavaScript (compressed/transferred) is <200 KB (stretch: <100 KB) — WSG 3.2
- [ ] JavaScript is minified in production — WSG 3.2
- [ ] All scripts use `defer`, `async`, or `type="module"` — no render-blocking scripts — WSG 3.2
- [ ] Tree-shaking is enabled; only imported functions are bundled — WSG 3.6
- [ ] Route-based code splitting is used (separate chunks per page/route) — WSG 3.6
- [ ] Native browser APIs are used instead of heavy libraries (fetch vs axios, dialog vs modal lib, Intl vs moment.js) — WSG 3.23
- [ ] Unused JavaScript is identified and removed (Chrome Coverage tab) — WSG 3.6
- [ ] Heavy components are dynamically imported (loaded on interaction) — WSG 3.6
- [ ] No jQuery if only used for DOM selection and events — WSG 3.23

## CSS

- [ ] Total CSS (compressed/transferred) is <70 KB (stretch: <30 KB) — WSG 3.2
- [ ] CSS is minified in production — WSG 3.2
- [ ] Unused CSS is identified and removed (Chrome Coverage tab) — WSG 3.6
- [ ] Critical CSS is inlined in `<head>` (<14 KB); remaining CSS loaded asynchronously — WSG 3.2
- [ ] CSS methodology (BEM or similar) is used to prevent duplication — WSG 3.6
- [ ] `content-visibility: auto` is used for long off-screen sections — WSG 3.2
- [ ] CSS solutions are preferred over JavaScript (animations, toggles, accordions) — WSG 3.23
- [ ] Dark mode is supported via `prefers-color-scheme` media query — WSG 2.15

## HTML

- [ ] HTML is minified in production — WSG 3.2
- [ ] Semantic HTML elements are used (`<nav>`, `<main>`, `<article>`, `<section>`, `<header>`, `<footer>`) — WSG 3.5
- [ ] Required meta elements are present (`<!DOCTYPE>`, `<html lang>`, `<meta charset>`, `<title>`, `<meta viewport>`) — WSG 3.12
- [ ] Open Graph and description meta tags are present and valid — WSG 3.12
- [ ] Structured data (schema.org) is used where applicable — WSG 3.12
- [ ] Heading hierarchy is correct (single `<h1>`, no skipped levels) — WSG 3.5
- [ ] Forms use `<label>`, `<fieldset>`, `<legend>` properly — WSG 3.5
- [ ] `autocomplete` attributes are used on personal data form fields — WSG 3.5

## Caching

- [ ] Static assets (CSS, JS, fonts with hash) have `Cache-Control: public, immutable, max-age=31536000` — WSG 4.2
- [ ] HTML pages use `Cache-Control: no-cache` with `ETag` for conditional requests — WSG 4.2
- [ ] Images use `Cache-Control: public, max-age=2592000` (30 days) — WSG 4.2
- [ ] A service worker is registered for offline access to key pages — WSG 4.2
- [ ] Server-side caching is configured (Varnish, page cache, or static site generation) — WSG 4.2
- [ ] Back-forward cache (bfcache) compatibility is maintained (no `Cache-Control: no-store` on HTML) — WSG 4.2

## Compression

- [ ] Brotli compression is enabled on the server for text-based assets — WSG 4.3
- [ ] GZIP is configured as a fallback for clients that don't support Brotli — WSG 4.3
- [ ] Response headers include `Content-Encoding: br` or `Content-Encoding: gzip` — WSG 4.3
- [ ] SVG files are compressed server-side (Brotli/GZIP) — WSG 4.3
- [ ] Transferred size is significantly smaller than resource size (verify in DevTools Network tab) — WSG 4.3

## Third-Party

- [ ] Total third-party domains are <4 (stretch: <2) — WSG 3.7
- [ ] Total third-party requests are <10 (stretch: <5) — WSG 3.7
- [ ] Third-party content (maps, videos, chat, social embeds) uses click-to-load facades — WSG 3.7
- [ ] Analytics uses a lightweight, self-hosted alternative (Plausible, Fathom, Umami) or minimal script — WSG 3.7
- [ ] Google Fonts are self-hosted as subsetted WOFF2 files — WSG 3.7
- [ ] No unused third-party scripts (tag managers, A/B testing, etc.) are loaded — WSG 3.7
- [ ] Users can disable non-essential third-party services — WSG 3.7
- [ ] Cookie consent is implemented without dark patterns — WSG 2.11

## Performance

- [ ] Total page weight (transferred) is <1.5 MB (stretch: <500 KB) — WSG 3.1
- [ ] Total HTTP requests are <30 (stretch: <15) — WSG 3.24
- [ ] Largest Contentful Paint (LCP) is <2.5 seconds on 4G — WSG 3.1
- [ ] Cumulative Layout Shift (CLS) is <0.1 — WSG 3.1
- [ ] Total Blocking Time (TBT) is <200ms — WSG 3.1
- [ ] Page is functional on 3G connection (1.6 Mbps) — WSG 2.29
- [ ] Page is usable on devices 5+ years old (4x CPU slowdown simulation) — WSG 2.29
- [ ] Lighthouse Performance score is >90 — WSG 3.1

## Hosting

- [ ] Hosting provider uses 100% renewable energy (verify via Green Web Foundation) — WSG 4.1
- [ ] Server is geolocated near the primary audience — WSG 4.1
- [ ] CDN is used for static asset delivery — WSG 4.1
- [ ] Infrastructure is right-sized (not over-provisioned) — WSG 4.11
- [ ] HTTPS is enforced with HTTP/2 or HTTP/3 — WSG 4.1
- [ ] Automated deployment and CI/CD pipelines are in place — WSG 4.6
- [ ] Security measures (firewall, bot blocking) are active to reduce malicious traffic — WSG 4.6
- [ ] Unused data, old content, and redundant assets are regularly cleaned up — WSG 4.12

## Accessibility (Sustainability Intersection)

- [ ] WCAG 2.1 AA compliance is maintained — WSG 3.5
- [ ] Accessibility is never sacrificed for sustainability optimizations — WSG 3.5
- [ ] Color contrast meets minimum ratios (4.5:1 normal text, 3:1 large text) — WSG 3.5
- [ ] Dark mode does not reduce contrast below WCAG thresholds — WSG 3.5
- [ ] Lazy-loaded content remains accessible to screen readers — WSG 3.5
- [ ] Facades (video, map) provide accessible labels and keyboard support — WSG 3.5
- [ ] All interactive elements are keyboard-accessible — WSG 3.5
- [ ] `prefers-reduced-motion` does not remove essential information — WSG 2.17, 3.5
