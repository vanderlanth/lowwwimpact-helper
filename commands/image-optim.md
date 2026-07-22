# Image Assets — Sustainable Optimization

Audit and optimize all image assets in this project for low bandwidth, high accessibility, and zero layout shift. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Format Requirements

- **Primary format:** WebP for all raster images.
- **Fallback:** Optimized JPEG (for photos) or PNG (for graphics with transparency).
- Structure every image using `<picture>` with both formats:
  ```html
  <picture>
    <source srcset="image.webp" type="image/webp" />
    <img src="image.jpg" alt="Descriptive alt text" width="800" height="600" />
  </picture>
  ```
- Never serve only a single format without a fallback for older browsers.

## 2. Responsive Images

- Use `srcset` and `sizes` to serve appropriately sized images per viewport:
  ```html
  <picture>
    <source
      type="image/webp"
      srcset="image-400.webp 400w, image-800.webp 800w, image-1200.webp 1200w"
      sizes="(max-width: 480px) 400px, (max-width: 1024px) 800px, 1200px"
    />
    <img
      src="image-800.jpg"
      srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
      sizes="(max-width: 480px) 400px, (max-width: 1024px) 800px, 1200px"
      alt="Descriptive alt text"
      width="1200"
      height="800"
    />
  </picture>
  ```
- Minimum breakpoints to generate: **400w** (mobile), **800w** (tablet), **1200w** (desktop).
- Never send a large desktop image to a mobile device.

## 3. Retina / HiDPI Handling

- Provide **1x and 2x** variants using `srcset` with pixel density descriptors when a fixed-size image is used (e.g., logos, icons, thumbnails):
  ```html
  <picture>
    <source srcset="logo.webp 1x, logo@2x.webp 2x" type="image/webp" />
    <img src="logo.png" srcset="logo.png 1x, logo@2x.png 2x" alt="Company logo" width="200" height="60" />
  </picture>
  ```
- Do **not** serve 2x images to 1x screens — use density descriptors or `srcset` with `sizes` correctly.
- Do **not** serve undersized images that appear blurry on any screen.

## 4. Lazy Loading & Decoding

- Add `loading="lazy"` to every image **except** above-the-fold / hero images.
- Add `decoding="async"` to every image.
- Hero or LCP images must have `loading="eager"` (or omit `loading`) and `fetchpriority="high"`:
  ```html
  <img src="hero.jpg" alt="Hero description" width="1200" height="600" loading="eager" fetchpriority="high" decoding="async" />
  ```
- Flag any image that is clearly above the fold but uses `loading="lazy"` — correct it.

## 5. Compression

- Target **80% quality** using perceptual compression.
- Use automated tooling to compress. Recommended commands:

  **Sharp (Node.js):**
  ```js
  sharp('input.jpg')
    .resize(1200)
    .webp({ quality: 80 })
    .toFile('output.webp');
  ```

  **Squoosh CLI:**
  ```bash
  squoosh-cli --webp '{"quality":80}' input.jpg
  ```

  **cwebp:**
  ```bash
  cwebp -q 80 input.png -o output.webp
  ```

  **ImageMagick (JPEG fallback):**
  ```bash
  convert input.jpg -quality 80 -strip output.jpg
  ```

- Strip all EXIF/metadata from production images unless GPS or copyright data is legally required.

## 6. Accessibility

- Every meaningful image **must** have a descriptive `alt` attribute that conveys purpose and content.
- Decorative images (purely visual, no information) **must** use `alt=""` and optionally `role="presentation"` or `aria-hidden="true"`.
- Never use the filename, "image of", or "photo of" as alt text.
- If an image conveys complex information (charts, diagrams), provide a long description via `aria-describedby` or an adjacent visible caption.
- Example:
  ```html
  <!-- Informative -->
  <img src="team.webp" alt="The Acme engineering team gathered at the 2025 offsite in Portland" />

  <!-- Decorative -->
  <img src="divider.webp" alt="" role="presentation" />
  ```

## 7. Prevent Layout Shift (CLS)

- Every `<img>` must define explicit `width` and `height` attributes matching the intrinsic image dimensions.
- When using CSS to make images responsive, pair with:
  ```css
  img {
    max-width: 100%;
    height: auto;
  }
  ```
- Alternatively, use CSS `aspect-ratio` when intrinsic dimensions are unavailable:
  ```css
  .image-container {
    aspect-ratio: 16 / 9;
    width: 100%;
  }
  .image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  ```
- Flag any image missing `width` and `height` — add them.

## 8. Hosting

- **Self-host all images whenever possible.** Flag any image loaded from a third-party URL (hotlinked) for review.
- If a third-party image is intentional (user avatar, CMS asset), document why and consider proxying through your own CDN.
- Serve images from the same origin or a CDN configured with correct cache headers:
  ```
  Cache-Control: public, max-age=31536000, immutable
  ```

## 9. Low Bandwidth Mode

- If the project does not already handle reduced data preferences, suggest adding:
  ```css
  @media (prefers-reduced-data: reduce) {
    img:not([data-critical]) {
      display: none;
    }
  }
  ```
- Optionally add a user-toggled "Low bandwidth mode" button that adds `.low-bandwidth` to `<html>` and persists via `localStorage`, hiding non-critical images.

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied
List every file modified and exactly what changed (format conversion, added `alt`, added `width`/`height`, changed `loading`, etc.).

### ⚠️ Manual Actions Required
List items that require human action — e.g., generating missing WebP variants, compressing source images, creating responsive size variants. Include exact file paths and the recommended CLI commands to resolve each.

### Image Compression Reference Commands
Provide copy-paste commands for any conversions needed:
- JPG/PNG → WebP: `cwebp -q 80 input.png -o output.webp`
- Resize + WebP (Sharp): `sharp input.jpg --resize 800 --webp --quality 80 -o output.webp`
- Strip metadata: `convert input.jpg -strip -quality 80 output.jpg`
- Batch WebP (cwebp): `for f in *.jpg; do cwebp -q 80 "$f" -o "${f%.jpg}.webp"; done`
- Generate 2x from 1x: `convert logo.png -resize 200% logo@2x.png`

### 📊 Estimated Bandwidth Impact
Provide a rough before/after estimate of image transfer size per page load where measurable.
