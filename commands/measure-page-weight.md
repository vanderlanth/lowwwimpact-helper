# Measure Page Weight

Measure `initial_weight_kb`, `deferred_weight_kb`, and Lighthouse scores (performance,
accessibility, best_practices, seo) for one or more URLs. Saves results to the output path
(default `workspace/page-weights.json`) which evaluate mode can consume without re-measuring.

**Usage:** `/measure-page-weight <url> [url2 url3 ...] [--out <path>]`

`--out <path>` is optional and sets where the result JSON is written. Default: `workspace/page-weights.json`. (evaluate `--debug` passes `--out workspace/debug-weights.json` so it never clobbers a real cache.)

If `workspace/auth-state.json` exists (written by the shared auth setup — see `references/auth-measure-pipeline.md` Phase A), it is loaded automatically: via `state-load` into every Playwright session (Step 2) and via CDP injection into the Lighthouse Chrome instance (Step 3). No parameter needed.

> **Why not read the file inside `run-code`**: the `run-code` sandbox does not expose Node's
> `require`/`fs`/`process`. Reading `auth-state.json` from inside `run-code` always throws
> `require is not defined`; a surrounding `try/catch` swallows it and the session runs
> **unauthenticated** — landing on the login page with null Lighthouse scores and wrong KB. Auth
> must be applied with the `state-load` CLI command **before** the `run-code` navigation.

---

## Process

### Step 1: Check Prerequisites

Verify Playwright CLI is available:

```bash
playwright-cli --version
```

Verify Lighthouse is available:

```bash
npx lighthouse --version
```

If either is missing, report the gap and stop. Do not attempt measurement without both tools.

### Step 2: Measure Each URL

For each URL, open a **blank** session (no URL passed to `open`) and run the
`run-code` + `requestfinished` measurement. This is the only method that captures
all bytes including cross-origin resources.

> **CRITICAL — do NOT pass a URL to `open`**. The navigation happens inside the
> `run-code` call below. Opening with a URL would warm the cache and silently undercount
> by 30–50%.

```bash
playwright-cli -s=measure-N open
playwright-cli -s=measure-N resize 1440 760
# Inject saved auth (cookies + per-origin localStorage) BEFORE any navigation, if present.
# state-load is a no-op to skip when the file does not exist (public site).
[ -f workspace/auth-state.json ] && playwright-cli -s=measure-N state-load workspace/auth-state.json
```

