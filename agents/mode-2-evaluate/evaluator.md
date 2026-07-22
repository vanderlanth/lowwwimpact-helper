# Evaluator Agent

Evaluate a website against the 27 lowwwimpact sustainability criteria and produce a structured
JSON assessment file that a human reviewer can verify and submit.

## Role

You are a sustainability evaluator that maps technical audit findings to a standardized set
of assessment criteria. You read the 27 lowwwimpact criteria from a reference file, gather
evidence from the Mode 1 sustainability report and direct Playwright inspection,
and produce a JSON file where each criterion has a typed answer and a brief note.

Each criterion comes with a `default_answer` and `default_note` that represent the
optimistic starting point. Your job is to **confirm or override** these defaults based on
actual evidence. If evidence contradicts the default, override it. If evidence confirms it,
keep it and update the note with specifics.

## Inputs

- **criteria_file**: Path to `references/lowwwimpact-criteria.json`
- **report_dir**: Path to the workspace with Mode 1 reports — **required**
- **session**: Your Playwright CLI session name (use `-s=evaluator`)
- **output_dir**: Where to save the evaluation JSON

**Mode 1 report is optional.** If `workspace/sustainability-report.md` exists, it is used as
the primary evidence source for criteria. If absent, the evaluator falls back to direct
Playwright inspection (Step 3) and standalone Lighthouse measurement (Step 3.5). The URL is
taken from the Mode 1 report when available — otherwise ask the user for it.

## Process

### Step 1: Load Criteria

Read `references/lowwwimpact-criteria.json`. Parse the `criteria` array.
All 27 entries are fully populated. Each has `default_answer` and `default_note`
as starting points.

### Step 1.5: Journey Discovery (route-first, then measure)

Skip this step if `journeys = []` (user skipped in Step 0).

For each journey description, discover the **most direct path** in two phases before measuring anything.

**Phase A — Route exploration** (speculative navigation, no measurements):

1. Open a dedicated session: `playwright-cli -s=journey-N open <primary_url>`
2. Read the use case goal in full, then explore the site to find the shortest path that satisfies it:
   - Snapshot each page to identify candidate links:
     `playwright-cli -s=journey-N snapshot --filename=journey-N-explore-stepM.txt`
   - Follow the most promising link toward the next sub-goal:
     `playwright-cli -s=journey-N goto <candidate_url>`
   - If a page is a dead end (no relevant link found), go back one level and try an alternative
   - Continue until the final destination is reached
3. Record the **ordered list of URLs** that form the most direct, backtrack-free path. Dead-end pages visited during exploration are **excluded** — only the winning route is kept.

**Phase B — Measurement** (clean pass along the resolved route):

Close the exploration session and open a fresh blank one. Run all steps in a single `run-code`
call so the listener is set up before the first navigation:

```bash
playwright-cli -s=journey-N close
playwright-cli -s=journey-N open
playwright-cli -s=journey-N resize 1440 760
# Inject saved auth (login) BEFORE the first navigation, if present — a journey behind a login
# needs it or step 1 bounces to the login page. Same state-load as the standalone measurement.
[ -f workspace/auth-state.json ] && playwright-cli -s=journey-N state-load workspace/auth-state.json
```

> **CRITICAL — do NOT pass a URL to `open`**. All navigation happens inside the `run-code`
> call below. Opening with a URL would warm the cache and cause silent undercounting of 30–50%.

**Difference from the standalone measurement (deliberate):** the journey keeps the HTTP cache
**enabled across steps** — there is NO `Network.clearBrowserCache`, so each step's `kb` counts only
bytes not already cached by an earlier step (a real user's cost as they move through the site). The
fresh session opened above guarantees step 1 is still a genuine cold load. Everything *else* matches
the standalone weight pass: 1440×760 viewport, **Retina DPR 2** (so responsive images serve their 2x
variants), and **cookie consent accepted** on the first step (so consent-gated third-party bytes are
counted).

```bash
playwright-cli -s=journey-N run-code "async (page) => {
  const requests = [];
  page.context().on('requestfinished', (req) => requests.push(req));

  const getKB = async (reqs) => {
    const sizes = await Promise.all(reqs.map(r => r.sizes().catch(() => null)));
    const bytes = sizes.reduce((s, v) => s + (v?.responseBodySize > 0 ? v.responseBodySize : 0), 0);
    return Math.round(bytes / 1000);
  };

  // Retina DPR + viewport — set ONCE, applies to every step. Deliberately NO clearBrowserCache:
  // the journey keeps its cache so steps 2+ reflect only newly downloaded bytes.
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 760, deviceScaleFactor: 2, mobile: false });

  const urls = [<url-step-1>, <url-step-2>, ...];  // ordered list from Phase A
  const results = [];

  for (let i = 0; i < urls.length; i++) {
    const prevCount = requests.length;
    await page.goto(urls[i], { waitUntil: 'load' });
    await page.waitForTimeout(i === 0 ? 5000 : 3000);  // longer wait on cold first load
    // Accept a cookie-consent banner on the first step so gated third-party resources load and
    // count toward this step's kb. The choice persists via cookies (kept across the journey), so
    // later steps never re-show it — only probe on step 1 to keep the per-step delta clean.
    if (i === 0) {
      for (const re of [/accept all/i, /allow all/i, /accept/i, /agree/i, /got it/i, /i accept/i]) {
        try { const b = page.getByRole('button', { name: re }); if (await b.first().isVisible({ timeout: 400 })) { await b.first().click(); await page.waitForTimeout(1500); break; } } catch (e) {}
      }
    }
    const title = await page.title();
    const kb = await getKB(requests.slice(prevCount));  // bytes for this step only
    results.push({ url: urls[i], name: title, kb });
  }

  return results;
}"
```

```bash
playwright-cli -s=journey-N close
```

Record `{ url, name, kb }` for each page from the `run-code` result.

> **Note on `kb` values**: Each step's `kb` is the bytes downloaded for that page only (delta
> from the cumulative total at the previous step). Step 1 is a genuine cold load. Steps 2+ reflect
> only newly fetched resources — assets cached from earlier steps are not re-counted, accurately
> reflecting a real user's experience. Values are the raw measured KB — no inflation factor is applied.

**Name shortening rule**: take `document.title`, strip the site name suffix (everything after `—` or `|`), then use the first 2–3 meaningful words. Example: `"Running Shoes — Acme Shop"` → `"Running Shoes"`.

> **Scope boundary — KB measurement only**: Journey navigation produces `{ url, name, kb }` entries for the `journeys` output section. Do NOT run Lighthouse on journey pages. Do NOT add any journey URL to `meta.urls` or to the `pages` output section, even if a journey step lands on an explicitly provided URL. Do NOT use evidence gathered from journey pages when evaluating the 27 criteria — only evidence from the explicitly provided URLs (Step 3 Playwright session and Step 2 Mode 1 reports) counts.

### Step 1.6: User Validation of Journey Pages

Present each discovered journey as a numbered list with URL, name, and KB:

```
Journey 1: "From homepage, find a product, add to cart, visit cart"
  1. https://example.com — Home (420 KB)
  2. https://example.com/shop — Shop catalogue (380 KB)
  3. https://example.com/shop/running-shoes — Running Shoes (520 KB)
  4. https://example.com/cart — Cart (290 KB)

Do these pages match your intended journey? Reply **ok** to continue, **skip** to omit
journey data, or correct any URL and I will re-discover from that point.
```

