# Reusable Components — Maintainable Code & Duplication Audit

Audit, refactor, and enforce reusability across this project. Detect duplicate CSS rules, consolidate repeated UI patterns into shared components, identify dead JavaScript functions, and wire up tooling to prevent regressions. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Detect Duplicate CSS Rules

Duplicated CSS inflates stylesheets, creates specificity conflicts, and makes design changes require edits in multiple places.

### Automated Detection with `stylelint`

```bash
npm install --save-dev stylelint stylelint-config-standard stylelint-no-duplicate-selectors
```

```js
// .stylelintrc.js
export default {
  extends: ['stylelint-config-standard'],
  plugins: ['stylelint-no-duplicate-selectors'],
  rules: {
    'no-duplicate-selectors':           true,
    'no-duplicate-at-import-rules':     true,
    'declaration-block-no-duplicate-properties': [
      true,
      { ignore: ['consecutive-duplicates-with-different-syntaxes'] },
    ],
    'plugin/no-duplicate-selectors':    true,
  },
};
```

```bash
npx stylelint "src/**/*.{css,scss,sass,less,svelte,vue}"
```

### Detect Duplicate Declaration Blocks

```bash
npm install --save-dev postcss-combine-duplicated-selectors postcss-combine-media-query
```

```js
// postcss.config.js
import combineDuplicatedSelectors from 'postcss-combine-duplicated-selectors';
import combineMediaQuery          from 'postcss-combine-media-query';

export default {
  plugins: [
    combineDuplicatedSelectors({ removeDuplicatedProperties: true }),
    combineMediaQuery(),
  ],
};
```

### Manual Audit Script — Find Property/Value Duplicates Across Files

```js
// scripts/find-duplicate-css.js
import { readFileSync, readdirSync, statSync } from 'fs';
import { join, extname }                       from 'path';

const SRC      = './src';
const CSS_EXTS = new Set(['.css', '.scss', '.sass', '.less']);
const BLOCK_RE = /([.#]?[\w[\]="'-]+[\s,>+~[\]="'-]*)\s*\{([^}]+)\}/g;
const PROP_RE  = /([\w-]+)\s*:\s*([^;]+);/g;

function walk(dir) {
  return readdirSync(dir).flatMap(f => {
    const full = join(dir, f);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

const declarationMap = new Map();

for (const file of walk(SRC).filter(f => CSS_EXTS.has(extname(f)))) {
  const content = readFileSync(file, 'utf8');
  let block;
  while ((block = BLOCK_RE.exec(content)) !== null) {
    const selector = block[1].trim();
    const body     = block[2];
    let prop;
    while ((prop = PROP_RE.exec(body)) !== null) {
      const key = `${prop[1].trim()}:${prop[2].trim()}`;
      if (!declarationMap.has(key)) declarationMap.set(key, []);
      declarationMap.get(key).push({ file, selector });
    }
  }
}

let count = 0;
for (const [decl, locations] of declarationMap) {
  if (locations.length > 2) {
    console.log(`\n  ${decl}  (×${locations.length})`);
    locations.slice(0, 5).forEach(({ file, selector }) => console.log(`    ${file}  →  ${selector}`));
    if (locations.length > 5) console.log(`    … and ${locations.length - 5} more`);
    count++;
  }
}

if (count === 0) {
  console.log('✅ No significant CSS declaration duplication found.');
} else {
  console.warn(`\n⚠️  ${count} declaration(s) duplicated across 3+ selectors. Consider extracting to a shared class or custom property.`);
}
```

**What to do with findings:**

| Pattern | Resolution |
|---|---|
| Same utility repeated (e.g. `display:flex; gap:1rem`) | Extract to a shared utility class |
| Same selector defined in multiple files | Merge into a single canonical file |
| Duplicate `@media` breakpoints with identical bodies | Merge with `postcss-combine-media-query` |
| Component base styles copy-pasted | Extract to a base/mixin/token |

---

## 2. Consolidate Repeated Components

Repeated UI patterns that differ only in content or minor variation should become a single parameterised component.

### Detection — Find Structurally Similar HTML/Template Blocks