```bash
playwright-cli -s=measure-N run-code "async (page) => {
  const getKB = async (reqs) => {
    const sizes = await Promise.all(reqs.map(r => r.sizes().catch(() => null)));
    const bytes = sizes.reduce((s, v) => s + (v?.responseBodySize > 0 ? v.responseBodySize : 0), 0);
    return Math.round(bytes / 1000);
  };

  // Clear only the HTTP cache (not cookies/localStorage) so weight reflects a cold first visit
  // while the auth loaded via state-load above is preserved.
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.clearBrowserCache');

  // Emulate a Retina display (deviceScaleFactor 2) — almost all real visitors are on HiDPI
  // screens (every modern Mac, most phones, many Windows laptops), so responsive images serve
  // their 2x variants. Measuring at DPR 1 loads the 1x images and undercounts real-world weight
  // on image-heavy pages (observed liip home initial 777 KB at DPR 1 vs 785 KB at DPR 2, and
  // liipgpt deferred 2542 → 3065 KB). Set this BEFORE navigation so the first load picks 2x assets.
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 760, deviceScaleFactor: 2, mobile: false });

  // Start collecting requests — full first-visit load is captured from scratch.
  const requests = [];
  page.context().on('requestfinished', (req) => requests.push(req));

  await page.goto('<url>', { waitUntil: 'load' });
  await page.waitForTimeout(3000);

  // Accept a cookie-consent banner so gated third-party resources load (real-world weight).
  // If Phase A already captured consent into auth-state.json, the banner won't appear and this
  // is a no-op; this inline click is the fallback for public pages with no saved state.
  for (const re of [/accept all/i, /allow all/i, /accept/i, /agree/i, /got it/i, /i accept/i]) {
    try { const b = page.getByRole('button', { name: re }); if (await b.first().isVisible({ timeout: 400 })) { await b.first().click(); break; } } catch (e) {}
  }
  await page.waitForTimeout(2000);

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

  const title = await page.title();
  const final_url = page.url();

  // Detect duplicate requests — the SAME url fetched more than once in this load (wasted
  // re-downloads: a third-party tag pulled in twice, an un-deduplicated bundle). Uses the same
  // requestfinished + responseBodySize data, so cross-origin bytes are counted accurately (unlike
  // the Performance API, which reports 0 for third-party). wasted_kb = every load beyond the first.
  const urlMap = new Map();
  for (const r of requests) {
    let s = null; try { s = await r.sizes(); } catch (e) {}
    const bytes = s && s.responseBodySize > 0 ? s.responseBodySize : 0;
    if (!urlMap.has(r.url())) urlMap.set(r.url(), []);
    urlMap.get(r.url()).push(bytes);
  }
  const duplicate_requests = [];
  for (const [u, arr] of urlMap) {
    if (arr.length > 1) {
      const sorted = arr.slice().sort((a, b) => b - a);
      const wasted_kb = Math.round(sorted.slice(1).reduce((s, v) => s + v, 0) / 1000);
      // NOTE: the run-code sandbox has NO global URL constructor — parse the host with a regex.
      const host = (u.match(/^[a-z]+:\/\/([^/]+)/i) || [, ''])[1];
      duplicate_requests.push({ url: u, host, count: arr.length, wasted_kb });
    }
  }
  duplicate_requests.sort((a, b) => b.wasted_kb - a.wasted_kb || b.count - a.count);

  return { initial_weight_kb, deferred_weight_kb, title, final_url, duplicate_requests };
}"
```

```bash
playwright-cli -s=measure-N close
```

Record `initial_weight_kb`, `deferred_weight_kb`, and `title` for this URL.

**Auth bounce check:** if `final_url` contains `/login`, `/signin`, or `/auth` (and the requested
URL did not), the saved auth state was not accepted — the weights describe the login page, not the
target. Re-run **Phase A** of `references/auth-measure-pipeline.md` to refresh
`workspace/auth-state.json`, then re-measure. Do not record login-page weights as the result.

**Note on values:**
- `initial_weight_kb` — total bytes transferred on first load, divided by 1000
- `deferred_weight_kb` — cumulative total after scrolling to the bottom (NOT a delta — always ≥ `initial_weight_kb`)
- Both values are captured via `requestfinished` + `responseBodySize`, which covers all resources including cross-origin third-party requests
- `deferred_weight_kb` is a **conservative lower bound** and the measurement loads each resource **once** (a clean single-pass visit). A real, longer, interactive browser session on a third-party-heavy page can total 5–20% higher because ad/analytics/chat tags **re-fire the same requests** — verified against DevTools HARs where liip's live session loaded Google Ads `gtag` twice, the hero video three times, and the Piwik beacon six times, while the automated visit loaded each once. That extra is duplicate third-party traffic, not additional page content; reproducing it would make measurements non-deterministic, so the skill deliberately measures one clean load. `initial_weight_kb` (first-load transfer) is the most stable, reproducible number — weight it most heavily when comparing against external benchmarks, and expect deferred to sit at or slightly below a real-session DevTools total.

### Step 3: Run Lighthouse for Each URL

Replace non-alphanumeric characters in the URL with `-` to form a `slug`.