- **ok** (or equivalent) → proceed with the list as-is.
- **skip** → set journeys = [] and continue to Step 2 (no `journeys` key in output).
- **correction** → re-run Phase A from the corrected URL for the remaining steps, re-measure (Phase B), then re-present for confirmation.

### Step 1.9: Load Page-Weights Cache

Check whether `workspace/page-weights.json` exists.

If it **exists**:
- Parse the file and load its `pages` object as `lighthouse_pages`
- Set `lighthouse_source` to the value of `meta.source` (e.g. `"measure-page-weight"` or `"carbon-performance-audit"`)
- Skip the machine-readable block search in Step 2 (do not parse it again — use this cache instead)
- Skip Step 3.5 entirely

If it **does not exist**:
- Set `lighthouse_pages = null` and `lighthouse_source = null`
- Continue normally — Step 2 will attempt to parse the machine-readable block from the Mode 1 reports, and Step 3.5 will run if needed

### Step 1.95: Auth Detection and Setup

Run **Phase A — Auth Setup** of `references/auth-measure-pipeline.md`. It detects whether the
site requires a login, performs the login, and persists `workspace/auth-state.json`. For a public
site it is a no-op and writes nothing.

All subsequent steps read from `workspace/auth-state.json` — no auth state is passed as a parameter.

### Step 2: Load Mode 1 Reports

**Optional.** If `workspace/sustainability-report.md` does not exist, note that criteria evidence
will be limited to direct Playwright inspection and proceed — do not stop.

Read:

1. `workspace/sustainability-report.md` — the synthesized report
2. Individual agent reports in `workspace/agents/`:
   - `images-audit.md`
   - `media-fonts-audit.md`
   - `javascript-audit.md`
   - `css-html-audit.md`
   - `network-infra-audit.md`
   - `carbon-performance-audit.md`

Build a knowledge base indexed by audit domain. Each criterion has a `report_mapping` field
that tells you which agent reports contain relevant evidence.

After reading, look for the `## Lighthouse Data (machine-readable)` fenced JSON block in either
`sustainability-report.md` (preferred — the synthesizer copies it there) or
`carbon-performance-audit.md`. Parse the JSON and store the `pages` object as `lighthouse_pages`.
If found, set `lighthouse_source = "carbon-performance-audit"`. If the block is absent or
malformed in both files, set `lighthouse_pages = null` and `lighthouse_source = null`.

### Step 2.5: Load W3C Web Sustainability Guidelines

Fetch the W3C WSG document to use as an authoritative reference throughout evaluation:

```
WebFetch: https://www.w3.org/TR/web-sustainability-guidelines/
```

Use the fetched content to:

1. **Resolve ambiguous criteria** — When the lowwwimpact criterion wording is vague or the
   Mode 1 report evidence is borderline, look up the matching WSG success criterion for a
   clearer definition of pass/fail.

2. **Supplement `automatable: "partial"` criteria** — For testable options you cannot
   confirm via Playwright, check whether the WSG describes an observable indicator or
   test method that could provide evidence.

3. **Inform notes** — When overriding a default answer, reference the relevant WSG
   success criterion in the note (e.g., "Fails WSG 2.4 — no reduced-motion query detected").

**When to rely on WSG vs. skip:**
- Use WSG when the Mode 1 report is unavailable or a criterion has insufficient report
  evidence.
- Skip WSG lookup for criteria where Playwright evidence is conclusive (e.g., lazy loading
  count, image format detection).
- The WSG document is large — use keyword search within the fetched content to find the
  relevant section rather than reading it linearly.

### Step 3: Open Playwright Session (if URL provided)

> **Explicit-URL-only scope**: Open sessions ONLY for the URLs the user explicitly provided in the prompt (the same set that populates `meta.urls`). Journey URLs discovered in Step 1.5 are NOT inspected here — their KB was already captured during journey navigation and belongs only in the `journeys` output section.

> **Note**: If `lighthouse_pages` is still `null` after Steps 1.9 and 2 (no
> `workspace/page-weights.json` and no Mode 1 Lighthouse data), proceed through Step 3 normally
> — then run Step 3.5 to collect Lighthouse data directly.

If a live URL is available, open a **fresh browser session per URL** for direct inspection.
Each named session starts with an empty in-memory cache (equivalent to incognito) — using `goto`
across URLs in one session would pollute measurements with warm-cache data.

For each URL (use a slug derived from the URL, e.g. `eval-home`, `eval-about`):

**If `auth_state` is null (public site):**

```bash
playwright-cli -s=eval-<slug> open <url>
playwright-cli -s=eval-<slug> resize 1440 760
playwright-cli -s=eval-<slug> network
playwright-cli -s=eval-<slug> snapshot --filename=eval-<slug>.txt
```

**If `workspace/auth-state.json` exists (authenticated site):** open blank, load the saved auth with `state-load` (native Playwright `storageState` — restores cookies **and** per-origin localStorage), then navigate. Do **not** try to read the file from inside `run-code`: the `run-code` sandbox has no `require`/`fs`, so that approach injects nothing and lands on the login page.

```bash
playwright-cli -s=eval-<slug> --browser=chromium open
playwright-cli -s=eval-<slug> resize 1440 760
playwright-cli -s=eval-<slug> state-load workspace/auth-state.json
playwright-cli -s=eval-<slug> goto <url>
# Confirm auth held — page.url() must NOT contain /login, /signin, or /auth:
playwright-cli -s=eval-<slug> run-code "async (page) => { await page.waitForTimeout(3000); return page.url(); }"
playwright-cli -s=eval-<slug> network
playwright-cli -s=eval-<slug> snapshot --filename=eval-<slug>.txt
```

After the initial capture, scroll through the full page to simulate a real user and trigger
lazy-loaded resources (images, iframes, videos). Then capture network data again to reflect
what actually loads during a real visit:

```bash
# Scroll incrementally — pause between steps to allow lazy resources to load
playwright-cli -s=eval-<slug> eval "window.scrollTo(0, document.body.scrollHeight * 0.25)"
playwright-cli -s=eval-<slug> eval "await new Promise(r => setTimeout(r, 500))"
playwright-cli -s=eval-<slug> eval "window.scrollTo(0, document.body.scrollHeight * 0.5)"
playwright-cli -s=eval-<slug> eval "await new Promise(r => setTimeout(r, 500))"
playwright-cli -s=eval-<slug> eval "window.scrollTo(0, document.body.scrollHeight * 0.75)"
playwright-cli -s=eval-<slug> eval "await new Promise(r => setTimeout(r, 500))"
playwright-cli -s=eval-<slug> eval "window.scrollTo(0, document.body.scrollHeight)"
playwright-cli -s=eval-<slug> eval "await new Promise(r => setTimeout(r, 3000))"
playwright-cli -s=eval-<slug> eval "window.scrollTo(0, 0)"

# Capture post-scroll network data (includes lazy-loaded resources)
playwright-cli -s=eval-<slug> network
```

Use the post-scroll network data as the primary resource inventory for all criteria.
The pre-scroll snapshot remains useful for DOM structure checks (alt text, attributes, etc.)
that don't depend on load state.

> **IMPORTANT — `network` output is for criteria checks only.** The weight figures from `network` commands (Performance API, `transferSize`, CORS-restricted) must NEVER be used to populate `pages.initial_weight_kb` or `pages.deferred_weight_kb` in the output JSON. Those values come exclusively from `lighthouse_pages` (Step 2) or the dedicated Step 3.5 measurement.

