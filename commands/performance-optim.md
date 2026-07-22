# Performance — Page Weight Budget

Audit, enforce, and monitor a page weight budget across this project. Define the budget, wire up measurement tooling, and block or warn on deployment if the budget is exceeded. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Define the Page Weight Budget

The total transfer size of all resources for a page must not exceed **2 MB on a cold load**. This is the absolute ceiling — but the real per-category budgets are not fixed numbers. They are **generated dynamically** from the project's actual content by estimating what each asset category should weigh after all optimisations are applied.

Run the budget generator before every audit or deployment:

```bash
node scripts/generate-budget.js
```

This produces a `budget.json` calibrated to the project's real content — a site with 40 images gets a larger image allowance than one with 3, but is held to a proportionally tighter standard for what those images must weigh after compression and format conversion.

### How Budgets Are Estimated

Each file in the build output is categorised and assessed against the best achievable weight for its type. A **20% tolerance** is added above the estimated optimised size to allow for minor variation. The total is then capped at 2 MB.

**Optimisation ratios applied per format:**

| Current state | Estimated saving | Retained weight |
|---|---|---|
| JPEG → AVIF | −65% | 35% of original |
| JPEG → WebP | −30% | 70% of original |
| PNG → AVIF | −80% | 20% of original |
| PNG → WebP | −60% | 40% of original |
| WebP → AVIF | −30% | 70% of original |
| Already AVIF | 0% savings | 100% (already optimal) |
| JS unminified → minified + brotli | −80% | 20% of original |
| JS minified → brotli | −70% | 30% of original |
| JS already brotli/gzip | 0% savings | 100% |
| CSS → minified + purged + brotli | −85% | 15% of original |
| CSS already minified | −70% | 30% of original |
| Font TTF/OTF → WOFF2 subsetted | −80% | 20% of original |
| Font WOFF2 unsubsetted → subsetted | −60% | 40% of original |
| Font already WOFF2 + subsetted | 0% savings | 100% |
| Video self-hosted → compressed WebM | −60% | 40% of original |
| Video already WebM/optimised | 0% savings | 100% |

### Budget Generator Script

```js
// scripts/generate-budget.js
import { readdirSync, statSync, writeFileSync } from 'fs';
import { join, extname, basename } from 'path';

const DIST          = './dist';
const BUDGET_FILE   = './budget.json';
const HARD_CEILING  = 2048;   // KB
const TOLERANCE     = 1.20;   // 20% above estimated optimised weight
const WARN_RATIO    = 0.75;

const RATIOS = {
  image:      { '.jpg': 0.35, '.jpeg': 0.35, '.png': 0.20, '.gif': 0.25, '.webp': 0.70, '.avif': 1.00, '.svg': 0.90 },
  script:     { minified: 0.30, unminified: 0.20 },
  stylesheet: { minified: 0.30, unminified: 0.15 },
  font:       { '.woff2': 1.00, '.woff': 0.50, '.ttf': 0.20, '.otf': 0.20, '.eot': 0.25 },
  media:      { '.webm': 1.00, '.mp4': 0.40, '.mov': 0.30, '.avi': 0.25 },
  other:      { default: 0.85 },
};

const IMAGE_EXTS  = new Set(['.jpg','.jpeg','.png','.gif','.webp','.avif','.svg']);
const SCRIPT_EXTS = new Set(['.js','.mjs','.cjs']);
const STYLE_EXTS  = new Set(['.css']);
const FONT_EXTS   = new Set(['.woff2','.woff','.ttf','.otf','.eot']);
const MEDIA_EXTS  = new Set(['.mp4','.webm','.mov','.avi','.ogg']);
const DOC_EXTS    = new Set(['.html','.htm','.xml','.json','.txt','.pdf']);

function walk(dir) {
  return readdirSync(dir).flatMap(f => {
    const full = join(dir, f);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

function isMinified(filePath) {
  const name = basename(filePath);
  return name.includes('.min.') || name.includes('-min.');
}

function estimatedSize(filePath, bytes) {
  const ext = extname(filePath).toLowerCase();
  if (IMAGE_EXTS.has(ext))  return bytes * (RATIOS.image[ext] ?? 0.35);
  if (SCRIPT_EXTS.has(ext)) return bytes * (isMinified(filePath) ? RATIOS.script.minified : RATIOS.script.unminified);
  if (STYLE_EXTS.has(ext))  return bytes * (isMinified(filePath) ? RATIOS.stylesheet.minified : RATIOS.stylesheet.unminified);
  if (FONT_EXTS.has(ext))   return bytes * (RATIOS.font[ext] ?? 0.50);
  if (MEDIA_EXTS.has(ext))  return bytes * (RATIOS.media[ext] ?? 0.40);
  if (DOC_EXTS.has(ext))    return bytes * RATIOS.other.default;
  return bytes * RATIOS.other.default;
}

function classify(filePath) {
  const ext = extname(filePath).toLowerCase();
  if (IMAGE_EXTS.has(ext))              return 'image';
  if (SCRIPT_EXTS.has(ext))            return 'script';
  if (STYLE_EXTS.has(ext))             return 'stylesheet';
  if (FONT_EXTS.has(ext))              return 'font';
  if (MEDIA_EXTS.has(ext))             return 'media';
  if (['.html','.htm'].includes(ext))  return 'document';
  return 'other';
}

const totals = { document: 0, stylesheet: 0, script: 0, font: 0, image: 0, media: 0, other: 0 };
const raw    = { document: 0, stylesheet: 0, script: 0, font: 0, image: 0, media: 0, other: 0 };
const counts = { document: 0, stylesheet: 0, script: 0, font: 0, image: 0, media: 0, other: 0 };

for (const file of walk(DIST)) {
  const bytes    = statSync(file).size;
  const category = classify(file);
  raw[category]    += bytes;
  totals[category] += estimatedSize(file, bytes);
  counts[category] += 1;
}

const budgetKB = {};
let totalEstimatedKB = 0;

for (const [cat, bytes] of Object.entries(totals)) {
  const kb = Math.ceil((bytes * TOLERANCE) / 1024);
  budgetKB[cat] = kb;
  totalEstimatedKB += kb;
}

if (totalEstimatedKB > HARD_CEILING) {
  const scale = HARD_CEILING / totalEstimatedKB;
  for (const cat of Object.keys(budgetKB)) {
    budgetKB[cat] = Math.floor(budgetKB[cat] * scale);
  }
  totalEstimatedKB = HARD_CEILING;
  console.warn(`⚠️  Estimated optimised weight exceeds 2 MB ceiling. Budgets scaled down proportionally.`);
}

const budget = [{
  resourceSizes: [
    { resourceType: 'document',   budget: budgetKB.document   },
    { resourceType: 'stylesheet', budget: budgetKB.stylesheet },
    { resourceType: 'script',     budget: budgetKB.script     },
    { resourceType: 'font',       budget: budgetKB.font       },
    { resourceType: 'image',      budget: budgetKB.image      },
    { resourceType: 'media',      budget: budgetKB.media      },
    { resourceType: 'other',      budget: budgetKB.other      },
    { resourceType: 'total',      budget: totalEstimatedKB    },
  ],
  timings: [
    { metric: 'first-contentful-paint',   budget: 1800 },
    { metric: 'largest-contentful-paint', budget: 2500 },
    { metric: 'total-blocking-time',      budget: 200  },
    { metric: 'cumulative-layout-shift',  budget: 0.1  },
    { metric: 'interactive',              budget: 3800 },
    { metric: 'speed-index',              budget: 3400 },
  ],
}];

writeFileSync(BUDGET_FILE, JSON.stringify(budget, null, 2));
console.log(`Written to ${BUDGET_FILE}`);
```

