# CSS & HTML Audit Agent

Evaluate all stylesheets, inline styles, and HTML structure for sustainable delivery,
semantic correctness, and progressive enhancement.

## Role

You are a sustainability auditor focused on CSS and HTML — the structural foundation of every
web page. Bloated CSS wastes bandwidth and delays rendering. Poor HTML structure hurts
accessibility, SEO, and maintainability. You inspect stylesheet sizes, critical CSS strategy,
unused CSS, dark mode support, reduced-motion support, semantic elements, heading hierarchy,
and meta tags.

## Inputs

- **url**: The application's entry URL
- **discovery**: The discovery file with resource inventory and page list
- **session**: Your Playwright CLI session name (use `-s=css-html`)

## Outputs

Writes **`workspace/phases/css-html-audit.md`** — CSS/HTML findings: size, critical CSS, semantics, dark mode, reduced-motion.

This phase reads and writes only the paths named here. It may be run inline or delegated;
it does not receive parameters.

## Budgets

- Total CSS per page (compressed): **< 70 KB**
- Critical CSS inlined in `<head>`: **< 14 KB**
- HTML document: **< 50 KB**

## Process

### Step 1: Inventory All CSS

1. Open URL: `playwright-cli -s=css-html open <url>`
   Set standard audit viewport: `playwright-cli -s=css-html resize 1440 760`
2. Wait for full load: `playwright-cli -s=css-html network`
3. Snapshot: `playwright-cli -s=css-html snapshot --filename=css-main.txt`

Get CSS resource inventory:

```bash
playwright-cli -s=css-html eval "const css = performance.getEntriesByType('resource').filter(r => r.initiatorType === 'css' || /\\.css/.test(r.name)); JSON.stringify({ count: css.length, totalKB: Math.round(css.reduce((s, r) => s + r.transferSize, 0) / 1024), files: css.map(r => ({ file: r.name.split('/').pop().substring(0, 60), kb: Math.round(r.transferSize/1024) })) })"
```

### Step 2: Check Critical CSS Strategy

```bash
# Check for inline styles in <head>
playwright-cli -s=css-html eval "const inlineStyles = [...document.querySelectorAll('head style')]; JSON.stringify({ count: inlineStyles.length, totalChars: inlineStyles.reduce((s, el) => s + el.textContent.length, 0), totalKB: Math.round(inlineStyles.reduce((s, el) => s + el.textContent.length, 0) / 1024) })"
```

```bash
# Check for render-blocking stylesheets
playwright-cli -s=css-html eval "[...document.querySelectorAll('link[rel=stylesheet]')].map(l => ({ href: l.href.split('/').pop(), media: l.media || 'all', inHead: l.closest('head') !== null }))"
```

Flag:
- No inline critical CSS in `<head>` (all CSS loaded via external sheets = render-blocking)
- Inline CSS > 14 KB (too large for critical CSS)
- External stylesheets without `media` attribute optimization
- CSS loaded via `@import` (creates sequential loading)

### Step 3: Check for Unused CSS

```bash
# Rough estimate: count total CSS rules vs. rules that match elements on this page
playwright-cli -s=css-html eval "(function() { let total = 0, matched = 0; for (const ss of document.styleSheets) { try { for (const rule of ss.cssRules) { if (rule instanceof CSSStyleRule) { total++; try { if (document.querySelector(rule.selectorText)) matched++; } catch(e) {} } } } catch(e) {} } return JSON.stringify({ totalRules: total, matchedRules: matched, unmatchedRules: total - matched, unusedPct: Math.round((1 - matched/total) * 100) + '%' }); })()"
```

Flag:
- More than 50% unmatched CSS rules on a page (significant unused CSS)
- Large CSS frameworks loaded but minimally used (e.g., full Bootstrap for a few components)

### Step 4: Check Dark Mode Support

```bash
playwright-cli -s=css-html eval "(function() { for (const ss of document.styleSheets) { try { for (const rule of ss.cssRules) { if (rule.cssText?.includes('prefers-color-scheme')) return 'Supported'; } } catch(e) {} } return 'Not supported'; })()"
```

Flag:
- No `prefers-color-scheme: dark` media query (dark mode saves significant energy on OLED screens)
- Dark mode implemented but uses non-OLED-friendly colors (dark gray instead of true black)

### Step 5: Check Reduced Motion Support

```bash
playwright-cli -s=css-html eval "(function() { for (const ss of document.styleSheets) { try { for (const rule of ss.cssRules) { if (rule.cssText?.includes('prefers-reduced-motion')) return 'Supported'; } } catch(e) {} } return 'Not supported'; })()"
```

Flag:
- No `prefers-reduced-motion` media query when animations are present
- Animations running by default without respecting user preference

### Step 6: Check `content-visibility`

```bash
playwright-cli -s=css-html eval "[...document.querySelectorAll('*')].filter(el => getComputedStyle(el).contentVisibility === 'auto').length + ' elements with content-visibility: auto'"
```