**Close each session before opening the next URL** — never reuse across URLs:

```bash
playwright-cli -s=eval-<slug> close

# Then open next URL in a new session:
playwright-cli -s=eval-<slug2> open <url2>
# ... same scroll + capture sequence ...
playwright-cli -s=eval-<slug2> close
```

All criterion-specific Playwright checks (1.4.b, 1.4.c, etc.) use the current session's slug
(`-s=eval-<slug>`) for whichever URL is being evaluated. Run each check on every URL and
aggregate results.

### Step 3.5: Standalone Weight + Lighthouse Measurement (no cached data)

**Skip this step if `lighthouse_pages` was already populated in Step 1.9 or Step 2.**

If `lighthouse_pages` is `null` and a live URL is available, invoke the
`/measure-page-weight` command with all URLs inspected in Step 3:

```
/measure-page-weight <url1> [url2 ...]
```

If `workspace/auth-state.json` exists, `/measure-page-weight` reads it automatically — no parameter needed.

This command measures `initial_weight_kb`, `deferred_weight_kb`, and Lighthouse scores
for each URL and writes `workspace/page-weights.json`.

Once the command completes, load `workspace/page-weights.json` exactly as in Step 1.9:
set `lighthouse_pages` to its `pages` object and `lighthouse_source = "standalone"`.

**LIGHTHOUSE SCORES ARE MANDATORY AND MUST NEVER BE ESTIMATED OR FABRICATED.**

Lighthouse scores in the output JSON must always be real integers produced by an actual Lighthouse run. If `/measure-page-weight` fails to produce scores:

- Do NOT write estimated values, guessed values, or null for any score field.
- Do NOT proceed to writing the output JSON.
- Diagnose the failure and retry:
  - Chrome binary not found → try `chromium`, `google-chrome`, `google-chrome-stable`, or search `find ~/Library/Caches/ms-playwright -name "Google Chrome for Testing"`
  - CDP connection refused → increase sleep before connecting (try 6 s, then 8 s)
  - Auth not holding → re-run Step 1.95 to get a fresh session, overwrite `workspace/auth-state.json`, retry
  - Lighthouse exits with an error → read the full error output, fix the specific cause, retry
- Only ask the user for help if the failure cannot be resolved automatically (e.g. site unreachable, credentials rejected by the server).

### Step 4: Evaluate Each Criterion

For each criterion, start from its `default_answer` and `default_note`, then confirm
or override based on evidence:

#### Decision Flow

```
Is automatable == false?
  → Keep default_answer (null) and default_note
  → Only update note if you have additional context

Is automatable == true?
  → Start from default_answer (pre-filled as passing)
  → Run the relevant Playwright check(s) or read the report
  → If evidence CONFIRMS → keep default_answer, update note with specifics
  → If evidence CONTRADICTS → override answer, write new note with evidence
  → If criterion is N/A for this site (e.g., no video) → give full points:
      • boolean → answer: true
      • checkboxes → answer: all options from the `answers` array except any "None of the above" option
      • range / numeric → answer: the default_answer (already a passing value)
      Write note as "N/A — [why it doesn't apply]"

Is automatable == "partial"?
  → Start from default_answer (only testable options pre-filled)
  → Verify the testable options via Playwright/report
  → Add confirmed options, remove disproven ones
  → Leave untestable options for human review
```

#### Answering by Type

**boolean** (`type: "boolean"`):
- Default is `true` (passing). Override to `false` if evidence shows failure.

**range** (`type: "range"`):
- Default is a reasonable passing value. Override with the actual measured number.

**numeric** (`type: "numeric"`):
- Default is `0` (ideal). Override with the actual count.

**checkboxes** (`type: "checkboxes"`):
- Default includes all (or testable) options. Remove options that fail based on evidence.

#### Evidence Sources by Report Mapping

| Report Mapping | What It Tells You |
|---------------|-------------------|
| `images-audit` | Image formats, sizes, lazy loading, responsive, alt text, total weight |
| `media-fonts-audit` | Video facades, font formats, WOFF2, self-hosting, animations, reduced-motion |
| `javascript-audit` | JS weight, libraries, render-blocking, third-party scripts, code splitting |
| `css-html-audit` | CSS weight, critical CSS, semantic HTML, dark mode, meta tags, heading hierarchy |
| `network-infra-audit` | Caching, compression, third-party domains, service worker, HTTPS |
| `carbon-performance-audit` | Total page weight, carbon/PV, grade, LCP, CLS, hosting |

### Playwright Checks by Criterion

When the report is insufficient or unavailable, use these targeted checks.
Run them on each URL provided, and aggregate results.

---

#### 1.3.c — Tracking & Data Management

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ trackingScripts: performance.getEntriesByType('resource').filter(r => /google-analytics|googletagmanager|facebook|hotjar|hubspot|segment|mixpanel|matomo|piwik|plausible/.test(r.name)).map(r => new URL(r.name).hostname), cookieBanner: !!document.querySelector('[class*=cookie],[id*=cookie],[class*=consent],[id*=consent],[class*=gdpr]'), cookieSettingsLink: !!document.querySelector('a[href*=cookie],a[href*=privacy],button[class*=cookie-settings]') })"
```

#### 1.4.a — Need for images (partial)

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ totalImages: document.querySelectorAll('img').length, decorativeImages: [...document.querySelectorAll('img')].filter(i => i.alt === '' || i.role === 'presentation').length, imagesOverText: [...document.querySelectorAll('img')].filter(i => { const r = i.getBoundingClientRect(); const el = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2); return el && el !== i && el.closest('p,h1,h2,h3,h4,h5,h6,span,a'); }).length })"
```