Add to `package.json`:
```json
{
  "scripts": {
    "budget:generate": "node scripts/generate-budget.js",
    "prebuild":        "npm run budget:generate"
  }
}
```

### Secondary Performance Budgets

| Metric | Budget | Measured under |
|---|---|---|
| First Contentful Paint (FCP) | ≤ 1.8 s | Mobile, Slow 3G, 4× CPU |
| Largest Contentful Paint (LCP) | ≤ 2.5 s | Mobile, Slow 3G, 4× CPU |
| Total Blocking Time (TBT) | ≤ 200 ms | Mobile, Slow 3G, 4× CPU |
| Cumulative Layout Shift (CLS) | ≤ 0.1 | Any |
| Time to Interactive (TTI) | ≤ 3.8 s | Mobile, Slow 3G, 4× CPU |
| Speed Index | ≤ 3.4 s | Mobile, Slow 3G, 4× CPU |
| Carbon per page load | ≤ 0.5 g CO₂ | Ecograder / Website Carbon |

---

## 2. Build Optimisations

### 2.1 Minify HTML, CSS, and JavaScript

**Vite (recommended default):**

```js
// vite.config.js
import { defineConfig } from 'vite';
import { createHtmlPlugin } from 'vite-plugin-html';

export default defineConfig({
  build: {
    minify: 'esbuild',
    cssMinify: true,
    rollupOptions: { output: { compact: true } },
  },
  plugins: [createHtmlPlugin({ minify: true })],
});
```

**webpack:**

```js
const TerserPlugin       = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  mode: 'production',
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin({ terserOptions: { compress: { drop_console: true }, mangle: true, format: { comments: false } } }), new CssMinimizerPlugin()],
  },
};
```

### 2.2 Remove Unused CSS

**PurgeCSS with PostCSS:**

```js
// postcss.config.js
import purgecss from '@fullhuman/postcss-purgecss';

export default {
  plugins: [
    purgecss({
      content: ['./src/**/*.{html,js,ts,jsx,tsx,svelte,vue,php}', './templates/**/*.{html,twig,php}'],
      defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || [],
      safelist: { standard: [/^js-/, /^is-/, /^has-/], deep: [/modal$/, /tooltip$/], greedy: [/data-/] },
    }),
  ],
};
```