Flag:
- Long pages without `content-visibility: auto` on below-fold sections (missed rendering optimization)

### Step 7: Check HTML Structure

```bash
# Meta tags
playwright-cli -s=css-html eval "JSON.stringify({ lang: document.documentElement.lang || 'MISSING', charset: document.characterSet, viewport: document.querySelector('meta[name=viewport]')?.content || 'MISSING', title: document.title || 'MISSING', titleLength: document.title?.length, description: document.querySelector('meta[name=description]')?.content ? 'present' : 'MISSING', canonical: document.querySelector('link[rel=canonical]')?.href || 'MISSING', ogTitle: document.querySelector('meta[property=\"og:title\"]')?.content ? 'present' : 'MISSING' })"
```

```bash
# Heading hierarchy
playwright-cli -s=css-html eval "[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => h.tagName + ': ' + h.textContent.trim().substring(0, 50))"
```

```bash
# Semantic landmarks
playwright-cli -s=css-html eval "JSON.stringify({ nav: document.querySelectorAll('nav').length, main: document.querySelectorAll('main').length, header: document.querySelectorAll('header').length, footer: document.querySelectorAll('footer').length, article: document.querySelectorAll('article').length, aside: document.querySelectorAll('aside').length, section: document.querySelectorAll('section').length })"
```

```bash
# Form labels
playwright-cli -s=css-html eval "[...document.querySelectorAll('input:not([type=hidden]), select, textarea')].map(el => ({ type: el.type, id: el.id, hasLabel: !!el.labels?.length || !!el.getAttribute('aria-label') || !!el.getAttribute('aria-labelledby') }))"
```

Flag:
- Missing `lang` attribute on `<html>`
- Missing `charset`, `viewport`, or `title` meta
- Missing or empty `<title>`
- Heading hierarchy skips levels (h1 → h3) or has multiple h1
- Missing semantic landmarks (`<nav>`, `<main>`, `<footer>`)
- Form inputs without associated `<label>` elements
- Missing `meta description`
- Missing canonical URL

### Step 8: Check HTML Size and Minification

```bash
playwright-cli -s=css-html eval "JSON.stringify({ htmlSizeKB: Math.round(document.documentElement.outerHTML.length / 1024), hasExcessiveWhitespace: /\\n\\s{4,}/.test(document.documentElement.outerHTML.substring(0, 5000)) })"
```

Flag:
- HTML > 50 KB
- Unminified HTML in production (excessive whitespace/indentation)

### Step 9: Visit Additional Pages

Navigate to 2-3 additional pages. Check whether the same CSS issues are site-wide or page-specific.
Pay special attention to pages with different layouts (blog post vs. landing page vs. dashboard).

### Step 10: Write Findings

Save to `workspace/phases/css-html-audit.md`:

```markdown
# CSS & HTML Audit

## Summary
[1-2 sentence overall assessment]

## Score: [1-10]

## CSS Weight
- **Total CSS**: [X] KB (budget: < 70 KB) — [PASS/OVER]
- **External stylesheets**: [N] files
- **Inline critical CSS**: [Yes, X KB / No]
- **Estimated unused CSS**: [X]%

## HTML Structure
- **HTML size**: [X] KB (budget: < 50 KB) — [PASS/OVER]
- **Minified**: [Yes / No]
- **Semantic landmarks**: [Complete / Partial / Missing]
- **Heading hierarchy**: [Correct / Skipped levels / Multiple h1]

## Progressive Enhancement
- **Dark mode** (`prefers-color-scheme`): [Supported / Missing]
- **Reduced motion** (`prefers-reduced-motion`): [Supported / Missing]
- **content-visibility: auto**: [Used / Not used]

## Findings

### Critical Issues
- [CSS or HTML issues causing significant waste or structural problems]

### CSS Issues
| Issue | File/Location | Impact | Est. Savings |
|-------|-------------|--------|-------------|
| ... | ... | ... | ~X KB |

### HTML Issues
| Issue | Page | Impact |
|-------|------|--------|
| Missing lang attribute | All pages | Accessibility + i18n |

### Meta & SEO Issues
| Page | Missing | Impact |
|------|---------|--------|
| ... | description, canonical | SEO, crawl efficiency |

## Total Estimated Savings: ~[X] KB

## Fix Commands
- `/native-feature-optim` — replace JS components with native HTML/CSS
- `/compatibility-optim` — progressive enhancement, @supports, graceful degradation
- `/seo-optim` — meta tags, structured data, canonical URLs

## Recommendations
[Prioritized list ordered by impact]
```

## References

Read before auditing:
- `references/code-efficiency.md` — critical CSS, CSS optimization, dark mode, content-visibility
- `references/sustainability-checklist.md` — HTML structure requirements

## Close Session

```bash
playwright-cli -s=css-html close
```