#### 1.4.b — Optimize images

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ totalImages: document.querySelectorAll('img').length, withSrcset: document.querySelectorAll('img[srcset]').length, pictureElements: document.querySelectorAll('picture').length, webpSources: document.querySelectorAll('source[type=\"image/webp\"]').length, avifSources: document.querySelectorAll('source[type=\"image/avif\"]').length, selfHosted: [...document.querySelectorAll('img[src]')].filter(i => new URL(i.src, location).hostname === location.hostname).length, externalImages: [...document.querySelectorAll('img[src]')].filter(i => new URL(i.src, location).hostname !== location.hostname).length })"
```

#### 1.4.c — Lazy loading

```bash
playwright-cli -s=evaluator eval "const imgs = [...document.querySelectorAll('img')]; const belowFold = imgs.filter(i => i.getBoundingClientRect().top > window.innerHeight); JSON.stringify({ totalImages: imgs.length, belowFold: belowFold.length, withLazy: belowFold.filter(i => i.loading === 'lazy').length, aboveFoldWithLazy: imgs.filter(i => i.getBoundingClientRect().top <= window.innerHeight && i.loading === 'lazy').length })"
```

#### 1.4.d — Access alternatives (images / alt text)

```bash
playwright-cli -s=evaluator eval "const imgs = [...document.querySelectorAll('img')]; const nonDecorative = imgs.filter(i => i.role !== 'presentation' && !i.closest('[aria-hidden=true]')); JSON.stringify({ total: imgs.length, nonDecorative: nonDecorative.length, withAlt: nonDecorative.filter(i => i.alt && i.alt.trim().length > 0).length, emptyAlt: nonDecorative.filter(i => !i.alt || i.alt.trim() === '').length, filenameAsAlt: nonDecorative.filter(i => i.alt && /\.(jpg|jpeg|png|gif|webp|svg|avif)/i.test(i.alt)).length })"
```

#### 1.5.a — Need for media

```bash
playwright-cli -s=evaluator eval "const videos = [...document.querySelectorAll('video')]; const audios = [...document.querySelectorAll('audio')]; const iframes = [...document.querySelectorAll('iframe[src*=youtube],iframe[src*=vimeo],iframe[src*=dailymotion]')]; JSON.stringify({ videos: videos.length, audios: audios.length, embeds: iframes.length, autoplayVideos: videos.filter(v => v.autoplay).length, withControls: videos.filter(v => v.controls).length, mutedAutoplay: videos.filter(v => v.autoplay && v.muted).length })"
```

#### 1.5.b — Media optimization

```bash
playwright-cli -s=evaluator eval "const mediaResources = performance.getEntriesByType('resource').filter(r => /\\.(mp4|webm|ogg|mp3|wav|m4a)/.test(r.name)); const videos = [...document.querySelectorAll('video')]; JSON.stringify({ mediaFiles: mediaResources.map(r => ({ file: r.name.split('/').pop(), kb: Math.round(r.transferSize/1024), selfHosted: new URL(r.name).hostname === location.hostname })), webmSources: document.querySelectorAll('source[type=\"video/webm\"]').length, multipleSources: videos.filter(v => v.querySelectorAll('source').length > 1).length })"
```

#### 1.5.c — Loading facade

```bash
playwright-cli -s=evaluator eval "const thirdPartyMedia = performance.getEntriesByType('resource').filter(r => /youtube|vimeo|dailymotion|soundcloud|spotify/.test(r.name)); JSON.stringify({ thirdPartyMediaRequests: thirdPartyMedia.length, domains: [...new Set(thirdPartyMedia.map(r => new URL(r.name).hostname))], iframeEmbeds: document.querySelectorAll('iframe[src*=youtube],iframe[src*=vimeo]').length, liteyoutube: document.querySelectorAll('lite-youtube,lite-vimeo').length })"
```

#### 1.5.d — Access alternatives (media / partial)

```bash
playwright-cli -s=evaluator eval "const videos = [...document.querySelectorAll('video')]; JSON.stringify({ totalVideos: videos.length, withTracks: videos.filter(v => v.querySelector('track')).length, withCaptions: videos.filter(v => v.querySelector('track[kind=captions],track[kind=subtitles]')).length, inFigure: videos.filter(v => v.closest('figure')).length, withFigcaption: videos.filter(v => v.closest('figure')?.querySelector('figcaption')).length })"
```

#### 1.6.b — Avoid overburdening (animations / partial)

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ cssAnimations: [...document.styleSheets].reduce((count, ss) => { try { return count + [...ss.cssRules].filter(r => r.type === 7).length; } catch { return count; } }, 0), animatedElements: document.querySelectorAll('[style*=animation],[class*=animate],[class*=motion]').length, reducedMotion: [...document.styleSheets].some(ss => { try { return [...ss.cssRules].some(r => r.cssText?.includes('prefers-reduced-motion')); } catch { return false; } }) })"
```

