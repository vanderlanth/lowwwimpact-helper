# Media Optimization for Sustainable Web Design

## Image Format Selection

Choose the most efficient format for the content type:

| Content Type | Best Format | Fallback | Notes |
|---|---|---|---|
| Photographs | AVIF | WebP, then JPEG | AVIF is ~50% smaller than JPEG, WebP ~30% smaller |
| Icons, logos, illustrations | SVG | PNG-8 | SVG is resolution-independent and typically <5 KB |
| Simple graphics (few colors) | SVG or PNG-8 | PNG | PNG-8 supports 256 colors, much smaller than PNG-24 |
| Animated content | WebP (animated) | MP4 video | Never use GIF — GIF stores each frame separately |
| Screenshots, UI mockups | WebP | PNG | WebP handles sharp edges and text well |

### Compression Targets
- Quality setting: 80% is the sweet spot for photographs (visually lossless, significant savings)
- If recompressing at 80% reduces file size by more than 20%, the original is unoptimized
- SVGs: remove unused groups, layers, metadata; then compress with SVGO
- Manual optimization + SVGO can reduce SVG files by up to 85%

## Responsive Images

### Vanilla HTML — `<picture>` with format fallback and responsive sizes

```html
<picture>
  <source
    type="image/avif"
    srcset="hero-400.avif 400w, hero-800.avif 800w, hero-1200.avif 1200w"
    sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 600px"
  >
  <source
    type="image/webp"
    srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
    sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 600px"
  >
  <img
    src="hero-800.jpg"
    srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1200.jpg 1200w"
    sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 600px"
    alt="Descriptive text about the image content"
    width="1200"
    height="800"
    loading="lazy"
    decoding="async"
  >
</picture>
```

### Svelte/SvelteKit — Enhanced `<picture>` component

```svelte
<script lang="ts">
  interface Props {
    src: string;
    alt: string;
    width: number;
    height: number;
    sizes?: string;
    loading?: 'lazy' | 'eager';
    widths?: number[];
  }

  let {
    src,
    alt,
    width,
    height,
    sizes = '100vw',
    loading = 'lazy',
    widths = [400, 800, 1200]
  }: Props = $props();

  function srcset(ext: string): string {
    return widths
      .map((w) => `${src.replace(/\.[^.]+$/, '')}-${w}.${ext} ${w}w`)
      .join(', ');
  }
</script>

<picture>
  <source type="image/avif" srcset={srcset('avif')} {sizes}>
  <source type="image/webp" srcset={srcset('webp')} {sizes}>
  <img
    {src}
    srcset={srcset('jpg')}
    {sizes}
    {alt}
    {width}
    {height}
    {loading}
    decoding="async"
  >
</picture>
```

## Lazy Loading Rules

| Position | `loading` value | Reason |
|---|---|---|
| Above the fold / LCP image | `eager` (or omit) | LCP images must load immediately for performance |
| Below the fold | `lazy` | Defers loading until the user scrolls near the image |
| Carousels (non-visible slides) | `lazy` | Only load when the slide becomes visible |
| Background images | Use Intersection Observer | CSS `background-image` does not support `loading` |

Always include explicit `width` and `height` attributes to prevent Cumulative Layout Shift (CLS).

Always include `decoding="async"` to avoid blocking the main thread.

## YouTube / Third-Party Video Facade

Never embed YouTube or Vimeo iframes directly. Use a click-to-load facade to avoid downloading 1-3 MB of third-party resources until the user requests playback.

### Vanilla HTML — YouTube Facade

```html
<div class="video-facade" data-video-id="VIDEO_ID">
  <button
    type="button"
    aria-label="Play video: Video Title"
    class="video-facade__play"
  >
    <img
      src="https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg"
      alt="Video Title"
      width="480"
      height="360"
      loading="lazy"
      decoding="async"
    >
    <svg aria-hidden="true" width="68" height="48" viewBox="0 0 68 48">
      <path d="M66.52 7.74c-.78-2.93-2.49-5.41-5.42-6.19C55.79.13 34 0 34 0S12.21.13 6.9 1.55c-2.93.78-4.64 3.26-5.42 6.19C.06 13.05 0 24 0 24s.06 10.95 1.48 16.26c.78 2.93 2.49 5.41 5.42 6.19C12.21 47.87 34 48 34 48s21.79-.13 27.1-1.55c2.93-.78 4.64-3.26 5.42-6.19C67.94 34.95 68 24 68 24s-.06-10.95-1.48-16.26z" fill="red"/>
      <path d="M45 24L27 14v20" fill="white"/>
    </svg>
  </button>
</div>

<script>
  document.querySelectorAll('.video-facade').forEach((facade) => {
    facade.querySelector('button').addEventListener('click', () => {
      const videoId = facade.dataset.videoId;
      const iframe = document.createElement('iframe');
      iframe.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`;
      iframe.width = '560';
      iframe.height = '315';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      iframe.allowFullscreen = true;
      iframe.title = facade.querySelector('img').alt;
      facade.replaceWith(iframe);
    });
  });
