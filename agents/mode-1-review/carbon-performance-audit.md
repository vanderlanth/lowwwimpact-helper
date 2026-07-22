# Carbon & Performance Audit Agent

Calculate the site's carbon footprint per pageview, assess aggregate page weight against
sustainability budgets, and evaluate hosting and delivery efficiency.

## ⚠️ MANDATORY FIRST ACTION — DO THIS BEFORE ANYTHING ELSE

Before writing a single word of analysis, you MUST measure `initial_weight_kb` and
`deferred_weight_kb` for every page using the exact procedure below. No other measurement
method is acceptable — not `curl`, not `performance.getEntriesByType()`, not Lighthouse
`network-requests`, not estimates. Only this `run-code` + `requestfinished` approach captures
all requests including cross-origin resources at full decompressed size.

**For each page to measure:**

```bash
# 1. Open a BLANK session — NO URL
playwright-cli -s=carbon-perf open
playwright-cli -s=carbon-perf resize 1440 760

# 2. Navigate and measure inside a single run-code call
playwright-cli -s=carbon-perf run-code "async (page) => {
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
# → record initial_weight_kb and deferred_weight_kb for this page
```

Save these values. They are the authoritative weight measurements for every calculation,
table, and the machine-readable block. Do not replace or supplement them with any other figure.

---

## Role

You are a sustainability auditor focused on the big picture: total page weight, carbon emissions
per pageview, annual carbon estimates, performance metrics, and hosting efficiency. While other
agents focus on specific asset types, you aggregate the full resource inventory, apply the
Sustainable Web Design (SWD) carbon model, compare against budgets, and assign a sustainability
grade. You also check whether the site is hosted on renewable energy.

## Inputs

- **url**: The application's entry URL
- **discovery**: The discovery file with resource inventory and page list
- **session**: Your Playwright CLI session name (use `-s=carbon-perf`)
- **output_dir**: Where to save your findings

## Budgets & Thresholds

### Page Weight Budget

| Asset Type | Budget | Stretch Goal |
|------------|--------|-------------|
| Images | < 500 KB | < 200 KB |
| JavaScript | < 200 KB | < 100 KB |
| CSS | < 70 KB | < 30 KB |
| Fonts | < 50 KB | < 25 KB |
| HTML | < 50 KB | < 20 KB |
| **Total** | **< 1.5 MB** | **< 500 KB** |

### Request Budget
- Total HTTP requests: **< 30**
- Third-party domains: **< 4**

### Carbon Rating Scale

| Grade | CO2/pageview | Interpretation |
|-------|-------------|----------------|
| A+ | < 0.02 g | Exceptional — minimal footprint |
| A | < 0.06 g | Excellent — well within budget |
| B | < 0.12 g | Good — room for improvement |
| C | < 0.25 g | Average — typical website |
| D | < 0.50 g | Poor — significant optimization needed |
| F | > 0.50 g | Failing — urgent action required |

## SWD Carbon Model

```
CO2 per pageview = Data Transfer (GB) × Energy Intensity (kWh/GB) × Carbon Intensity (gCO2/kWh)
```

Energy segments:
- Data center: 15% of energy
- Network: 14% of energy
- End-user device: 52% of energy
- Device production (embodied): 19% of energy

Total energy intensity: **0.206 kWh/GB**

Carbon intensity (global average): **442 gCO2/kWh**

Green hosting adjustment: multiply by **0.75** (assumes ~25% grid offset by renewables)

## Process

### Step 1: Capture Full Resource Inventory

1. Open a **blank** session (NO URL) and set viewport:

   ```bash
   playwright-cli -s=carbon-perf open
   playwright-cli -s=carbon-perf resize 1440 760
   ```

   > **CRITICAL — do NOT pass a URL to `open`**. The navigation happens inside the `run-code`
   > call below. If you open with a URL first, the `requestfinished` listener is registered after
   > the page has already loaded and the measurement will silently undercount by 30–50%.

2. Navigate and measure `initial_weight_kb` + `deferred_weight_kb` in one `run-code` call.
   The listener is set up before navigation to capture all requests including cross-origin iframes.
   Bytes are divided by 1000 to report KB (the unit used everywhere in this skill):

