# Third-Party Scripts — Interaction-First Loading

Audit and refactor every third-party embed in this project to load only after explicit user interaction. Replace heavy iframes and auto-loading scripts with lightweight facades. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Facade Pattern — Core Approach

Third-party embeds (video players, maps, booking widgets, social feeds) routinely add 500 KB–2 MB of script, style, and network requests on page load — before the user has expressed any intent to use them. The facade pattern defers all of that cost until the first interaction.

**How it works:**

1. Render a static placeholder (screenshot, poster image, or styled button) in place of the embed
2. Show a clear call-to-action that communicates what will load
3. On first click: inject the real embed, load its scripts, and hand off to the provider's player or widget
4. The user waits ~1–2 seconds on click, but the page loads instantly for everyone

**Universal rules:**

- No third-party `<script>` tags in `<head>` or body unless required for core page function (analytics, consent management)
- No third-party `<iframe>` that loads on page paint — every iframe must be deferred or replaced
- No `<link rel="preconnect">` to third-party origins unless a facade is already loaded and the connection will be used within 3 seconds
- Every facade must be keyboard-accessible and communicate its purpose to screen readers

### 1.1 Generic Vanilla JS Facade Loader

Use this as the base for any embed not covered by a dedicated section below:

```js
// src/lib/facade-loader.js

/**
 * Replace a facade placeholder with a real embed on first click.
 */
export function initFacade(container, buildEmbed, onLoad) {
  const trigger = container.querySelector('[data-facade-trigger]') ?? container;

  trigger.addEventListener('click', function handler() {
    trigger.removeEventListener('click', handler);
    container.innerHTML = buildEmbed();
    onLoad?.();
  }, { once: true });
}
```

---

## 2. Video Embeds — YouTube and Vimeo

YouTube iframes load ~1.2 MB of JavaScript on page paint. Vimeo loads ~400 KB. Both can be replaced with a static poster image and a play button that triggers the real player only on click.

### 2.1 YouTube Facade

```svelte
<!-- src/components/YouTubeFacade.svelte -->
<script>
  let { videoId, title = 'Play video', params = 'autoplay=1&rel=0' } = $props();

  let active = $state(false);
  const poster = `https://i.ytimg.com/vi/${videoId}/maxresdefault.jpg`;
</script>