```js
// scripts/find-duplicate-components.js
import { readFileSync, readdirSync, statSync } from 'fs';
import { join, extname }                       from 'path';

const SRC       = './src';
const TMPL_EXTS = new Set(['.html', '.svelte', '.vue', '.jsx', '.tsx', '.php', '.twig']);
const TAG_RE    = /<(\w[\w-]*)[\s>]/g;

function walk(dir) {
  return readdirSync(dir).flatMap(f => {
    const full = join(dir, f);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

function tagSignature(content) {
  const tags = [];
  let m;
  while ((m = TAG_RE.exec(content)) !== null) tags.push(m[1].toLowerCase());
  return tags.sort().join(',');
}

function jaccardSimilarity(a, b) {
  const setA = new Set(a.split(','));
  const setB = new Set(b.split(','));
  const intersection = [...setA].filter(x => setB.has(x)).length;
  const union = new Set([...setA, ...setB]).size;
  return union === 0 ? 0 : intersection / union;
}

const files = walk(SRC).filter(f => TMPL_EXTS.has(extname(f)));
const sigs  = files.map(f => ({ file: f, sig: tagSignature(readFileSync(f, 'utf8')) }));

const THRESHOLD = 0.85;
const pairs     = [];

for (let i = 0; i < sigs.length; i++) {
  for (let j = i + 1; j < sigs.length; j++) {
    const score = jaccardSimilarity(sigs[i].sig, sigs[j].sig);
    if (score >= THRESHOLD) {
      pairs.push({ a: sigs[i].file, b: sigs[j].file, score: Math.round(score * 100) });
    }
  }
}

if (pairs.length === 0) {
  console.log('✅ No structurally similar components detected above threshold.');
} else {
  console.log(`\n⚠️  ${pairs.length} potentially duplicated component pair(s):\n`);
  pairs.sort((a, b) => b.score - a.score).forEach(({ a, b, score }) =>
    console.log(`  ${score}% similar\n    ${a}\n    ${b}\n`)
  );
}
```

### Consolidation Checklist

| Type | Signal | Resolution |
|---|---|---|
| Identical markup, different content | Same tag structure, different text/images | Parameterise into a single component with props/slots |
| Same component, different styles | Shared structure, CSS classes differ | One component + variant prop or CSS modifier class |
| Forked copy with minor changes | One file is a near-copy of another | Merge differences into the original via conditional logic |
| Parallel page sections | Hero, card grid, CTA appear on multiple pages | Extract to a shared layout section component |

**Example consolidation (Svelte):**

```svelte
<!-- Before: two near-identical files -->

<!-- src/components/BlogCard.svelte -->
<article class="card">
  <img src={post.image} alt={post.title} />
  <h2>{post.title}</h2>
  <p>{post.excerpt}</p>
  <a href={post.url}>Read more</a>
</article>

<!-- src/components/NewsCard.svelte -->
<article class="card">
  <img src={item.image} alt={item.headline} />
  <h2>{item.headline}</h2>
  <p>{item.summary}</p>
  <a href={item.link}>Read more</a>
</article>
```

```svelte
<!-- After: one canonical component -->

<!-- src/components/ContentCard.svelte -->
<script>
  let { image, title, excerpt, href, linkLabel = 'Read more' } = $props();
</script>

<article class="card">
  <img src={image} alt={title} />
  <h2>{title}</h2>
  <p>{excerpt}</p>
  <a href={href}>{linkLabel}</a>
</article>
```

---

## 3. Create Reusable Patterns

### 3.1 CSS Custom Properties as Design Tokens

Replace hardcoded values with named custom properties:

```css
/* src/styles/tokens.css */
:root {
  /* Colour */
  --color-brand:       hsl(220 90% 56%);
  --color-surface:     hsl(0 0% 100%);
  --color-text:        hsl(220 20% 12%);
  --color-text-muted:  hsl(220 10% 48%);
  --color-border:      hsl(220 14% 88%);

  /* Spacing scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-8: 2rem;

  /* Typography */
  --font-sans: system-ui, sans-serif;
  --font-mono: ui-monospace, monospace;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-lg:   1.125rem;

  /* Radius */
  --radius-sm:   0.25rem;
  --radius-md:   0.5rem;
  --radius-lg:   0.75rem;
  --radius-full: 9999px;
}
```

**Audit for hardcoded values:**

```bash
grep -rn --include="*.css" --include="*.scss" --include="*.svelte" \
  -E '#[0-9a-fA-F]{3,6}|rgb\(|rgba\(' src/ \
  | grep -v 'tokens.css' \
  | grep -v '^\s*//'
```