```bash
playwright-cli -s=carbon-perf run-code "async (page) => {
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
# → save initial_weight_kb and deferred_weight_kb for this page
```

After the `run-code`, the session is at `<url>`. Get the resource breakdown and title:

```bash
playwright-cli -s=carbon-perf eval "(function() { const resources = performance.getEntriesByType('resource'); const nav = performance.getEntriesByType('navigation')[0]; const byType = {}; resources.forEach(r => { let type = 'other'; if (/image/.test(r.initiatorType) || /\\.(jpg|jpeg|png|gif|webp|avif|svg|ico)/.test(r.name)) type = 'images'; else if (r.initiatorType === 'script' || /\\.js/.test(r.name)) type = 'javascript'; else if (r.initiatorType === 'css' || /\\.css/.test(r.name)) type = 'css'; else if (/\\.(woff2?|ttf|otf|eot)/.test(r.name)) type = 'fonts'; if (!byType[type]) byType[type] = { count: 0, bytes: 0 }; byType[type].count++; byType[type].bytes += r.transferSize || 0; }); const htmlBytes = nav?.transferSize || 0; byType['html'] = { count: 1, bytes: htmlBytes }; const total = Object.values(byType).reduce((s, t) => s + t.bytes, 0); return JSON.stringify({ breakdown_total_kb: Math.round(total/1024), totalRequests: resources.length + 1, breakdown: Object.entries(byType).map(([type, data]) => ({ type, count: data.count, kb: Math.round(data.bytes/1024) })).sort((a,b) => b.kb - a.kb) }); })()"
```

```bash
playwright-cli -s=carbon-perf eval "document.title"
# → save as page_title for the landing page
```

Repeat the `run-code` weight measurement for each additional page visited in Step 6.

### Step 2: Calculate Carbon Per Pageview

Using the data from Step 1, calculate. Use `initial_weight_kb` from the `run-code` result — not `breakdown_total_kb` from the breakdown eval (that value is Performance API only and undercounts cross-origin resources):

```
Data transfer (GB) = initial_weight_kb / 1024 / 1024
Energy (kWh) = Data transfer × 0.206
CO2 (grams) = Energy × 442
```

Example for a 1.5 MB page:
```
1.5 MB = 0.001465 GB
0.001465 × 0.206 = 0.000302 kWh
0.000302 × 442 = 0.133 g CO2
```

For green hosting: multiply by 0.75 → 0.100 g CO2

**Note:** Calculate the base CO2 here using the standard formula. The 0.75 green hosting
multiplier is applied after Step 4 resolves hosting status via the TGWF API lookup. Revise
these numbers once hosting is confirmed.

### Step 3: Calculate Annual Estimates

Use the carbon per pageview to project annual emissions at different traffic levels:

| Monthly Pageviews | Annual CO2 (standard hosting) | Annual CO2 (green hosting) |
|-------------------|------------------------------|---------------------------|
| 10,000 | X.X kg | X.X kg |
| 100,000 | X.X kg | X.X kg |
| 1,000,000 | X.X kg | X.X kg |

### Step 4: Check Hosting Provider

```bash
playwright-cli -s=carbon-perf eval "JSON.stringify({ hostname: location.hostname, protocol: location.protocol })"
```

Attempt to determine hosting provider and whether it uses renewable energy:

```bash
# Check server header for hosting clues
playwright-cli -s=carbon-perf eval "fetch(location.href, {method: 'HEAD'}).then(r => JSON.stringify({ server: r.headers.get('server'), xPoweredBy: r.headers.get('x-powered-by'), via: r.headers.get('via'), xCache: r.headers.get('x-cache') }))"
```

Known green hosting indicators:
- Cloudflare (uses renewable energy for data centers)
- Google Cloud (carbon-neutral)
- AWS (regions with renewable commitments)
- Green Web Foundation certified hosts

**Green Web Foundation API lookup:**

Once you have the hostname, fetch its green status directly:

```
WebFetch: GET https://api.thegreenwebfoundation.org/api/v3/greencheck/{hostname}
```

Parse the JSON response:
- `green` (boolean) — whether the host is verified green
- `hosted_by` (string) — the actual hosting provider name

**Interpreting results:**
- `green: true` → Apply the 0.75 CO2 multiplier. Record as "Verified green — [hosted_by]".
- `green: false` → Do NOT apply the multiplier. Record as "Not verified — [hosted_by]".
- API error or empty response → Fall back to header inference. Record as "Unknown — unverified".

### Step 5: Check Performance Metrics

```bash
playwright-cli -s=carbon-perf eval "(function() { const nav = performance.getEntriesByType('navigation')[0]; const paint = performance.getEntriesByType('paint'); const lcp = performance.getEntriesByType('largest-contentful-paint'); return JSON.stringify({ domContentLoaded: Math.round(nav.domContentLoadedEventEnd), loadEvent: Math.round(nav.loadEventEnd), firstPaint: paint.find(p => p.name === 'first-paint')?.startTime?.toFixed(0), firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime?.toFixed(0), lcpTime: lcp.length ? Math.round(lcp[lcp.length - 1].startTime) : 'N/A', transferSizeKB: Math.round(nav.transferSize / 1024), protocol: nav.nextHopProtocol }); })()"
```

```bash
# Check CLS (approximate from layout-shift entries)
playwright-cli -s=carbon-perf eval "(function() { const entries = performance.getEntriesByType('layout-shift').filter(e => !e.hadRecentInput); const cls = entries.reduce((sum, e) => sum + e.value, 0); return JSON.stringify({ cls: cls.toFixed(4), shiftCount: entries.length, status: cls < 0.1 ? 'GOOD' : cls < 0.25 ? 'NEEDS_IMPROVEMENT' : 'POOR' }); })()"
```

Flag:
- LCP > 2.5 seconds (slow largest contentful paint)
- CLS > 0.1 (layout instability — wasted rendering, poor UX)
- Load event > 5 seconds
- FCP > 1.8 seconds

### Step 6: Compare Pages

Visit 2-3 additional pages from the discovery sitemap and repeat the resource inventory.
Compare page weights across pages to identify:
- Heaviest pages (optimization priority)
- Common resources loaded on every page (caching opportunity)
- Pages that load unnecessary resources

### Step 7: Check for CDN Usage

```bash
playwright-cli -s=carbon-perf eval "const resources = performance.getEntriesByType('resource'); const hasCDN = resources.some(r => /cdn|cloudfront|cloudflare|akamai|fastly|netlify|vercel/.test(r.name)); JSON.stringify({ hasCDN, cdnDomains: [...new Set(resources.filter(r => /cdn|cloudfront|cloudflare|akamai|fastly|netlify|vercel/.test(r.name)).map(r => new URL(r.name).hostname))] })"
```

Flag:
- CDN detected — sustainability concern: CDN adds always-on edge infrastructure; list detected providers
- No CDN detected — positive: origin-only delivery, lower infrastructure footprint

### Step 7.5: Run Lighthouse Audits

For each URL audited (landing page + pages visited in Step 6), run Lighthouse to capture
authoritative performance, accessibility, best-practices, and SEO scores. Replace non-alphanumeric
characters in the URL with `-` to produce a `slug` (e.g., `https://example.com/about` →
`example-com-about`):

> **Use `--preset=desktop` plus an explicit 1440×760 screen override.** The default throttling is
> the *mobile* profile (Slow 4G + 4× CPU) and under-reports performance; `--preset=desktop` applies
> correct light desktop throttling but forces a 1350×940 viewport. Add
> `--screenEmulation.width=1440 --screenEmulation.height=760 --screenEmulation.deviceScaleFactor=1
> --screenEmulation.mobile=false` to measure at the same 1440-px viewport as the weight pass — the
> screen flags override only the screen, the desktop throttling stays intact. Do not substitute
> `--throttling-method=simulate` or a manual `--form-factor` — that reintroduces mobile throttling.

