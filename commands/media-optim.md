# Media Optimization — Sustainable Video & Audio

Audit and optimize all video and audio assets in this project for minimal bandwidth and controlled loading. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Autoplay Rules

- **No autoplay** on any video or audio element by default.
- **Exception — Hero background video only:** A muted hero/background video MAY autoplay, but it must have ALL four of these attributes:
  - `muted`
  - `loop`
  - `playsinline`
  - `autoplay`
  - And must be heavily compressed (target ≤ 3 MB for a 10-second loop at 1080p).
- Remove `autoplay` from any element that does not qualify as a hero background video.

## 2. Preload

- Set `preload="none"` on every `<video>` and `<audio>` element.
- Remove `preload="auto"` or `preload="metadata"` unless there is a documented performance reason — flag those for review.

## 3. Format Requirements

### Video
- **Primary:** WebM with VP9 or AV1 codec.
- **Fallback:** MP4 with H.264 codec.
- Structure every `<video>` with both `<source>` elements in this order:
  ```html
  <video preload="none" poster="poster.webp">
    <source src="video.webm" type="video/webm" />
    <source src="video.mp4" type="video/mp4" />
    <track kind="captions" src="captions.vtt" srclang="en" label="English" />
  </video>
  ```

### Audio
- **Primary:** Opus (`.opus` or `.ogg` container).
- **Fallback:** MP3.
- Structure every `<audio>` with both `<source>` elements:
  ```html
  <audio preload="none" controls>
    <source src="audio.opus" type="audio/ogg; codecs=opus" />
    <source src="audio.mp3" type="audio/mpeg" />
  </audio>
  ```

## 4. Accessibility

- Every `<video>` must include a `<track>` element pointing to a `.vtt` captions file.
- Every `<audio>` element must have a visible transcript linked or embedded nearby.
- If captions or transcripts do not exist yet, output a TODO comment and note the file paths needed.

## 5. Third-Party Embeds (YouTube, Vimeo, etc.)

- **Never load an iframe on page load.** Always use a click-to-load facade pattern:
  1. Show a thumbnail/poster image and a play button UI.
  2. Only inject the `<iframe>` after the user clicks
  3. The `<iframe>` should visually replace the facade.
  4. The facade should have the same form/ratio than the iframe
- For YouTube specifically:
  - Use `youtube-nocookie.com` instead of `youtube.com`.
  - Append `?rel=0&modestbranding=1` to the embed URL.
- Provide a facade implementation using a `<button>` wrapping the poster image, with a JavaScript click handler that replaces the button with the iframe.
- Example pattern:
  ```html
  <div class="video-facade" data-src="https://www.youtube-nocookie.com/embed/VIDEO_ID?rel=0">
    <img src="poster.webp" alt="Video title — click to play" loading="lazy" />
    <button class="play-btn" aria-label="Play video">▶</button>
  </div>
  ```
  ```js
  document.querySelectorAll('.video-facade').forEach(facade => {
    facade.querySelector('.play-btn').addEventListener('click', () => {
      const iframe = document.createElement('iframe');
      iframe.src = facade.dataset.src + '&autoplay=1';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      iframe.allowFullscreen = true;
      facade.replaceWith(iframe);
    });
  });
  ```

## 6. Decorative Videos

- Identify any video used purely for decoration (no meaningful content, no captions needed).
- If the video is short (≤ 5 seconds), looping, and decorative, recommend replacing it with an **animated WebP** or **animated AVIF** and note the ffmpeg command to convert it:
  ```bash
  ffmpeg -i input.mp4 -vf "fps=15,scale=800:-1" -loop 0 output.webp
  ```
- If replacement is not suitable, ensure the decorative video still uses `preload="none"` and has `aria-hidden="true"`.

## 7. Low Bandwidth Mode

- If the project does not already have a low-bandwidth mode, suggest adding one using `prefers-reduced-data` media query or a user-toggled CSS class:
  ```css
  @media (prefers-reduced-data: reduce) {
    video,
    .video-facade img {
      display: none;
    }
  }
  ```
- Optionally add a visible "Low bandwidth mode" toggle button that adds a `.low-bandwidth` class to `<html>` and persists the preference in `localStorage`.

## 8. Hosting & Streaming

- **Self-host whenever possible.** Flag any video/audio loaded from a CDN or third-party host (other than the facade pattern above) for review.
- Only recommend HLS (`.m3u8`) or DASH if the video is longer than 10 minutes or requires DRM. For those cases, note the tooling needed (e.g., `hls.js`, Shaka Player).
- If self-hosting is not feasible, document why.

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied
List every file modified and what changed.

### ⚠️ Manual Actions Required
List items that require human action (e.g., creating missing `.vtt` files, compressing source videos, generating WebP alternatives). Include exact file paths and recommended commands.

### ffmpeg Reference Commands
Provide copy-paste ffmpeg commands for any conversions needed:
- MP4 → WebM (VP9): `ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 33 -b:v 0 -c:a libopus output.webm`
- MP4 → WebM (AV1): `ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 -c:a libopus output.webm`
- MP4 → Animated WebP: `ffmpeg -i input.mp4 -vf "fps=15,scale=800:-1" -loop 0 output.webp`
- Audio → Opus: `ffmpeg -i input.mp3 -c:a libopus -b:a 64k output.opus`

### 📊 Estimated Bandwidth Impact
Give a rough before/after estimate of bytes transferred per page load where measurable.
