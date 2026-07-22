# Figma Eco-Design Specs

| Title | Spec |
|---|---|
| Keyboard Accessibility | Provide "Skip to content" on pages with repeated navigation |
| Animation/motion | Respect `prefers-reduced-motion` (reduce/disable non-essential motion) |
| Live content/Feed refresh | Avoid aggressive polling/background refresh; update on user action or sensible intervals |
| Cookies | Choices must be clear, non-manipulative, and fully accessible (keyboard + screen reader)<br>No non-essential cookies / third-party requests before consent<br>Users can review/change/revoke their choice anytime, like on liip.ch privacy policy page. |
| Fonts | Self-host the fonts<br>Provide a system font fallback<br>Subset fonts to reduce filesize.<br>Use woff2 whenever possible |
| Icons/illustrations | Prefer SVG over icon fonts or large raster images |
| Images | Use responsive sources (`srcset`/`sizes`) and serve AVIF/WebP with JPG/PNG fallback<br>Use `loading="lazy"` + `decoding="async"` (where appropriate)<br>Only hero/critical images could use `loading="eager"`<br>Mark decorative images as such (empty `alt` and/or `aria-hidden="true"`)<br>Set `width`/`height` or `aspect-ratio` to prevent layout shift<br>Avoid oversized assets; serve appropriately resized versions per breakpoint |
| Third-party | Prefer self-hosted icons/widgets/assets over vendor-hosted where feasible<br>Third-party embeds (iframes): use `loading="lazy"` + restrictive `sandbox`/`allow` permissions (only what's needed)<br>Hide third-party content behind a facade (static self-hosted preview + CTA) to avoid useless network request and bandwidth usage unless the user wants to access it |
| Videos/Audios | Providing transcripts is recommended where content is informational<br>For informational content, prefer a third-party as it requires less work on maintenance and work on accessibility/compatibility<br>No autoplay nor pre-loading, exception could be made for a hero on a homepage |
| Youtube | Embed via `youtube-nocookie.com` (not `youtube.com`) |
| Lite-mode (advanced) | By detecting slow internet speed (like after 10 seconds of loading time using the network API) or device on data saving mode, you could:<br>- Hide decorative images<br>- Replace non-decorative media with their alt text, with a button allowing user to load the full image<br>- Replace third-party embeds with a light alternative like an alt text as well, with a button allowing user to load the full image<br>- Replace videos with poster images<br>- Add banner indicating the user has a slow-connection, giving the choice to access the normal version of the website anyway (like a happy browser.) |
| CMS Constraints | Enforce max upload weight & dimensions; auto-generate renditions (thumb/medium/large). Offer editor guidance (e.g. recommended aspect ratios).<br>Add short helper text regarding media contribution: "Use media only if it adds meaning; prefer vector/icons; keep images concise." |
| CMS Constraints | Set content limits to prevent bloat when building pages with blocks and rich texts, such as: max number of blocks, max gallery images, max embed count, max hero size.<br>Encourage reuse of shared blocks/assets. |
| Carousel & Galleries | Don't download all slides upfront. Load first slide only; lazy-load the rest on interaction/near-viewport. Reduce non-visible images. |