> **CRITICAL — `--preset=desktop` PLUS an explicit 1440×760 screen override.** Lighthouse's default
> throttling is the *mobile* profile (Slow 4G, 4× CPU slowdown); applying it under a desktop
> form-factor crushes the performance score (observed 96 → 78 on the same page). `--preset=desktop`
> sets the correct desktop form-factor and **light desktop throttling** (CPU 1×). But the desktop
> preset also forces a **1350×940** viewport — different from the 1440×760 used for the Playwright
> weight pass. To keep both measurements at the same width, **add the screen-emulation overrides**:
>
> ```
> --preset=desktop \
> --screenEmulation.width=1440 --screenEmulation.height=760 \
> --screenEmulation.deviceScaleFactor=1 --screenEmulation.mobile=false
> ```
>
> The `--screenEmulation.*` flags override only the **screen** part of the preset — the desktop
> **throttling stays intact** (verified: CPU 1×, RTT 0, perf 98 at 1440×760). Do **not** instead
> pass `--throttling-method=simulate` or `--form-factor` manually — those reintroduce the mobile
> throttling bug. Use this exact flag set for every Lighthouse run below (public and authenticated)
> so Lighthouse and the weight pass share the 1440-px viewport.

> **CRITICAL — public and authenticated pages use the SAME Lighthouse setup.** Always launch the
> Playwright-bundled Chromium yourself on a debug port and run `lighthouse --port=9223`. Do **not**
> use the bare `lighthouse <url> --chrome-flags=…` form: that makes Lighthouse launch its *own*
> Chrome via `chrome-launcher`, which only searches for a **system** Chrome install — on a machine
> that has only Playwright's Chromium it fails hard with *"No Chrome installations found"* and every
> public-site score comes back null. Launching Chrome ourselves (with the explicit Playwright binary)
> and connecting via `--port` is the only setup that works for both cases. The **only** difference
> between public and authenticated/consented pages is the optional auth/consent injection in step 3.

```bash
# 1. Locate the Playwright Chromium binary (no system Chrome is required).
CHROME=$(find ~/Library/Caches/ms-playwright -name "Google Chrome for Testing" -type f 2>/dev/null | head -1)
[ -z "$CHROME" ] && CHROME=$(which chromium || which google-chrome || which google-chrome-stable)

# 2. Kill ALL stale debug Chrome (not just port owners — they collide and block the port), launch ONE
#    fresh instance, and POLL until the port answers (cold Chromium can take 15-20s; a fixed sleep is
#    unreliable). Use --headless (NOT --headless=new: it can crash the bundled Chromium) and bind to
#    127.0.0.1 (avoids the IPv6 ::1 ECONNREFUSED that 'localhost' triggers on macOS).
pkill -9 -f "remote-debugging-port=9223" 2>/dev/null
lsof -ti:9223 | xargs kill -9 2>/dev/null
sleep 1
rm -rf /tmp/lh-auth-<slug>
nohup "$CHROME" --headless --no-sandbox --disable-gpu \
  --remote-debugging-port=9223 --remote-debugging-address=127.0.0.1 \
  --user-data-dir=/tmp/lh-auth-<slug> >/tmp/chrome-<slug>.log 2>&1 &
disown
for i in $(seq 1 25); do
  curl -s http://127.0.0.1:9223/json/version >/dev/null 2>&1 && { echo "Chrome up after ${i}s"; break; }
  sleep 1
done
```

**3. (Authenticated / consented pages only)** If `workspace/auth-state.json` exists, inject its
cookies + per-origin localStorage (login session and/or accepted cookie-consent) into the debug
Chrome before Lighthouse navigates. **Skip this entire step for a bare public page with no saved
state.** The inject script reads the **native `storageState`** file and must run from the directory
that contains `workspace/`:

```bash
# Write the inject script to a temp file.
# Reads the native storageState format: { cookies:[...], origins:[{ origin, localStorage:[{name,value}] }] }
node -e "require('fs').writeFileSync('/tmp/inject-auth-<slug>.mjs', \`
import { get } from 'http';
import { readFileSync } from 'fs';
const state = JSON.parse(readFileSync('./workspace/auth-state.json', 'utf8'));
const url = process.argv[2];
const origin = new URL(url).origin;
// Map Playwright cookies to CDP Network.setCookies shape (drop session-cookie expires:-1, keep valid sameSite).
const cookies = (state.cookies || []).map(c => {
  const o = { name: c.name, value: c.value, domain: c.domain, path: c.path || '/', secure: !!c.secure, httpOnly: !!c.httpOnly };
  if (c.sameSite && ['Strict','Lax','None'].includes(c.sameSite)) o.sameSite = c.sameSite;
  if (typeof c.expires === 'number' && c.expires > 0) o.expires = c.expires;
  return o;
});
const ls = ((state.origins || []).find(o => o.origin === origin)?.localStorage) || [];
function cdpGet(path) {
  return new Promise((resolve) => {
    get('http://127.0.0.1:9223' + path, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(JSON.parse(d)));
    });
  });
}
function cdpSend(ws, method, params, id) {
  return new Promise(resolve => {
    ws.addEventListener('message', function h(e) {
      const m = JSON.parse(e.data);
      if (m.id === id) { ws.removeEventListener('message', h); resolve(m); }
    });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
const targets = await cdpGet('/json');
const target = targets.find(t => t.type === 'page') || targets[0];
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r));
await cdpSend(ws, 'Network.enable', {}, 1);
await cdpSend(ws, 'Network.setCookies', { cookies }, 2);
await cdpSend(ws, 'Page.enable', {}, 3);
// Set localStorage on a NON-app same-origin URL (favicon) so it persists to the profile WITHOUT
// booting the target route. If we navigated the app route here, the SPA would render warm and
// Lighthouse (run with --disable-storage-reset) would then measure a warm page → performance 0.
// Keeping the route cold lets Lighthouse do a proper cold navigation and score performance correctly.
await cdpSend(ws, 'Page.navigate', { url: origin + '/favicon.ico' }, 4);
await new Promise(r => setTimeout(r, 2000));
let id = 10;
for (const { name, value } of ls) {
  await cdpSend(ws, 'Runtime.evaluate', { expression: 'localStorage.setItem(' + JSON.stringify(name) + ', ' + JSON.stringify(value) + ')' }, id++);
}
ws.close();
console.log('Injected: ' + cookies.length + ' cookies, ' + ls.length + ' localStorage keys');
\`)"

# Run the inject script against the already-running debug Chrome (pass the full URL as argv so the
# script picks the matching origin's localStorage).
node /tmp/inject-auth-<slug>.mjs "<url>"
```

**4. Run Lighthouse** against the debug Chrome via `--port`. Add `--disable-storage-reset` **only when
state was injected in step 3** (so Lighthouse keeps the injected cookies/localStorage); omit it for a
bare public page so the run starts from clean storage:

```bash
# Authenticated / consented page (state injected in step 3):
npx lighthouse "<url>" \
  --port=9223 \
  --output=json \
  --output-path=./workspace/lighthouse-<slug>.json \
  --quiet \
  --preset=desktop \
  --screenEmulation.width=1440 --screenEmulation.height=760 \
  --screenEmulation.deviceScaleFactor=1 --screenEmulation.mobile=false \
  --disable-storage-reset

# OR — bare public page (no auth-state.json, step 3 skipped): same command WITHOUT --disable-storage-reset
npx lighthouse "<url>" \
  --port=9223 \
  --output=json \
  --output-path=./workspace/lighthouse-<slug>.json \
  --quiet \
  --preset=desktop \
  --screenEmulation.width=1440 --screenEmulation.height=760 \
  --screenEmulation.deviceScaleFactor=1 --screenEmulation.mobile=false

# 5. Kill the Chrome instance
pkill -9 -f "remote-debugging-port=9223" 2>/dev/null
```

**Retry guard — performance score `null`/`0`.** On fast-rendering SPA routes (especially hash-route
pages), Lighthouse intermittently fails to compute **Speed Index** (`audits['speed-index'].score`
comes back `null`), which nulls the **entire** `categories.performance.score` even though FCP, LCP,
TBT, and CLS all scored fine. This is non-deterministic — the *same* page returns `null`, then `83`,
then `90` across consecutive fresh runs. After each Lighthouse run, check the performance score:

```bash
node -e "const d=JSON.parse(require('fs').readFileSync('./workspace/lighthouse-<slug>.json'));const s=d.categories.performance.score;process.exit(s===null||s===0?1:0);"
```