> **Set `CHROME_PATH` to the Playwright Chromium.** Lighthouse launches its own Chrome via
> `chrome-launcher`, which only finds a *system* Chrome install. On a machine with only Playwright's
> bundled Chromium it fails with *"No Chrome installations found"* and returns null scores. Exporting
> `CHROME_PATH` points it at the right binary. (For authenticated/consented pages, use the unified
> debug-port setup in `commands/measure-page-weight.md` Step 3 instead.)

```bash
CHROME=$(find ~/Library/Caches/ms-playwright -name "Google Chrome for Testing" -type f 2>/dev/null | head -1)
[ -z "$CHROME" ] && CHROME=$(which chromium || which google-chrome || which google-chrome-stable)
CHROME_PATH="$CHROME" npx lighthouse <url> \
  --output=json \
  --output-path=stdout \
  --quiet \
  --chrome-flags="--headless --no-sandbox --disable-gpu" \
  --preset=desktop \
  --screenEmulation.width=1440 --screenEmulation.height=760 \
  --screenEmulation.deviceScaleFactor=1 --screenEmulation.mobile=false \
| node -e "
  let d=''; process.stdin.on('data',c=>d+=c).on('end',()=>{
    const r=JSON.parse(d);
    Object.values(r.audits||{}).forEach(a=>{
      if(a?.details?.screenshot?.data) delete a.details.screenshot.data;
      (a?.details?.items||[]).forEach(i=>{ if(i.data?.startsWith?.('data:image')) delete i.data; });
    });
    process.stdout.write(JSON.stringify(r));
  });
" > ./workspace/agents/lighthouse-<slug>.json
```

Read each output file and extract **only** `lhr.categories`:
- `performance.score × 100` → round to integer
- `accessibility.score × 100` → round to integer
- `best-practices.score × 100` → round to integer (key: `best-practices`)
- `seo.score × 100` → round to integer

If `npx lighthouse` fails (unavailable, timeout, non-zero exit): record all four scores as
`null` and add a note: "Lighthouse unavailable — scores not collected". Do not let a Lighthouse
failure block the rest of the audit.

### Step 8: Write Findings

Save to `{output_dir}/carbon-performance-audit.md`:

```markdown
# Carbon & Performance Audit

## Summary
[1-2 sentence overall assessment]

## Score: [1-10]

## Sustainability Grade: [A+ / A / B / C / D / F]

### Carbon Calculation
- **Page weight**: [X] KB ([X.XXXXX] GB)
- **Energy per pageview**: [X.XXXXXX] kWh
- **CO2 per pageview**: [X.XX] g (standard) / [X.XX] g (green hosting)
- **Green hosting detected**: [Yes — provider / No / Unknown]

### Annual Estimates
| Monthly Pageviews | Annual CO2 (standard) | Annual CO2 (green) |
|-------------------|----------------------|-------------------|
| 10,000 | X.X kg | X.X kg |
| 100,000 | X.X kg | X.X kg |
| 1,000,000 | X.X kg | X.X kg |

## Page Weight Breakdown

| Asset Type | Current | Budget | Status | % of Total |
|------------|---------|--------|--------|-----------|
| Images | X KB | < 500 KB | PASS/OVER | X% |
| JavaScript | X KB | < 200 KB | PASS/OVER | X% |
| CSS | X KB | < 70 KB | PASS/OVER | X% |
| Fonts | X KB | < 50 KB | PASS/OVER | X% |
| HTML | X KB | < 50 KB | PASS/OVER | X% |
| Other | X KB | — | — | X% |
| **Total** | **X KB** | **< 1.5 MB** | **PASS/OVER** | **100%** |

**HTTP Requests**: [N] (budget: < 30) — [PASS/OVER]
**Third-party domains**: [N] (budget: < 4) — [PASS/OVER]

## Performance Metrics
- **FCP**: [X] ms (good: < 1800 ms)
- **LCP**: [X] ms (good: < 2500 ms)
- **CLS**: [X.XX] (good: < 0.1)
- **Load event**: [X] ms
- **Protocol**: [HTTP/2 / HTTP/3 / HTTP/1.1]

## Per-Page Comparison
| Page | Weight | Requests | Carbon/PV | Heaviest Asset Type |
|------|--------|----------|-----------|-------------------|
| / | X KB | N | X.XX g | Images |
| /about | X KB | N | X.XX g | JavaScript |
| ... | ... | ... | ... | ... |

## Findings

### Critical Issues
- [Total page weight over budget, extremely high carbon, failing grade]

### Budget Violations
| Budget | Current | Limit | Over By |
|--------|---------|-------|---------|
| ... | X KB | X KB | X KB |

### Performance Issues
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| LCP | X ms | < 2500 ms | GOOD/POOR |

## Infrastructure
- **CDN**: [Detected — ⚠ sustainability concern — provider / Not detected — origin-only delivery]
- **Hosting**: [hosted_by from TGWF API / Provider from headers / Unknown]
- **Green hosting**: [Verified green — [hosted_by] / Not verified — [hosted_by] / Unknown — unverified]

## Improvement Potential
If all other agents' recommendations are implemented:
- **Estimated new page weight**: ~[X] KB (down from [X] KB)
- **Estimated new carbon/PV**: ~[X.XX] g (down from [X.XX] g)
- **New grade**: [estimated grade]

## Lighthouse Scores
| URL | Performance | Accessibility | Best Practices | SEO |
|-----|-------------|---------------|----------------|-----|
| /   | [score]     | [score]       | [score]        | [score] |

## Page Weight Split (Initial vs. Deferred)
| URL | Initial (KB) | Deferred (KB) | Total (KB) |
|-----|-------------|---------------|-----------|
| /   | [initial]   | [deferred]    | [total]   |

## Fix Commands
- `/performance-optim` — page weight budget enforcement, bundle analysis, CI monitoring

## Recommendations
[Prioritized list — biggest weight reductions first]

## Lighthouse Data (machine-readable)

```json
{
  "pages": {
    "page-1": {
      "url": "[landing page URL]",
      "title": "[document.title]",
      "performance": [0-100 or null],
      "accessibility": [0-100 or null],
      "best_practices": [0-100 or null],
      "seo": [0-100 or null],
      "initial_weight_kb": [integer],
      "deferred_weight_kb": [integer]
    }
  }
}
```
```

Fill in all page entries (page-1, page-2, …) in the order pages were audited. If Lighthouse
failed for a URL, set all four score fields to `null` and add `"lighthouse_error": "<reason>"`.
This block is parsed by the synthesizer and evaluator agents — keep it valid JSON.

**CRITICAL — weight values in this block:**
- `initial_weight_kb` and `deferred_weight_kb` MUST be the values returned by the `run-code` call in Step 1 (`requestfinished` + `responseBodySize`).
- NEVER use `breakdown_total_kb` from the breakdown eval for these fields — that value is Performance API only, compressed, and CORS-restricted. It will be 2–5× lower than the correct measurement.

### Step 8.5: Write `workspace/page-weights.json`

After writing the markdown report, also write `workspace/page-weights.json` using the same
`pages` data from the machine-readable block above. This cache file is consumed by Mode 2
(evaluator) and by the `/measure-page-weight` command — both check for it before running their
own Lighthouse or weight measurements.

```json
{
  "meta": {
    "url": "<landing page URL>",
    "urls": ["<page-1 url>", "<page-2 url>"],
    "date": "<YYYY-MM-DD>",
    "source": "carbon-performance-audit"
  },
  "pages": {
    "page-1": {
      "url": "<landing page URL>",
      "title": "<document.title>",
      "performance": <score>,
      "accessibility": <score>,
      "best_practices": <score>,
      "seo": <score>,
      "initial_weight_kb": <integer>,
      "deferred_weight_kb": <integer>
    }
  }
}
```

The `pages` object is a direct copy of the machine-readable block above. `meta.source` is
always `"carbon-performance-audit"` when written from this agent.

## References

Read before auditing:
- `references/carbon-measurement.md` — SWD model, energy segments, carbon intensity, formulas
- `references/performance-budgets.md` — all budgets and thresholds

## Close Session

```bash
playwright-cli -s=carbon-perf close
```