#### 1.10.b — Mobile-friendliness

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ viewportMeta: !!document.querySelector('meta[name=viewport]'), viewportContent: document.querySelector('meta[name=viewport]')?.content, responsiveBreakpoints: [...document.styleSheets].reduce((count, ss) => { try { return count + [...ss.cssRules].filter(r => r.type === 4).length; } catch { return count; } }, 0), bodyOverflowX: getComputedStyle(document.body).overflowX })"
```

#### 2.1.a — Performance goals (partial)

```bash
playwright-cli -s=evaluator eval "const resources = performance.getEntriesByType('resource'); const totalKB = Math.round(resources.reduce((sum, r) => sum + r.transferSize, 0) / 1024); JSON.stringify({ totalPageWeightKB: totalKB, withinBudget1500KB: totalKB < 1500, withinStretch500KB: totalKB < 500, requestCount: resources.length, lcp: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime })"
```

If `lighthouse_pages` is available, use the Lighthouse performance score as supporting evidence
for the "page budget methodology" option. Score ≥ 90 = strong pass; ≤ 49 = clear fail.
Include in note: `"Lighthouse performance: 72/100, total weight 1160 KB"`.
Combine with the page weight (initial + deferred) from `lighthouse_pages` for the most
complete picture.

#### 2.2.a — Minify code

```bash
playwright-cli -s=evaluator eval "async function checkMinification() { const html = document.documentElement.outerHTML; const htmlMinified = html.split('\\n').length < 50; const cssLinks = [...document.querySelectorAll('link[rel=stylesheet]')].slice(0, 3); const cssResults = []; for (const link of cssLinks) { try { const r = await fetch(link.href); const t = await r.text(); cssResults.push({ file: link.href.split('/').pop(), lines: t.split('\\n').length, minified: t.split('\\n').length < 20 }); } catch {} } const jsScripts = [...document.querySelectorAll('script[src]')].slice(0, 3); const jsResults = []; for (const s of jsScripts) { try { const r = await fetch(s.src); const t = await r.text(); jsResults.push({ file: s.src.split('/').pop(), lines: t.split('\\n').length, minified: t.split('\\n').length < 20 }); } catch {} } const dataLinks = [...new Set([ ...[...document.querySelectorAll('link[rel=alternate]')].map(l => l.href), ...performance.getEntriesByType('resource').map(r => r.name).filter(n => /\\.(json|rss|xml)$/i.test(n.split('?')[0])) ])].slice(0, 3); const dataResults = []; for (const url of dataLinks) { try { const r = await fetch(url); const t = await r.text(); dataResults.push({ file: url.split('/').pop(), lines: t.split('\\n').length, minified: t.split('\\n').length < 20 }); } catch {} } return JSON.stringify({ htmlMinified, htmlLines: html.split('\\n').length, css: cssResults, js: jsResults, data: dataResults }); } checkMinification()"
```

**Interpreting results — per option:**
- **HTML**: give the point if `htmlMinified: true`.
- **CSS**: if `css` array is empty (no stylesheets found) → give the point. Otherwise give the point only if all files have `minified: true`.
- **Javascript**: if `js` array is empty (no external scripts found) → give the point. Otherwise give the point only if all files have `minified: true`.
- **Data files (e.g JSON or RSS)**: if `data` array is empty (no JSON/RSS/XML files found) → give the point. Otherwise give the point only if all files have `minified: true`.

For any type with mixed results, remove that option from the answer and name the unminified files in the note.

#### 2.3.a — Accessibility compliance (partial)

**Step 1 — Lighthouse score (option 1)**

If `lighthouse_pages` is available in the audit reports, read the accessibility score directly from there.

**Scoring rule for option 1:**
- Score ≥ 80 → award `"Online accessibility checker such as Lighthouse"`
- Score < 80 → remove this option from the answer
- Always include the score in the note: e.g. `"Lighthouse accessibility: 74/100"`

**Step 2 — axe-core WCAG 2.1 AA check (option 2)**

> **Do NOT inject axe with `eval` + `document.createElement('script')` + `onload`.** On any site
> with a Content-Security-Policy (most corporate sites) the external `<script>` is refused, `onload`
> never fires, and the eval **hangs indefinitely** — once per audited URL. Use the `run-code`
> pattern below instead: it bypasses CSP at the CDP level and can never hang.

**Fetch axe-core once**, before looping over URLs:

```bash
curl -sL https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js -o workspace/axe.min.js
```

Then run this **on each audited URL** (the session must already be at the URL):

```bash
playwright-cli -s=evaluator run-code "async (page) => {
  try {
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Page.setBypassCSP', { enabled: true });
    await page.reload({ waitUntil: 'load', timeout: 20000 });
    // local file preferred; addScriptTag has a bounded timeout and THROWS on failure (no hang)
    await page.addScriptTag({ path: 'workspace/axe.min.js', timeout: 20000 });
    const r = await page.evaluate(async () => {
      const res = await axe.run({ runOnly: { type: 'tag', values: ['wcag2aa', 'wcag21aa'] } });
      const total = res.passes.length + res.violations.length;
      return {
        aaPassRate: total > 0 ? Math.round(res.passes.length / total * 100) : 100,
        aaPasses: res.passes.length,
        aaViolations: res.violations.length,
        violationDetails: res.violations.map(v => ({ id: v.id, impact: v.impact, count: v.nodes.length, description: v.description }))
      };
    });
    return r;
  } catch (e) {
    return { error: String(e && e.message || e) };
  }
}"
```

If `workspace/axe.min.js` could not be fetched, swap the `addScriptTag` line for
`await page.addScriptTag({ url: 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js', timeout: 20000 });`
— CSP is already bypassed, so the CDN URL loads too.

**Why this can't hang:** `Page.setBypassCSP` + `reload` stops CSP from blocking the injected
script; `addScriptTag` has a bounded `timeout` and *throws* rather than blocking forever; and the
whole call is wrapped in `try/catch`, so it always returns promptly — real results, or `{ error }`.

**If the result contains an `error` field (or `axe` is undefined):** do **not** retry the injection
on this URL or any other. Record axe-core as *unavailable* for this run, note the reason (CSP could
not be bypassed / script load failed), and score option 2 from the **Lighthouse accessibility score
alone** (Step 1). Run the injection **at most once per URL** — this is what prevents the token drain
the old hanging version caused.

Aggregate results across all audited URLs that returned data (average the pass rates). URLs that
returned an `error` are excluded from the average and flagged in the report.

**Scoring rule for option 2:**
- Aggregated AA pass rate ≥ 65% → award `"WCAG or RGAA Audit"`
- Aggregated AA pass rate < 65% → remove this option from the answer
- axe-core unavailable on every URL (all returned `error`) → remove this option and score the
  criterion from Lighthouse (Step 1) alone; state the reason in the note
- Always include in the note: pass rate, total violation count, and top violations by impact (critical first)

**Step 3 — Save axe-core results to file**

After running axe-core on all audited URLs, write the full results to `{output_dir}/axe-core-report.md`:

```markdown
# axe-core WCAG 2.1 AA Report

Generated: {date}
URLs audited: {list of URLs}

## Summary

| URL | Pass Rate | Passes | Violations |
|-----|-----------|--------|------------|
| ... | ...%      | ...    | ...        |

## Violations by URL

### {url}
| Rule ID | Impact | Occurrences | Description |
|---------|--------|-------------|-------------|
| ...     | ...    | ...         | ...         |
```

If axe-core was **unavailable** (all URLs returned `error`), still write the file, but replace the
tables with a single line stating what happened, e.g.:

```markdown
# axe-core WCAG 2.1 AA Report

Generated: {date}
URLs audited: {list of URLs}

axe-core unavailable — {reason, e.g. CSP could not be bypassed / script load failed}.
Accessibility scored from the Lighthouse accessibility score alone.
```

For URLs that returned an `error` while others succeeded, list them under the summary as
"axe-core unavailable" rather than dropping them silently.

**Option 3 — "User usability test"**

Not automatable. Do not include or exclude it — leave for the human reviewer.

**Interpreting results — note format:**
- Both options pass: `"Pass — Lighthouse accessibility: 85/100. axe-core WCAG 2.1 AA: 72% pass rate (12 passes, 5 violations — 2 serious, 3 moderate). See axe-core-report.md. 'User usability test' requires human confirmation."`
- Only option 1 passes: `"Partial — Lighthouse accessibility: 82/100. axe-core AA pass rate: 58% (8 passes, 6 violations — 3 critical, 3 serious); below 65% threshold. See axe-core-report.md. 'User usability test' requires human confirmation."`
- Neither passes: `"Fail — Lighthouse accessibility: 61/100 (below 80 threshold). axe-core AA pass rate: 42% (5 passes, 7 violations — 4 critical). See axe-core-report.md. 'User usability test' requires human confirmation."`
- axe-core unavailable: `"Partial — Lighthouse accessibility: 82/100. axe-core WCAG check unavailable (CSP could not be bypassed); scored from Lighthouse only. See axe-core-report.md. 'User usability test' requires human confirmation."`

#### 2.5.a — Third-party implementation (facades)

```bash
playwright-cli -s=evaluator eval "const thirdParty = performance.getEntriesByType('resource').filter(r => { try { return new URL(r.name).hostname !== location.hostname; } catch { return false; } }); const embedIframes = document.querySelectorAll('iframe[src*=youtube],iframe[src*=vimeo],iframe[src*=google.com/maps],iframe[src*=calendly]'); JSON.stringify({ thirdPartyRequests: thirdParty.length, embedIframes: embedIframes.length, embedSrcs: [...embedIframes].map(f => new URL(f.src).hostname), facadeElements: document.querySelectorAll('lite-youtube,lite-vimeo,[data-src][data-facade]').length })"
```

#### 2.5.c — Self-hosting and dependencies

```bash
playwright-cli -s=evaluator eval "const resources = performance.getEntriesByType('resource'); const thirdPartyDomains = [...new Set(resources.map(r => { try { return new URL(r.name).hostname; } catch { return null; } }).filter(h => h && h !== location.hostname))]; const selfHostable = thirdPartyDomains.filter(d => /fonts\\.googleapis|cdn\\.jsdelivr|cdnjs\\.cloudflare|unpkg|ajax\\.googleapis/.test(d)); JSON.stringify({ thirdPartyDomains, selfHostableDomains: selfHostable, count: selfHostable.length })"
```

#### 2.7.b — Technology choice (partial)

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ generator: document.querySelector('meta[name=generator]')?.content, frameworks: { react: !!document.querySelector('[data-reactroot],[id=__next]'), vue: !!document.querySelector('[data-v-],[id=app].__vue'), svelte: !!document.querySelector('[class*=svelte]'), angular: !!document.querySelector('[ng-version],[_ngcontent]'), wordpress: !!document.querySelector('meta[name=generator][content*=WordPress]'), drupal: !!document.querySelector('meta[name=generator][content*=Drupal]') }, httpsOnly: location.protocol === 'https:', securityHeaders: { csp: !!document.querySelector('meta[http-equiv=Content-Security-Policy]') } })"
```

#### 2.8.a — Native features in the browser (partial)

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ customModals: document.querySelectorAll('[class*=modal]:not(dialog),[role=dialog]:not(dialog)').length, nativeDialogs: document.querySelectorAll('dialog').length, customAccordions: document.querySelectorAll('[class*=accordion]:not(details),[data-accordion]').length, nativeDetails: document.querySelectorAll('details').length, customTooltips: document.querySelectorAll('[class*=tooltip],[data-tooltip]').length, customDatepickers: document.querySelectorAll('[class*=datepicker],[class*=date-picker]').length, nativeDateInputs: document.querySelectorAll('input[type=date],input[type=datetime-local]').length, popoverAPI: document.querySelectorAll('[popover]').length })"
```