### 3.2 Shared CSS Utility Classes

Extract repeated multi-property patterns into named utilities (only if appearing 3+ times):

```css
/* src/styles/utilities.css */
.stack       { display: flex; flex-direction: column; }
.stack--sm   { gap: var(--space-2); }
.stack--md   { gap: var(--space-4); }
.cluster     { display: flex; flex-wrap: wrap; align-items: center; }
.center      { max-width: 72rem; margin-inline: auto; padding-inline: var(--space-4); }
.sr-only     { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
```

### 3.3 Shared JavaScript Utilities

```js
// src/lib/utils.js
export const formatDate = (date, locale = 'en-GB') =>
  new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(new Date(date));

export const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

export function debounce(fn, wait = 250) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), wait); };
}

export const truncate = (str, max = 80) =>
  str.length <= max ? str : str.slice(0, max).trimEnd() + '…';

export const groupBy = (arr, key) =>
  arr.reduce((acc, item) => { (acc[item[key]] ??= []).push(item); return acc; }, {});
```

---

## 4. Remove Unused JavaScript Functions

### 4.1 Static Analysis with `knip`

```bash
npm install --save-dev knip
```

```js
// knip.config.js
export default {
  entry:   ['src/main.{js,ts}', 'src/routes/**/*.{js,ts}', 'src/pages/**/*.{js,ts}'],
  project: ['src/**/*.{js,ts,svelte,vue,jsx,tsx}'],
};
```

```bash
npx knip
# Output: unused exports, files, and dependencies
# Exit code 1 if anything unused is found
```

### 4.2 ESLint — No Unused Variables or Imports

```bash
npm install --save-dev eslint eslint-plugin-unused-imports
```

```js
// eslint.config.js
import unusedImports from 'eslint-plugin-unused-imports';

export default [{
  plugins: { 'unused-imports': unusedImports },
  rules: {
    'unused-imports/no-unused-imports': 'error',
    'unused-imports/no-unused-vars':    ['warn', { vars: 'all', varsIgnorePattern: '^_', args: 'after-used', argsIgnorePattern: '^_' }],
  },
}];
```

### 4.3 TypeScript — `noUnusedLocals` / `noUnusedParameters`

```json
{
  "compilerOptions": {
    "noUnusedLocals":     true,
    "noUnusedParameters": true
  }
}
```

---

## 5. Pre-Commit & CI Enforcement

### `package.json` — Full Audit Suite

```json
{
  "scripts": {
    "lint:css":         "stylelint \"src/**/*.{css,scss,svelte,vue}\"",
    "lint:js":          "eslint \"src/**/*.{js,ts,svelte,vue}\" --fix",
    "audit:css-dupes":  "node scripts/find-duplicate-css.js",
    "audit:dupes":      "node scripts/find-duplicate-components.js",
    "audit:dead-code":  "knip",
    "audit:all":        "npm run lint:css && npm run lint:js && npm run audit:css-dupes && npm run audit:dupes && npm run audit:dead-code"
  }
}
```

### GitHub Actions CI

```yaml
# .github/workflows/quality.yml
name: Code Quality

on:
  pull_request:
    branches: [main, staging]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint:css
      - run: npm run lint:js
      - run: npm run audit:css-dupes
      - run: npm run audit:dupes
      - run: npm run audit:dead-code
```

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied

List every file created or modified — tokens extracted, utilities consolidated, duplicate components merged, dead functions removed, configs added.

### ⚠️ Manual Actions Required

List items requiring human review — flagged component pairs to assess for consolidation, heuristic unused functions to verify before deletion, custom property tokens to validate in designs, lint rules to tune for false positives.

### Current Duplication Status

| Check | Findings |
|---|---|
| Duplicate CSS selectors | X found |
| Duplicate declaration blocks (3+ sites) | X found |
| Structurally similar component pairs | X pairs |
| Unused JS exports (knip) | X |
| Hardcoded design values (non-token) | X |

### Estimated Impact

- CSS reduction: X KB before → X KB after purge and deduplication
- JS reduction: X KB of dead code removed
- Components consolidated: X → X files
- Design tokens extracted: X hardcoded values → token references
- CI gates added: lint, duplication audit, dead-code scan on every PR