</script>
```

### Svelte — YouTube Facade Component

```svelte
<script lang="ts">
  interface Props {
    videoId: string;
    title: string;
  }

  let { videoId, title }: Props = $props();
  let playing = $state(false);
</script>

{#if playing}
  <iframe
    src="https://www.youtube-nocookie.com/embed/{videoId}?autoplay=1"
    width="560"
    height="315"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
    {title}
  ></iframe>
{:else}
  <button
    type="button"
    aria-label="Play video: {title}"
    class="video-facade"
    onclick={() => (playing = true)}
  >
    <img
      src="https://i.ytimg.com/vi/{videoId}/hqdefault.jpg"
      alt={title}
      width="480"
      height="360"
      loading="lazy"
      decoding="async"
    >
  </button>
{/if}
```

## Self-Hosted Video

When self-hosting video, always use a facade (poster/play button), never autoplay, and provide WebVTT subtitles.

```html
<figure>
  <video
    controls
    preload="none"
    poster="video-poster.jpg"
    width="1280"
    height="720"
  >
    <source src="video.webm" type="video/webm">
    <source src="video.mp4" type="video/mp4">
    <track kind="captions" src="captions-en.vtt" srclang="en" label="English" default>
  </video>
  <figcaption>Description of video content for context</figcaption>
</figure>
```

### Video optimization rules
- Compress with Handbrake or FFmpeg before upload; if recompression reduces size by >20%, the original is unoptimized
- Use WebM as primary format (smaller), MP4 as fallback
- Never autoplay — use `preload="none"` and a poster image
- Keep videos short — every second of video content consumes more data than a full-screen JPEG
- Always provide captions via `<track kind="captions">` with WebVTT files
- Wrap in `<figure>` with `<figcaption>` for semantic context

## Font Loading

### Optimal `@font-face` declaration

```css
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom-font-subset.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0020-007F, U+00A0-00FF; /* Latin + Latin Extended */
}
```

### Font optimization rules
- Use WOFF2 exclusively — it is the most compressed web font format and has universal browser support
- Subset fonts to include only the character sets your content requires (Latin, Latin Extended, etc.)
- Limit to 2 font weights maximum (e.g., regular + bold); use CSS `font-synthesis` for italic if needed
- Always declare a system font fallback stack:
  ```css
  font-family: 'CustomFont', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  ```
- Use `font-display: swap` to prevent invisible text during loading
- Self-host fonts — avoid third-party font subscription services (Adobe Fonts, Fonts.com) that add extra requests and latency
- Consider system fonts for body text, custom fonts only for headings/brand elements
- A single font weight should be <25 KB (subsetted WOFF2); stretch goal <10 KB
- Tools: Font Squirrel Webfont Generator (format conversion), Everything Fonts Subsetter (character stripping), Font Drop (glyph inspection)

## Animation Rules

### Use CSS over JavaScript for animation
CSS animations minimize CPU-to-GPU overhead. Prefer `transform` and `opacity` (compositor-only properties) over animating `width`, `height`, `top`, `left`, or `margin`.

### Respect `prefers-reduced-motion`

```css
/* Full animation by default */
.animated-element {
  animation: slide-in 0.3s ease-out;
  transition: transform 0.2s ease;
}

/* Remove or reduce motion for users who prefer it */
@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: none;
  }
}
```

### Animation performance rules
- Adding a carousel increases peak CPU usage by ~7% vs static images
- Adding a fade-in effect on page load increases peak CPU usage by ~22%
- CPU usage from overlay effects increases proportionally with image size
- Avoid multiple simultaneous overlay/blend-mode effects on the same page
- Never use GIF for animation — use animated WebP, CSS animation, or short MP4 video
- All continuous animations must have a pause/stop control
- Test animation impact using Chrome DevTools Performance tab or Safari Energy Impact monitor
