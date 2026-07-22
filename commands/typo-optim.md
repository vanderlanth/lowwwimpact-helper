# Typeface — Sustainable Typography

Audit and optimize all font usage in this project for minimal transfer size, fast rendering, and zero layout shift. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Prefer System Font Stack

- If branding does not strictly require a custom typeface, replace all font family declarations with a system font stack:
  ```css
  body {
    font-family:
      system-ui,
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      Roboto,
      Oxygen,
      Ubuntu,
      Cantarell,
      "Helvetica Neue",
      Arial,
      sans-serif;
  }
  ```
- For monospace contexts (code blocks, terminals):
  ```css
  code, pre {
    font-family:
      ui-monospace,
      "Cascadia Code",
      "Source Code Pro",
      Menlo,
      Consolas,
      "DejaVu Sans Mono",
      monospace;
  }
  ```
- Flag every `@font-face` declaration and every Google Fonts / Adobe Fonts `<link>` for review. If the font serves no brand-critical role, recommend removing it in favor of the system stack.
- Document which font families are brand-critical and must remain custom.

## 2. Format: WOFF2 Only

- Serve custom fonts exclusively as **WOFF2**. Remove any `@font-face` `src` entries for TTF, OTF, EOT, SVG, or WOFF (non-2):
  ```css
  /* Correct */
  @font-face {
    font-family: "BrandFont";
    src: url("/fonts/brand-regular.woff2") format("woff2");
    font-weight: 400;
    font-style: normal;
    font-display: swap;
  }

  /* Remove these formats */
  /* src: url("font.ttf") format("truetype"); */
  /* src: url("font.eot"); */
  /* src: url("font.woff") format("woff"); */
  ```
- WOFF2 achieves ~30% better compression than WOFF and has universal modern browser support. There is no valid reason to ship TTF or EOT in 2024+.

## 3. Self-Host All Fonts

- Remove every `<link>` to Google Fonts, Adobe Fonts (Typekit), Bunny Fonts, or any external font CDN:
  ```html
  <!-- Remove this -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet" />
  ```
- Download the WOFF2 files and place them in the project under `/fonts/` or `/public/fonts/`.
- Rewrite as a local `@font-face` declaration (see section 2).
- Tools to download Google Fonts as WOFF2 for self-hosting:
  ```bash
  # google-webfonts-helper (CLI or web UI)
  # https://gwfh.mranftl.com/fonts

  # fontsource (npm)
  npm install @fontsource/inter
  ```
- Self-hosting eliminates a third-party DNS lookup, TCP handshake, and removes a privacy-exposing external request.
- Serve fonts with long-lived cache headers:
  ```
  Cache-Control: public, max-age=31536000, immutable
  ```

## 4. Subset to Required Glyph Ranges

- Identify the actual character sets used in the project (Latin, Latin Extended, Cyrillic, etc.).
- Subset every custom font to only the required Unicode ranges using `pyftsubset` (part of `fonttools`):
  ```bash
  # Install
  pip install fonttools brotli

  # Subset to Latin only (most common for English-language sites)
  pyftsubset font.ttf \
    --output-file=font-subset.woff2 \
    --flavor=woff2 \
    --unicodes="U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"

  # Subset to only characters actually used in the project
  pyftsubset font.ttf \
    --output-file=font-subset.woff2 \
    --flavor=woff2 \
    --text-file=characters.txt
  ```
- Add a `unicode-range` descriptor to each `@font-face` so the browser only downloads the font file when those characters appear in the page:
  ```css
  @font-face {
    font-family: "BrandFont";
    src: url("/fonts/brand-latin.woff2") format("woff2");
    font-weight: 400;
    font-style: normal;
    font-display: swap;
    unicode-range: U+0020-007E, U+00A0-00FF;
  }
  ```
- Flag any font file larger than **50 KB** after subsetting as a candidate for further reduction.

## 5. Remove Unused Weights and Styles

- Audit every `font-weight` value used in CSS across the entire project.
- Remove `@font-face` declarations (and their corresponding WOFF2 files) for any weight or style not referenced anywhere in the codebase.
- **Maximum allowed: 3 weights total across all custom font families.**
- Common unnecessary inclusions to check for and remove:
  - Thin (100) and ExtraLight (200) — rarely used in body text
  - ExtraBold (800) and Black (900) — unless explicitly in use
  - Italic variants — only include if `font-style: italic` is applied in CSS
- Use variable fonts when a range of weights is genuinely needed, as a single variable font file replaces multiple static weight files:
  ```css
  @font-face {
    font-family: "BrandFont";
    src: url("/fonts/brand-variable.woff2") format("woff2-variations");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }
  ```