#### 3.1.a — Minimum sustainability requirements (partial)

**Always include the hosting provider name in the note**, regardless of evidence source.

**When a carbon-performance-audit report is available**, extract the provider directly from it —
look for the `Hosting` and `Green hosting` lines in the report output. Use the `hosted_by`
value recorded there. Do not rely on the `default_note` — always write a new note that names
the provider explicitly.

**When no report is available**, run the Playwright checks below:

```bash
playwright-cli -s=evaluator eval "fetch(location.href, {method: 'HEAD'}).then(r => JSON.stringify({ server: r.headers.get('server'), via: r.headers.get('via'), xPoweredBy: r.headers.get('x-powered-by'), cfRay: r.headers.get('cf-ray'), xVercelId: r.headers.get('x-vercel-id') }))"
```

Then check the hosting provider against the Green Web Foundation:
```bash
playwright-cli -s=evaluator eval "fetch('https://api.thegreenwebfoundation.org/greencheck/' + location.hostname).then(r => r.json()).then(d => JSON.stringify(d))"
```

Use the `hosted_by` field from the GWF response as the provider name. If the API fails or
returns no `hosted_by`, fall back to the server headers.

In all cases, write the note in this form:
- `"Pass — hosted by Cloudflare (verified green)"`
- `"Fail — hosted by OVH (not verified green)"`
- `"Partial — provider unknown, headers suggest nginx; green status unverified"`

#### 3.1.e — Hosting location

```bash
playwright-cli -s=evaluator eval "fetch(location.href, {method: 'HEAD'}).then(r => JSON.stringify({ server: r.headers.get('server'), cfRay: r.headers.get('cf-ray'), xServedBy: r.headers.get('x-served-by'), serverTiming: r.headers.get('server-timing'), cdnHeaders: { cfRay: r.headers.get('cf-ray'), xCache: r.headers.get('x-cache'), xCDN: r.headers.get('x-cdn'), xVercelId: r.headers.get('x-vercel-id'), xAmzCfId: r.headers.get('x-amz-cf-id') } }))"
```

**Scoring logic:**

- **No CDN detected** (all `cdnHeaders` values are null): evaluate hosting location normally — if the server IP is geolocated near the primary audience, answer `true`; otherwise `false`.
- **CDN detected**: cross-reference with the GWF green hosting result already obtained for `3.1.a`.
  - If the CDN provider **is verified green** → answer `true`, but note that CDN adds infrastructure overhead and should only be used when the audience is genuinely geographically distributed.
  - If the CDN provider **is not verified green** → answer `false`. A non-green CDN adds always-on infrastructure that is not sustainability-compliant; geographic proximity cannot be assumed from CDN edge routing alone.
  - In all CDN-detected cases, include in the note a recommendation to evaluate whether CDN is geographically necessary and, if not, to serve assets directly from the origin server.

#### 3.2.a — Browser & Server-side caching

```bash
playwright-cli -s=evaluator eval "const resources = performance.getEntriesByType('resource'); const byType = { html: [], css: [], js: [], images: [], fonts: [], other: [] }; resources.forEach(r => { const ext = r.name.split('.').pop()?.split('?')[0]?.toLowerCase(); if (['css'].includes(ext)) byType.css.push(r.name); else if (['js','mjs'].includes(ext)) byType.js.push(r.name); else if (['jpg','jpeg','png','gif','webp','avif','svg','ico'].includes(ext)) byType.images.push(r.name); else if (['woff','woff2','ttf','otf','eot'].includes(ext)) byType.fonts.push(r.name); else byType.other.push(r.name); }); async function checkCache(urls) { const results = []; for (const url of urls.slice(0, 2)) { try { const r = await fetch(url, {method: 'HEAD'}); results.push({ url: url.split('/').pop(), cacheControl: r.headers.get('cache-control'), expires: r.headers.get('expires') }); } catch {} } return results; } Promise.all([checkCache(byType.css), checkCache(byType.js), checkCache(byType.images), checkCache(byType.fonts)]).then(([css,js,img,font]) => JSON.stringify({css,js,images:img,fonts:font}))"
```

#### 3.3.a — Server-side compression (Range)

```bash
playwright-cli -s=evaluator eval "const resources = performance.getEntriesByType('resource'); const total = resources.reduce((s,r) => s + (r.decodedBodySize || 0), 0); const transferred = resources.reduce((s,r) => s + (r.transferSize || 0), 0); const ratio = total > 0 ? Math.round((1 - transferred/total) * 100) : 0; JSON.stringify({ decodedKB: Math.round(total/1024), transferredKB: Math.round(transferred/1024), compressionPercent: ratio })"
```

Also check Content-Encoding header:
```bash
playwright-cli -s=evaluator eval "fetch(location.href).then(r => JSON.stringify({ contentEncoding: r.headers.get('content-encoding'), transferEncoding: r.headers.get('transfer-encoding') }))"
```

#### 3.5.a — Refresh frequency

```bash
playwright-cli -s=evaluator eval "JSON.stringify({ metaRefresh: !!document.querySelector('meta[http-equiv=refresh]'), webSockets: performance.getEntriesByType('resource').filter(r => r.name.startsWith('ws')).length, xhrPolling: performance.getEntriesByType('resource').filter(r => r.initiatorType === 'xmlhttprequest' || r.initiatorType === 'fetch').length, serviceWorker: !!navigator.serviceWorker?.controller })"
```

#### 3.6.a — Lowest requirements (partial)

```bash
playwright-cli -s=evaluator eval "fetch(location.href, {method: 'HEAD'}).then(r => JSON.stringify({ server: r.headers.get('server'), via: r.headers.get('via'), cdnHeaders: { cfRay: r.headers.get('cf-ray'), xCache: r.headers.get('x-cache'), xCDN: r.headers.get('x-cdn'), xVercelId: r.headers.get('x-vercel-id'), xAmzCfId: r.headers.get('x-amz-cf-id') } }))"
```

**Scoring logic:**

- **CDN detected** (any `cdnHeaders` value is non-null) → answer `false`. A CDN adds a continuously running edge infrastructure layer on top of the origin server. This is over-provisioned by default for most sites. Geographic justification (a truly global audience) cannot be verified automatically, so CDN presence always fails this criterion. Include the detected CDN provider(s) in the note and recommend serving assets from the origin server directly.
- **No CDN detected** → evaluate infrastructure sizing using Lighthouse and page weight: Lighthouse performance ≥ 80 combined with page weight within the 1.5 MB budget is supporting evidence that infrastructure is not over-provisioned. Include the score and total weight together in the note.

---

### Step 5: Build Note Strings

**Never use emoji in any output field.** All `note`, `lighthouse_recap`, `executive_summary`, and `top_5` values must use plain text only. No ✅, ❌, ⚠️, 🟢, 🔴, or any other symbol — use words instead (Pass, Fail, Partial, Warning, etc.).

For each criterion, write a note with the following parts, **separated by `\n\n`** so they render as distinct paragraphs:

**Signal line** (required for all verdicts): one of Pass / Fail / Partial / N/A / Too subjective — [brief evidence in one complete sentence]

**Reasoning** (required for all verdicts, 2–3 sentences): explain what was observed, why it leads to this verdict, and any nuance the reviewer should weigh when making the final call.

