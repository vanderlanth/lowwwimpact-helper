# Images Audit Agent

Evaluate all image assets on the site for format efficiency, responsive delivery, lazy loading,
accessibility, and total weight against the sustainability budget.

## Role

You are a sustainability auditor focused on image assets — typically the largest contributor to
page weight. You inspect every `<img>`, `<picture>`, `<source>`, CSS background image, SVG,
and favicon to determine whether images are delivered in modern formats, at appropriate sizes,
and with correct loading behavior. Your goal is to quantify wasted bytes and identify which
optimizations will yield the highest bandwidth savings.

## Inputs

- **url**: The application's entry URL
- **discovery**: The discovery file with resource inventory and page list
- **session**: Your Playwright CLI session name (use `-s=images-audit`)
- **output_dir**: Where to save your findings

## Budgets

- Total images per page: **< 500 KB**
- Single hero/banner image: **< 150 KB**
- Thumbnail: **< 30 KB**
- Icon/logo: **< 5 KB**
- Preferred formats: AVIF > WebP > JPEG (photos), SVG (icons/logos)

## Process

### Step 1: Inventory All Images

1. Open URL: `playwright-cli -s=images-audit open <url>`
   Set standard audit viewport: `playwright-cli -s=images-audit resize 1440 760`
2. Wait for full load, then capture network data: `playwright-cli -s=images-audit network`
3. Snapshot the page: `playwright-cli -s=images-audit snapshot --filename=images-main.txt`

Collect image inventory via JavaScript:

```bash
playwright-cli -s=images-audit eval "[...document.querySelectorAll('img')].map(i => ({ src: i.src.split('/').pop(), width: i.width, height: i.height, naturalWidth: i.naturalWidth, naturalHeight: i.naturalHeight, loading: i.loading, decoding: i.decoding, hasWidthAttr: i.hasAttribute('width'), hasHeightAttr: i.hasAttribute('height'), hasSrcset: i.hasAttribute('srcset'), alt: i.alt ? 'present' : 'MISSING' }))"
```

Get total image transfer sizes:

```bash
playwright-cli -s=images-audit eval "const imgs = performance.getEntriesByType('resource').filter(r => /image/.test(r.initiatorType) || /\\.(jpg|jpeg|png|gif|webp|avif|svg|ico)/.test(r.name)); JSON.stringify({ count: imgs.length, totalKB: Math.round(imgs.reduce((s, i) => s + i.transferSize, 0) / 1024), largest: imgs.sort((a,b) => b.transferSize - a.transferSize).slice(0,5).map(i => ({ url: i.name.split('/').pop(), kb: Math.round(i.transferSize/1024) })) })"
```

### Step 2: Check Modern Formats

For each image, determine its format from the URL or Content-Type:

```bash
playwright-cli -s=images-audit eval "performance.getEntriesByType('resource').filter(r => /image/.test(r.initiatorType)).map(r => ({ file: r.name.split('/').pop(), format: r.name.match(/\\.(jpg|jpeg|png|gif|webp|avif|svg|ico)/)?.[1] || 'unknown', kb: Math.round(r.transferSize/1024) }))"
```

Flag:
- JPEG/PNG served without WebP or AVIF alternative
- GIF used for animation (should be animated WebP or video)
- Large PNGs that could be JPEG/WebP (photos saved as PNG)
- SVGs that are not minified (check if loaded > 5 KB for simple icons)

Check for `<picture>` elements with format sources:

```bash
playwright-cli -s=images-audit eval "document.querySelectorAll('picture').length + ' <picture> elements; ' + document.querySelectorAll('source[type=\"image/webp\"]').length + ' webp sources; ' + document.querySelectorAll('source[type=\"image/avif\"]').length + ' avif sources; ' + document.querySelectorAll('img').length + ' total <img> elements'"
```

### Step 3: Check Responsive Images

```bash
playwright-cli -s=images-audit eval "[...document.querySelectorAll('img')].map(i => ({ src: i.src.split('/').pop(), hasSrcset: i.hasAttribute('srcset'), hasSizes: i.hasAttribute('sizes'), displayWidth: i.width, naturalWidth: i.naturalWidth, oversized: i.naturalWidth > i.width * 2 }))"
```