- Flag any project loading more than 3 distinct font weight files.

## 6. Limit Font Families

- **Maximum 2 custom font families** across the entire project (e.g. one for headings, one for body).
- If more than 2 families are loaded, flag the extras and recommend:
  - Replacing the secondary display font with a weight/size variation of the primary.
  - Replacing an icon font (Font Awesome, Material Icons) with inline SVG or an SVG sprite.
  - Removing icon fonts entirely — they are among the highest-cost, lowest-value font loads.
- Flag any icon font (`FontAwesome`, `Material Icons`, `Ionicons`, etc.) and recommend replacement with inline SVG:
  ```html
  <!-- Remove icon font usage -->
  <!-- <i class="fa fa-arrow-right"></i> -->

  <!-- Replace with inline SVG -->
  <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
    <path d="M8 1l7 7-7 7M1 8h14" stroke="currentColor" stroke-width="2" fill="none"/>
  </svg>
  ```

## 7. `font-display: swap`

- Every `@font-face` declaration must include `font-display: swap`:
  ```css
  @font-face {
    font-family: "BrandFont";
    src: url("/fonts/brand-regular.woff2") format("woff2");
    font-weight: 400;
    font-style: normal;
    font-display: swap; /* Required */
  }
  ```
- `swap` renders text immediately in the fallback font, then swaps when the custom font loads — preventing invisible text (FOIT).
- Flag any `@font-face` missing `font-display` or using `font-display: block` (which hides text during load).

## 8. Preload Critical Fonts

- Preload only the font files used **above the fold on the critical rendering path** (typically the body regular weight).
- Add a `<link rel="preload">` in `<head>` for each critical font, **before** any stylesheets:
  ```html
  <head>
    <!-- Preload only the critical font(s) -->
    <link
      rel="preload"
      href="/fonts/brand-regular.woff2"
      as="font"
      type="font/woff2"
      crossorigin="anonymous"
    />
    <!-- Then load stylesheets -->
    <link rel="stylesheet" href="/css/main.css" />
  </head>
  ```
- `crossorigin="anonymous"` is required even for self-hosted fonts — omitting it causes the browser to fetch the font twice.
- Do **not** preload more than 2 font files — over-preloading competes with other critical resources.
- Flag any Google Fonts `<link rel="preconnect">` tag — remove it once the font is self-hosted.

## 9. Eliminate Render-Blocking Font CSS

- Never load font CSS in a `<link>` that blocks rendering.
- Remove any `@import url(...)` for fonts inside CSS files — `@import` is synchronous and blocks rendering:
  ```css
  /* Remove this — blocks rendering */
  @import url('https://fonts.googleapis.com/css2?family=Inter');
  ```
- All `@font-face` declarations should live in the main stylesheet or a stylesheet loaded with `<link rel="stylesheet">` in `<head>` (not `@import`).

## 10. Fallback Font Tuning

- Define a `size-adjust`, `ascent-override`, `descent-override`, and `line-gap-override` on the fallback `@font-face` to reduce layout shift when the custom font swaps in:
  ```css
  /* Fallback tuned to match Inter metrics */
  @font-face {
    font-family: "InterFallback";
    src: local("Arial");
    size-adjust: 107%;
    ascent-override: 90%;
    descent-override: 22%;
    line-gap-override: 0%;
  }

  body {
    font-family: "BrandFont", "InterFallback", system-ui, sans-serif;
  }
  ```
- Tools to calculate override values: [fontpie](https://github.com/pixel-point/fontpie) or [next/font](https://nextjs.org/docs/app/building-your-application/optimizing/fonts).

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied
List every file modified and exactly what changed — `@font-face` updated, external `<link>` removed, `font-display: swap` added, weights removed, preload added, etc.

### ⚠️ Manual Actions Required
List items requiring human action — downloading font files, running subsetting commands, generating variable font variants. Include exact file paths and copy-paste commands.

### Font Subsetting Reference Commands
Provide ready-to-run commands for any subsetting needed:
- Latin subset: `pyftsubset font.ttf --output-file=font-latin.woff2 --flavor=woff2 --unicodes="U+0020-007E,U+00A0-00FF"`
- Text-based subset: `pyftsubset font.ttf --output-file=font-subset.woff2 --flavor=woff2 --text-file=chars.txt`
- Inspect font file size: `wc -c fonts/*.woff2`

### 📊 Estimated Impact
Provide a rough before/after summary of:
- Total font transfer size (KB) before and after
- Number of font files removed
- Number of external font requests eliminated
- Weights and families removed
- Estimated reduction in render-blocking time