If it exits non-zero (perf is `null`/`0`) **and the other three categories scored normally**, the run
hit the Speed Index glitch — **relaunch a fresh Chrome (steps 2-4) and re-run Lighthouse, up to 4
attempts**, keeping the first run that yields a non-null performance score. Only accept a `null`/`0`
performance after 4 failed attempts (and note it). Do not retry when accessibility/best-practices/SEO
are *also* abnormal — that indicates a real load failure (auth/consent), not the Speed Index glitch.

**Strip screenshot data** from the Lighthouse output to keep file size manageable:

```bash
node -e "
  const fs = require('fs');
  const r = JSON.parse(fs.readFileSync('./workspace/lighthouse-<slug>.json', 'utf8'));
  Object.values(r.audits||{}).forEach(a => {
    if (a?.details?.screenshot?.data) delete a.details.screenshot.data;
    (a?.details?.items||[]).forEach(i => { if (i.data?.startsWith?.('data:image')) delete i.data; });
  });
  fs.writeFileSync('./workspace/lighthouse-<slug>.json', JSON.stringify(r));
"
```

Extract category scores:

```bash
node -e "
  const d = JSON.parse(require('fs').readFileSync('./workspace/lighthouse-<slug>.json', 'utf8'));
  const c = d.categories;
  console.log(JSON.stringify({
    performance:    Math.round(c.performance.score * 100),
    accessibility:  Math.round(c.accessibility.score * 100),
    best_practices: Math.round(c['best-practices'].score * 100),
    seo:            Math.round(c.seo.score * 100)
  }));
"
```

**Lighthouse scores are mandatory and must never be estimated or fabricated.** If Lighthouse fails, diagnose and retry before giving up:

- Chrome binary not found → try `chromium`, `google-chrome`, `google-chrome-stable`, or re-run the `find` command
- CDP/inject `ECONNREFUSED` **or** Lighthouse launching its *own* Chrome (chrome-launcher error) → the debug port never bound. Causes: the poll loop gave up too early (cold Chromium can need ~20 s — raise the loop to 30), stale Chrome instances colliding on 9223 (run `pkill -9 -f "remote-debugging-port=9223"` and relaunch), or `localhost` resolving to IPv6 — always inject against `127.0.0.1`.
- Performance score far lower than expected (e.g. 78 instead of ~96) → a mobile throttling profile is being applied; confirm `--preset=desktop` is set and that no `--throttling-method`/`--screenEmulation` flags are overriding it.
- Performance score is `0` or `null` while the other three are normal → usually the non-deterministic Speed Index glitch on fast SPA routes (see the **Retry guard** above) — relaunch a fresh Chrome and re-run, up to 4 attempts. (A *warm/cached* Chrome reuse also causes this; either way the fix is a fresh instance + re-run.)
- Auth not holding (page redirects to login during the Lighthouse run) → re-run `node /tmp/inject-auth-<slug>.mjs "<url>"` and retry Lighthouse immediately without restarting Chrome
- Lighthouse exits with a non-zero code → print the full stderr output, identify the specific error, fix it, retry

Only ask the user for help if the failure cannot be resolved automatically (site unreachable, credentials rejected by the server). Never write estimated or null scores.

### Step 4: Write the output JSON

Write to the `--out` path if provided, otherwise `workspace/page-weights.json`. Create `workspace/` if it does not exist.

Assign page keys in measurement order: first URL is `page-1`, second is `page-2`, etc.

```json
{
  "meta": {
    "url": "<first URL>",
    "urls": ["<url1>", "<url2>"],
    "date": "<YYYY-MM-DD>",
    "source": "measure-page-weight"
  },
  "pages": {
    "page-1": {
      "url": "<url1>",
      "title": "<document.title>",
      "performance": 72,
      "accessibility": 91,
      "best_practices": 83,
      "seo": 95,
      "initial_weight_kb": 820,
      "deferred_weight_kb": 1340
    },
    "page-2": {
      "url": "<url2>",
      "title": "<document.title>",
      "performance": 68,
      "accessibility": 88,
      "best_practices": 79,
      "seo": 90,
      "initial_weight_kb": 640,
      "deferred_weight_kb": 980
    }
  },
  "duplicate_requests": {
    "page-1": [
      { "url": "https://www.googletagmanager.com/gtag/js?id=AW-1000834882", "host": "www.googletagmanager.com", "count": 2, "wasted_kb": 151 }
    ],
    "page-2": []
  }
}
```