### 2.3 Tree-shake JavaScript

```js
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      treeshake: { moduleSideEffects: false, propertyReadSideEffects: false, unknownGlobalSideEffects: false },
    },
  },
});
```

Use named imports, not namespace imports:

```js
// Tree-shakeable
import { debounce } from 'lodash-es';

// Pulls entire library
import _ from 'lodash';
```

### 2.4 Avoid Shipping Development Dependencies

```bash
# Verify no process.env.NODE_ENV in build output
grep -r "process.env.NODE_ENV" dist/ || echo "✅ No process.env.NODE_ENV in build output"
```

---

## 3. Measure with Lighthouse

### Local Audit

```bash
# Install
npm install -g lighthouse

# Run audit (mobile preset, slow 3G)
lighthouse https://example.com \
  --preset=perf \
  --emulated-form-factor=mobile \
  --throttling-method=simulate \
  --output=html \
  --output-path=./reports/lighthouse.html

# Run with budget enforcement
lighthouse https://example.com \
  --budget-path=./budget.json \
  --output=json \
  --output-path=./reports/lighthouse.json
```

### Lighthouse CI (for automated PR checks)

```bash
npm install -g @lhci/cli
lhci autorun
```

```js
// lighthouserc.js
export default {
  ci: {
    collect: {
      url: ['http://localhost:3000', 'http://localhost:3000/about'],
      numberOfRuns: 3,
      settings: { preset: 'perf', formFactor: 'mobile', throttlingMethod: 'simulate' },
    },
    assert: {
      budgetsFile: './budget.json',
      assertions: {
        'categories:performance':   ['warn',  { minScore: 0.8  }],
        'first-contentful-paint':   ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'total-blocking-time':      ['error', { maxNumericValue: 200  }],
        'cumulative-layout-shift':  ['error', { maxNumericValue: 0.1  }],
        'uses-text-compression':    ['error', { minScore: 1    }],
        'unused-javascript':        ['warn',  { minScore: 0.9  }],
      },
    },
    upload: { target: 'temporary-public-storage' },
  },
};
```

---

## 4. Measure with WebPageTest

Recommended test configuration:
- **Browser:** Chrome on a Motorola G (Android)
- **Connection:** 3G Fast (1.6 Mbps / 768 Kbps, 150ms RTT)
- **Runs:** 3 (median reported)

| Metric | Target |
|---|---|
| First Contentful Paint | ≤ 1.8 s |
| Speed Index | ≤ 3.4 s |
| Largest Contentful Paint | ≤ 2.5 s |
| Total Blocking Time | ≤ 200 ms |
| Total page weight | ≤ 2,048 KB |
| Total requests | ≤ 50 |
| Repeat view total weight | ≤ 200 KB |

---

## 5. Measure with Ecograder

Visit [ecograder.com](https://ecograder.com) and run an audit against the production URL. Target a score of **80 or above**.

Ecograder scoring criteria:
- Page weight < 1 MB (full marks) / < 2 MB (passing)
- Hosted on verified green energy infrastructure
- Images served in next-gen formats (WebP/AVIF)
- Caching headers present
- No autoplay video
- Fonts self-hosted and subsetted
- Minimal third-party requests

---

## 6. Pre-Deployment Budget Warnings

### npm `prebuild` / `postbuild` Hooks

```json
{
  "scripts": {
    "budget:generate": "node scripts/generate-budget.js",
    "budget:check":    "node scripts/bundle-budget.js",
    "prebuild":        "npm run budget:generate",
    "postbuild":       "npm run budget:check"
  }
}
```

### GitHub Actions CI Workflow

```yaml
# .github/workflows/performance.yml
name: Performance Budget

on:
  pull_request:
    branches: [main, staging]
  push:
    branches: [main]

jobs:
  budget:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build
      - run: npm run budget:check
      - run: npm run preview &
      - run: npx wait-on http://localhost:3000 --timeout 30000
      - run: npx lhci autorun
        env: { LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }} }
```

### Git Pre-Push Hook

```bash
#!/bin/sh
# .git/hooks/pre-push
npm run budget:check || exit 1
```

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied
List every file created or modified — `budget.json` added, scripts written, CI workflow added, Lighthouse CI config created.

### ⚠️ Manual Actions Required
List items requiring human action — setting `AUDIT_URL` and environment variables, configuring `LHCI_GITHUB_APP_TOKEN` in GitHub secrets, running initial Lighthouse baseline, updating `example.com` URLs in config files. Include exact file paths and steps.

### Current Budget Status
- Total page weight: X KB / 2048 KB budget
- Lighthouse Performance score: X / 100
- LCP: X ms / 2500 ms budget
- TBT: X ms / 200 ms budget
- CLS: X / 0.1 budget
- Estimated CO₂ per page view: X g / 0.5 g budget
- Budget pass/fail per asset category (table)

### 📊 Estimated Impact
- Page weight before and after any immediate optimisations
- Performance score before and after
- Number of CI gates added
- Whether deployment is now blocked on budget failure