{#if active}
  <iframe
    src="https://www.youtube-nocookie.com/embed/{videoId}?{params}"
    {title}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
    loading="lazy"
  ></iframe>
{:else}
  <div
    class="facade"
    role="button"
    tabindex="0"
    aria-label={title}
    style:background-image="url('{poster}')"
    onclick={() => active = true}
    onkeydown={e => (e.key === 'Enter' || e.key === ' ') && (active = true)}
  >
    <span class="facade__play" aria-hidden="true">
      <svg width="68" height="48" viewBox="0 0 68 48">
        <path d="M66.5 7.7c-.8-2.9-3-5.2-5.8-6C55.8 0 34 0 34 0S12.2 0 7.3 1.6c-2.8.8-5 3.1-5.8 6C0 12.6 0 24 0 24s0 11.4 1.5 16.3c.8 2.9 3 5.2 5.8 6C12.2 48 34 48 34 48s21.8 0 26.7-1.6c2.8-.8 5-3.1 5.8-6C68 35.4 68 24 68 24S68 12.6 66.5 7.7z" fill="#f00"/>
        <path d="M45 24 27 14v20" fill="#fff"/>
      </svg>
    </span>
  </div>
{/if}
```

**Usage:** `<YouTubeFacade videoId="dQw4w9WgXcQ" title="Watch: Product Demo" />`

### 2.2 Vimeo Facade

```svelte
<!-- src/components/VimeoFacade.svelte -->
<script>
  let { videoId, title = 'Play video', params = 'autoplay=1' } = $props();

  let active  = $state(false);
  let poster  = $state(`https://vumbnail.com/${videoId}.jpg`);
</script>

{#if active}
  <iframe
    src="https://player.vimeo.com/video/{videoId}?{params}"
    {title}
    allow="autoplay; fullscreen; picture-in-picture"
    allowfullscreen
    loading="lazy"
  ></iframe>
{:else}
  <div
    class="facade"
    role="button"
    tabindex="0"
    aria-label={title}
    style:background-image="url('{poster}')"
    onclick={() => active = true}
    onkeydown={e => (e.key === 'Enter' || e.key === ' ') && (active = true)}
  >
    <span class="facade__play" aria-hidden="true">▶</span>
  </div>
{/if}
```

---

## 3. Maps — Static Image Replacement

Google Maps iframes load 1–2 MB of JavaScript, fonts, and tiles on page paint.

**Rule:** Replace every Google Maps `<iframe>` with a static image and an "Open map" link. Only offer an interactive embedded map if the use case genuinely requires it.

```svelte
<!-- src/components/MapFacade.svelte -->
<script>
  let { staticImage = '', mapsUrl = '', label = 'View location on Google Maps', lat, lng, zoom = 15 } = $props();
  const mapLink = mapsUrl || `https://www.google.com/maps?q=${lat},${lng}&z=${zoom}`;
</script>

<div class="map-facade">
  {#if staticImage}
    <img src={staticImage} alt="Map showing location" loading="lazy" decoding="async" />
  {/if}
  <a href={mapLink} target="_blank" rel="noopener noreferrer" class="map-facade__btn" aria-label={label}>
    Open map
  </a>
</div>
```

---

## 4. Calendly and Booking Widgets

Calendly's embed script loads ~900 KB. Default to a direct link. Only use the inline widget if users must book without leaving the page.

```svelte
<!-- Default: link, no JS ever loads -->
<a href="https://calendly.com/yourname/30min" target="_blank" rel="noopener noreferrer">
  Book a 30-minute call
</a>
```

---

## 5. Social Feeds and Embeds

| Embed type | Replacement |
|---|---|
| Twitter/X timeline widget | Static screenshot of recent posts + link to profile |
| Instagram feed widget | CSS grid of `<img>` tags (pre-fetched at build) + link |
| Facebook page widget | Plain link with page name |
| LinkedIn share button | Plain `<a>` with manually constructed share URL |
| Twitter/X share button | Plain `<a>` with `https://twitter.com/intent/tweet?text=...` |
| Any `<blockquote>` + platform `<script>` | Remove the `<script>`; manually style the `<blockquote>` |

**Removing platform widget scripts:**
```html
<!-- Before: pulls in twitter-widgets.js (~350 KB) -->
<blockquote class="twitter-tweet"><p>Tweet text…</p></blockquote>
<script async src="https://platform.twitter.com/widgets.js"></script>

<!-- After: remove the <script>, style the <blockquote> natively -->
<blockquote class="social-quote">
  <p>Tweet text…</p>
  <footer><a href="https://twitter.com/user/status/123" target="_blank" rel="noopener noreferrer">@user on Twitter/X →</a></footer>
</blockquote>
```

---

## 6. Audit, Detection, and CI

### Audit Script — Find Third-Party Iframes and Scripts

```js
// scripts/audit-third-party.js
import { readdirSync, readFileSync, statSync } from 'fs';
import { join, extname } from 'path';

const SRC = './src';

const BLOCKED_ORIGINS = [
  'youtube.com', 'youtu.be', 'vimeo.com', 'spotify.com',
  'google.com/maps', 'maps.googleapis.com', 'calendly.com',
  'twitter.com/widgets', 'platform.twitter.com',
  'instagram.com/embed', 'facebook.com/plugins',
  'connect.facebook.net', 'assets.calendly.com',
];

const IFRAME_RE = /<iframe\s[^>]*src=["']([^"']+)["']/gi;
const SCRIPT_RE = /<script\s[^>]*src=["']([^"']+)["']/gi;

function walk(dir) {
  return readdirSync(dir).flatMap(f => {
    const full = join(dir, f);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

const EXTS = new Set(['.html', '.svelte', '.vue', '.jsx', '.tsx', '.php', '.twig']);
const files = walk(SRC).filter(f => EXTS.has(extname(f)));
let issues = 0;

for (const file of files) {
  const content = readFileSync(file, 'utf8');
  for (const [re, type] of [[IFRAME_RE, 'iframe'], [SCRIPT_RE, 'script']]) {
    let m;
    while ((m = re.exec(content)) !== null) {
      const blocked = BLOCKED_ORIGINS.find(o => m[1].includes(o));
      if (blocked) {
        console.error(`❌ Direct third-party ${type} (${blocked}): ${file}`);
        issues++;
      }
    }
  }
}

if (issues === 0) {
  console.log(`✅ No direct third-party iframes or blocked scripts found.`);
} else {
  console.error(`\n${issues} issue(s) found. Replace with facades before deploying.`);
  process.exit(1);
}
```

Add to `package.json`:
```json
{ "scripts": { "audit:third-party": "node scripts/audit-third-party.js" } }
```

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied

List every file created or modified — iframes replaced with facade components, platform `<script>` tags removed, social share links added, static map images committed.

### ⚠️ Manual Actions Required

List items requiring human action — static map screenshots to capture, Vimeo poster images to fetch at build time, social feed content to snapshot before removing the embed.

### Current Third-Party Status

| Embed | Pages affected | Status | Weight saved |
|---|---|---|---|
| YouTube iframes | X | Replaced / Remaining | ~1,200 KB each |
| Vimeo iframes | X | Replaced / Remaining | ~400 KB each |
| Google Maps iframes | X | Replaced / Remaining | ~1,500 KB each |
| Calendly widget | X | Link / Inline / Remaining | ~900 KB |
| Social embed scripts | X | Replaced / Remaining | ~X KB each |

### Estimated Impact

- Total third-party weight removed from page load: ~X KB (~X MB)
- Third-party network requests eliminated on page paint: X
- CI gate added: direct third-party iframe/script audit on every PR