**Schema rules:**
- `meta.url` — first URL provided
- `meta.urls` — all URLs in measurement order
- `meta.date` — today's date in YYYY-MM-DD format
- `meta.source` — `"measure-page-weight"` by default; the caller may override it (evaluate `--debug` sets `"debug"`)
- Page keys are `page-1`, `page-2`, … in measurement order
- `title` — from `document.title` captured in the `run-code` session
- `initial_weight_kb` — integer, from `run-code` + `requestfinished`
- `deferred_weight_kb` — integer, from `run-code` + `requestfinished` after scrolling
- Each page object contains **exactly these 8 keys** — do NOT add `duplicate_requests` (or anything else) inside a page.
- `duplicate_requests` is a **separate top-level object** keyed by the same `page-N` ids, each holding an array of URLs fetched 2+ times during the measurement: `{ url, host, count, wasted_kb }`. Empty array `[]` when a page had no duplicates. This is diagnostic data for the network audit phase and the report's `/third-party-optim` findings — it is NOT consumed by the strict `pages` schema. Omit the whole `duplicate_requests` key only if every page's array is empty.

The `pages` block is identical to the one written by the carbon-performance phase (`carbon-performance-audit.md`)
and consumed by the evaluator (`evaluator.md` Step 1.9).

### Step 5: Print Summary

Print a summary table:

```
Page weight measurements — <date>

page-1: <url>
  Title:              <title>
  Initial weight:     <N> KB
  Deferred weight:    <N> KB
  Performance:        <N>/100
  Accessibility:      <N>/100
  Best Practices:     <N>/100
  SEO:                <N>/100
  Duplicate requests: <N> (<total wasted> KB wasted)   # only if any; list top offenders below

page-2: ...

Saved to <output path>
```

When a page has duplicate requests, list the top offenders under it, e.g.:

```
  Duplicate requests: 1 (151 KB wasted)
    - gtag/js?id=AW-1000834882 (googletagmanager.com) ×2 → 151 KB  [/third-party-optim]
```

> **Note — scope of the live detector.** It catches every resource fetched 2+ times **during this
> clean automated visit** (e.g. an analytics beacon fired repeatedly, a bundle requested twice) and
> reports each with its wasted KB — map them to `/third-party-optim` or `/reusable-components-optim`.
> It does **not** capture duplicates that a site only produces for a *specific real-user segment* —
> notably Google Ads **remarketing** tags that re-load `gtag.js` only when the visitor already carries
> Google ad cookies (from a prior ad click / Google session). A fresh, cookieless audit profile never
> has that state, so those loads do not fire here regardless of headless/headed, `navigator.webdriver`
> masking, engagement simulation, or repeat visits (all verified). This is the correct baseline — an
> audit should measure a clean first-time visitor, not one visitor's ad-cookie state — so an empty
> gtag result is accurate for that baseline, not a detector failure.

When the output path is the default `workspace/page-weights.json`, add: "Evaluate mode will use this file automatically."

---

## Notes

- **Journey KB data is not included.** Journey page weights are inherently interactive and
  sequential — they must be measured inside evaluate mode's Step 1.5 where the user confirms the
  navigation path. `/measure-page-weight` only covers standalone page measurements.

- **Lighthouse runs in a separate Chrome instance** — it does not conflict with Playwright
  sessions and can run immediately after the session closes.

- **If a Playwright measurement fails** for a URL (run-code error or timeout), set
  `initial_weight_kb` and `deferred_weight_kb` to `null` for that page entry and note the error.
  Lighthouse can still run for that URL independently.

- **Re-running** `/measure-page-weight` overwrites the output file (default
  `workspace/page-weights.json`, or the `--out` path). Any existing file at that path will be replaced.