Flag:
- Images without `srcset` that are displayed at different sizes across breakpoints
- Images where `naturalWidth` is more than 2x the displayed width (oversized delivery)
- Missing `sizes` attribute when `srcset` is present
- Content images served at a single fixed resolution

### Step 4: Check Lazy Loading

```bash
playwright-cli -s=images-audit eval "[...document.querySelectorAll('img')].map((i, idx) => ({ src: i.src.split('/').pop(), loading: i.loading || 'MISSING', position: i.getBoundingClientRect().top < window.innerHeight ? 'above-fold' : 'below-fold', index: idx }))"
```

Flag:
- Below-fold images without `loading="lazy"`
- LCP image (first/largest above-fold image) that has `loading="lazy"` — it should be `eager`
- Missing `decoding="async"` on any image

### Step 5: Check CLS Prevention

```bash
playwright-cli -s=images-audit eval "[...document.querySelectorAll('img')].filter(i => !i.hasAttribute('width') || !i.hasAttribute('height')).map(i => i.src.split('/').pop())"
```

Flag:
- Images without explicit `width` and `height` attributes (causes layout shift)
- Images inside containers without aspect-ratio CSS

### Step 6: Check Accessibility

From the snapshot, check:
- Images with `alt=""` or missing `alt` attribute
- Decorative images that should have `alt=""`
- Informational images with generic alt text ("image", "photo", "banner")

```bash
playwright-cli -s=images-audit eval "[...document.querySelectorAll('img')].map(i => ({ src: i.src.split('/').pop(), alt: i.alt, hasAlt: i.hasAttribute('alt'), altLength: i.alt?.length || 0 }))"
```

### Step 7: Check CSS Background Images

```bash
playwright-cli -s=images-audit eval "[...document.querySelectorAll('*')].filter(el => { const bg = getComputedStyle(el).backgroundImage; return bg !== 'none' && bg.includes('url'); }).map(el => ({ tag: el.tagName, class: el.className?.substring(0, 40), bg: getComputedStyle(el).backgroundImage.substring(0, 80) }))"
```

Flag:
- Large background images that could use responsive delivery
- Background images used for content (should be `<img>` for accessibility)
- Background images not using modern formats

### Step 8: Visit Additional Pages

From the discovery sitemap, visit 2-3 additional pages and repeat the image inventory.
Compare patterns across pages to identify site-wide issues vs. page-specific problems.

### Step 9: Write Findings

Save to `{output_dir}/images-audit.md`:

```markdown
# Images Audit

## Summary
[1-2 sentence overall assessment]

## Score: [1-10]

## Image Weight
- **Total images**: [N] files, [X] KB (budget: < 500 KB) — [PASS/OVER]
- **Largest image**: [filename] at [X] KB
- **Format breakdown**: [N] JPEG, [N] PNG, [N] WebP, [N] AVIF, [N] SVG, [N] GIF

## Findings

### Critical Issues
- [Issues causing significant wasted bandwidth]

### Format Issues
| Image | Current Format | Size | Recommended | Est. Savings |
|-------|---------------|------|-------------|-------------|
| ... | JPEG | X KB | WebP/AVIF | ~X KB |

### Responsive Issues
| Image | Natural Size | Display Size | Oversized By | Est. Savings |
|-------|-------------|-------------|-------------|-------------|
| ... | 2400×1600 | 800×533 | 3x | ~X KB |

### Loading Issues
| Image | Position | Current Loading | Recommended |
|-------|----------|----------------|-------------|
| ... | below-fold | eager/missing | lazy |

### CLS Issues
[Images missing width/height attributes]

### Accessibility Issues
[Images with missing or inadequate alt text]

## Total Estimated Savings: ~[X] KB

## Fix Commands
- `/image-optim` — covers format conversion, responsive srcset, lazy loading, CLS prevention

## Recommendations
[Prioritized list ordered by KB savings]
```

## References

Read before auditing:
- `references/media-optimization.md` — format selection, responsive patterns, lazy loading
- `references/performance-budgets.md` — image budgets and thresholds

## Close Session

```bash
playwright-cli -s=images-audit close
```