**Potential fix** (required for Fail and Partial only, 2–3 sentences): describe a concrete remediation to consider — what to change, which technique or tool to apply, and the expected improvement. Omit this block for Pass, N/A, and Too subjective verdicts.

**Writing rules:**

- **Expand every acronym on first use** within the note. Examples: "Content Delivery Network (CDN)", "Digital Asset Manager (DAM)", "Content Management System (CMS)", "Green Web Foundation (GWF)", "Cross-Origin Resource Sharing (CORS)", "Web Content Accessibility Guidelines (WCAG)". After the first use, the short form may be reused within the same note.
- **Write complete sentences** — subject, verb, object. Do not write noun-dash-noun fragments. Every sentence must be grammatically complete.
- **Use `\n\n` between blocks** — one `\n\n` after the signal line, one `\n\n` after the reasoning block (before the fix, when present).
- **Write for a mixed audience.** Notes are read by both developers and non-technical stakeholders. Explain the impact of a finding in plain terms before (or instead of) naming the technical cause. Avoid raw HTML/CSS attribute names in the reasoning block unless essential; keep those in the fix block where a developer will act on them. Prefer "the page loads all YouTube scripts immediately when it opens" over "iframes have a live src attribute set at page load".
- **Use bullet lists for multiple items.** When the reasoning block identifies more than two distinct findings, or the fix block recommends more than two distinct actions, format them as a `\n- ` bulleted list rather than a run-on sentence. Begin the block with one lead sentence, then list the items.

Examples:

- **Pass**: `"Pass — 14 of 16 below-fold images load only when the visitor scrolls to them.\n\nThe 2 exceptions are in the hero section at the top of the page, which is correct behaviour — those images are visible immediately and should not be deferred. Lazy loading is consistently applied throughout the rest of the page."`
- **Fail**: `"Fail — None of the images on the site use a modern format; all are served as JPEG or PNG.\n\nThis matters because modern formats like WebP and AVIF are 35–50% smaller at the same visual quality, and every visitor downloads full-size originals regardless of their screen size — there is no responsive sizing in place.\n\nThe following changes would have the highest impact:\n- Convert all images to WebP (with a JPEG fallback for older browsers)\n- Add srcset and sizes attributes to every image so smaller screens receive a smaller file\n- Use a <picture> element to serve AVIF to browsers that support it"`
- **Partial**: `"Partial — Responsive image sizing is used on the hero banners but not on the 18 product thumbnails.\n\nThe hero images adapt correctly to different screen sizes, but thumbnails always deliver the same large file regardless of the device — a phone downloads the same resolution as a desktop monitor.\n\nAdd srcset and sizes attributes to the thumbnail images, or configure the image pipeline to generate responsive variants automatically."`
- **N/A**: `"N/A — No video or audio content was found on any of the inspected pages.\n\nThis criterion does not apply to the site and full points are awarded by default."`
- **Too subjective**: `"Too subjective — This criterion requires knowledge of the project brief and stakeholder input.\n\nIt cannot be assessed from technical inspection alone; a human reviewer must confirm."`

Keep the signal line brief. The reasoning block should be 2–3 sentences (or a short list) — enough to explain the verdict, not a full audit report. The potential fix block should be equally concise — actionable direction, not a full tutorial.

### Step 5.5: Write `lighthouse_recap`

Run this step **after** all 27 criteria have been evaluated and **before** serializing the JSON.

If `lighthouse_pages` is `null` (no Lighthouse data available at all), set `lighthouse_recap = null` and skip the rest of this step.

Otherwise:

1. Compute the average score per category across all pages in `lighthouse_pages` (skip `null` scores).
2. Identify the weakest category (lowest average). Flag any category averaging below 90.
3. Cross-reference evidence:
   - Scan the Mode 1 sustainability report (if available) for findings that relate to the weak categories.
   - Scan the evaluated criteria for any `Fail` or `Partial` answers whose `report_mapping` overlaps with those categories.
4. Write a single prose string of **at most 600 characters** (spaces included):
   - **If any category averages below 90**: name the weakest area(s) and approximate score(s), point to 1–3 concrete causes found in the report or criteria, optionally name the relevant fix command(s) (e.g. `/performance-optim`).
   - **If all categories average ≥ 90 across all pages**: acknowledge the strong results in measured, factual terms, briefly note what is working well (caching, image optimisation, accessible markup, etc.), and suggest one area to watch or a stretch goal if relevant.

Store the result as `lighthouse_recap` (a string or `null`).

### Step 5.6: Compute `recommendations`

Run this step **after** Step 5.5 and **before** writing the JSON.

#### 1. Compute `top_5`

Iterate the evaluated criteria. For each criterion:
- Skip if `automatable === false` (answer is `null`) — human-only, not rankable
- Determine whether it is **failing**:
  - `boolean` → failing if `answer === false`
  - `checkboxes` → failing if `answer` array is missing ≥ 1 option that appears in the criterion's `answers` field
  - `range` → failing if the answer is clearly below the passing threshold implied by the default
  - `numeric` → failing if `answer > 0` (higher is worse for these criteria)
- For each failing criterion, compute **potential gain**:
  - `checkboxes`: `len(criterion.answers) - len(current_answer)` (number of unchecked options)
  - All other types (`boolean`, `range`, `numeric`): `1`
- Sort all failing criteria descending by potential gain
- Take the IDs of the top 5; if fewer than 5 criteria fail, return however many do

Store as `top_5` (array of ID strings).

#### 2. Write `executive_summary`

- Count: total criteria evaluated (non-null answers), total failing, total passing
- If a Mode 1 report is available, reference the synthesizer's headline findings for additional context
- Write a single prose block of **at most 600 characters** covering:
  - Overall verdict — is the site doing well or not, and why
  - Main failing areas (categories or domains with the most failures)
  - Brief note on what would help most
- Measured tone — factual, no hyperbole

Store as `executive_summary` (a string).

### Step 6: Write Output JSON

**Before writing the file, verify all of the following are ready:**

- [ ] `lighthouse_recap` string written in Step 5.5 (or `null`)
- [ ] `recommendations.executive_summary` written in Step 5.6
- [ ] `recommendations.top_5` array of exactly 5 criterion IDs written in Step 5.6
- [ ] Every criterion ID in `top_5` has `"recommended": true` in its `evaluation` entry
- [ ] No extra keys in `meta` beyond the exact nine listed below

**Do not write the file until all boxes are checked.**

Save to `{output_dir}/lowwwimpact-evaluation.json`:

```json
{
  "meta": {
    "url": "<primary URL>",
    "urls": ["<primary URL>", "<url2>", "<url3>"],
    "date": "<YYYY-MM-DD>",
    "lighthouse": "<'carbon-performance-audit' | 'standalone' | null>",
    "criteria_version": "lowwwimpact v1",
    "total_criteria": 27,
    "evaluated": "<count of non-null answers, including N/A-awarded criteria>",
    "skipped_subjective": "<count of null answers — automatable: false criteria only>",
    "na": "<count of answers where note starts with 'N/A'>"
  },
  "evaluation": [
    {
      "id": "1.4.c",
      "type": "boolean",
      "question": "Is lazy loading used to ensure that image assets are only loaded when they are needed?",
      "answer": true,
      "note": "Pass — 14 of 16 below-fold images use loading=\"lazy\""
    },
    {
      "id": "1.1.b",
      "type": "checkboxes",
      "question": "Were the needs of the planet...",
      "answer": null,
      "note": "Manual verification needed — requires knowledge of team training records"
    }
  ],
  "pages": {
    "page-1": {
      "url": "https://example.com",
      "title": "Home — Example",
      "performance": 72,
      "accessibility": 91,
      "best_practices": 83,
      "seo": 95,
      "initial_weight_kb": 820,
      "deferred_weight_kb": 1340
    },
    "page-2": {
      "url": "https://example.com/about",
      "title": "About — Example",
      "performance": 68,
      "accessibility": 88,
      "best_practices": 83,
      "seo": 90,
      "initial_weight_kb": 640,
      "deferred_weight_kb": 980
    }
  },
  "lighthouse_recap": "Performance is the weakest area (avg. 70/100 across pages). The audit found render-blocking JS and unoptimised images as main causes — criteria 1.4.b and 2.2.a confirm unminified assets. Running /performance-optim and /image-optim would likely bring scores above 85.",
  "recommendations": {
    "executive_summary": "The site handles infrastructure and font loading well but fails on image optimisation and third-party script management. Seven criteria failed outright, with images and JS weight being the most impactful gaps. A focused sprint on /image-optim and /third-party-optim would address the majority of the issues.",
    "top_5": ["1.4.b", "1.5.c", "2.5.c", "2.2.a", "3.2.a"]
  },
  "journeys": {
    "journey-1": {
      "description": "From homepage, find a product, add to cart, visit the cart",
      "pages": [
        { "url": "https://example.com", "name": "Home", "kb": 420 },
        { "url": "https://example.com/shop", "name": "Shop catalogue", "kb": 380 },
        { "url": "https://example.com/shop/running-shoes", "name": "Running Shoes", "kb": 520 },
        { "url": "https://example.com/cart", "name": "Cart", "kb": 290 }
      ]
    }
  }
}
```

**STRICT SCHEMA — `meta` object**: The `meta` object must contain ONLY the exact nine keys listed above (`url`, `urls`, `date`, `lighthouse`, `criteria_version`, `total_criteria`, `evaluated`, `skipped_subjective`, `na`). Do not add any extra keys under any circumstances — not for auth notes, report paths, session details, or any other context. Use the exact key names shown: `"na"` (not `"skipped_na"` or `"na_count"`), `"skipped_subjective"` (not `"skipped"`). If you need to document something about the audit conditions, put it in `lighthouse_recap` or a criterion note.

**`meta.lighthouse`** values:
- `"carbon-performance-audit"` — data came from Mode 1 report (Step 2)
- `"standalone"` — Lighthouse was run directly in Step 3.5
- `null` — no Lighthouse data available (also omit the `pages` key entirely)

**`pages`** rules:
- Keys are `page-1`, `page-2`, … assigned in the order pages were audited (landing = `page-1`)
- `title` comes from `document.title` captured during the Playwright session
- `initial_weight_kb` — **MUST come from `lighthouse_pages`** (Step 1.9, Step 2, or Step 3.5). Always measured via `requestfinished` + `responseBodySize`. NEVER substitute a Performance API `transferSize` value from Step 3 `network` commands — CORS-restricted, compressed, 30–60% lower.
- `deferred_weight_kb` — **MUST come from `lighthouse_pages`**. Cumulative total after scrolling (always ≥ `initial_weight_kb`). Same source requirement as `initial_weight_kb`.
- Every page entry **must** include all four score fields (`performance`, `accessibility`, `best_practices`, `seo`) as actual integers. Never write `null` for a score field. If Lighthouse cannot run on a URL (e.g. authentication wall), extract session cookies from the Playwright session and re-run `/measure-page-weight` with `--cookies "<cookie-string>"` so Lighthouse can reach the page. Do not write the output JSON until scores are available for all pages.
- Omit `pages` entirely when `meta.lighthouse` is `null`
- **Explicit-only**: `pages` and `meta.urls` must contain ONLY the URLs the user explicitly provided in the prompt. Never add a URL discovered during journey navigation to either field.

**`lighthouse_recap`** rules:
- Written in Step 5.5, after all criteria are evaluated
- A plain string of at most 600 characters, or `null` if no Lighthouse data was available
- Focuses on the weakest scoring category; positive when all categories average ≥ 90

**`recommendations`** rules:
- Written in Step 5.6, after `lighthouse_recap`
- **Mandatory** — always present in the output, even if all criteria pass
- `executive_summary`: plain string ≤ 600 characters — overall verdict, main failing areas, what to prioritise
- `top_5`: array of exactly 5 criterion ID strings, ranked by potential gain (unchecked options for checkboxes, 1 for other types); excludes `automatable: false` criteria
- Each criterion whose `id` appears in `top_5` must have `"recommended": true` added to its entry in the `evaluation` array

**`journeys`** rules:
- Keys are `journey-1`, `journey-2`, … in the order the user provided them
- Each entry has `description` (the original natural-language text) and `pages` (ordered array)
- Each page entry: `url` (full URL), `name` (2–3 word title, site suffix stripped), `kb` (integer transfer size)
- `kb` is measured in a **single sequential session** (accumulated cache across steps): step 1
  is a cold load; steps 2+ reflect warm-cache load from assets cached in earlier steps. This
  simulates a real user navigating across pages in one session. Measurement is taken 3 seconds
  after the `load` event fires. Cross-origin resources may be underreported (CORS limitation).
- Omit the `journeys` key entirely when the user skipped journey input

The `evaluation` array must contain one entry per criterion, in the same order as the criteria file.

### Step 7: Close Session

```bash
playwright-cli -s=evaluator close
```

## Guidelines

- **Start from defaults.** Every criterion has a `default_answer` and `default_note`. Use them as your starting point, then confirm or override with evidence.
- **Never fabricate evidence.** Only change a default based on data from reports or Playwright inspection.
- **Respect the type.** boolean gets `true`/`false`, range gets a number, numeric gets a number, checkboxes gets an array of strings that exactly match values from the `answers` field.
- **Keep notes factual and readable.** Write a signal line, then a reasoning block, then (for Fail/Partial) a fix block — separated by `\n\n`. Use complete sentences; no fragments. Expand every acronym on first use. Write for a mixed audience: plain-language impact in the reasoning block, technical specifics in the fix block. Use `\n- ` bullet lists when enumerating more than two findings or actions. Avoid vague language — use specific evidence ("14/16 images", "0 WebP sources detected").
- **Use N/A for inapplicable criteria.** If a site has no video, give full points to media criteria (1.5.a-d): set boolean answers to `true` and checkboxes answers to all options except "None of the above". Write note as "N/A — no video/audio content on the site". Do NOT set answer to null for N/A — null is reserved for `automatable: false` criteria only.
- **Criteria with `automatable: false` keep their null defaults.** Don't try to infer subjective answers from technical data. Project strategy, stakeholder alignment, and design intent require human input.
- **Criteria with `automatable: "partial"`** may have some checkboxes you can verify and some you can't. Confirm or remove testable options; leave untestable ones for the human.
- **Aggregate across URLs.** If multiple URLs are provided, run checks on each and use the combined evidence. If one page passes but another fails, note both in the description.

## References

- `references/lowwwimpact-criteria.json` — the 27 criteria with defaults
- `references/playwright-guide.md` — Playwright CLI commands for live inspection
- Mode 1 agent reports — primary evidence source
