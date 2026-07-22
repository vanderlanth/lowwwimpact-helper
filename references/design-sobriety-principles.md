# Design Sobriety Principles

Higher-level design principles for low-carbon websites. Where the per-screen checklist
(`eco-design-principles-for-designers.md`) catalogs tactical fixes, this file captures the
*mindset* — the questions a designer asks before a single element is placed. Use it to
write the closing "Design Sobriety" section of a Mode 5 review: map each principle below
against what was actually found in the analyzed screens, and only surface the ones that
apply.

---

## Justify every element

The default should be *absence*, not presence. Instead of asking "would this be nice to
add?", ask "can the page do its job without it?" — and when the answer is unclear, leave it
out. Bloat usually comes from a fear of missing something, a reluctance to say no to a
stakeholder, or the comfort of fast connections hiding the cost. Treat a minimal design as
the goal, not a fallback: every image, block, page, and script has to earn its place by
serving the user. Minimal does not mean bare or ugly — it means nothing is present that
isn't pulling its weight.

## Simplify the journey, not just the page

Information architecture and UX decide how much a site loads long before code or hosting
enter the picture. The earlier inefficiency is designed out, the cheaper it is.

- **Cut wasted page loads.** Total data moved is a product of page weight × visitors ×
  pages-per-visit. Shortening the path to what the user actually wants attacks the last
  factor directly. Removing one intermediate step from a common journey scales across every
  visitor who takes it.
- **Kill gateway pages.** If people know what they want, don't force them through decorative
  landing or category pages to reach it. Surface subcategories in the menu, offer a
  prominent search box, and let users jump straight to the destination.
- **Notice "yoyo" journeys.** When users bounce repeatedly back to the homepage, that's a
  navigation-confidence problem — they're using home as their only reliable orientation
  point. Better wayfinding (and patterns like an overlay cart instead of a separate cart
  page) removes those round-trips.
- **Audit and retire content.** Content multiplies over a site's life; stale pages keep
  consuming storage and energy while making the site heavier and harder to use. Schedule
  content reviews the same way you schedule technical maintenance, and remove what no longer
  serves anyone.
- **Read bounce rate in context.** A bounce isn't automatically bad. Someone who finds their
  answer on the first page and leaves is an efficiency *win*. A bounce is a problem only when
  it signals a mismatch — content that attracts the wrong audience, a page that hides what
  users came for, or a page too slow to load before they give up.

## Make imagery lightweight

Images are the single biggest carbon contributor on most sites, so this is the highest-
leverage design lever.

- **Question each image first.** Before optimizing, decide whether the image belongs at all.
  Stock photography and decorative filler rarely add real value; text and space often
  communicate more efficiently.
- **Choose efficient formats.** Prefer WebP or AVIF for photographs, PNG/GIF for flat few-
  color graphics like icons and logos, and MP4 over animated GIF for anything moving.
- **Compress everything.** Run images through compression tooling (and ideally automate it in
  the build/CMS so uploads and generated thumbnails are optimized without manual effort).
- **Serve at display size.** File size grows roughly with the square of dimensions, so an
  oversized image is disproportionately expensive. Use responsive images (`srcset`/`sizes`)
  to hand each device an appropriately sized version.
- **Reach for vectors and CSS.** SVG illustrations, CSS gradients, and CSS styling can
  replace heavy raster imagery entirely while staying crisp at any size. Hand-optimizing
  then compressing SVGs shrinks them dramatically.
- **Use blur and crop deliberately.** Softening non-essential areas (shallow depth of field,
  blurred edges) and cropping tighter both cut file size, and generous whitespace can make a
  smaller image feel *more* impactful, not less.

## Weigh the cost of color

Color affects energy in two distinct ways.

- **Screen draw.** On OLED displays each pixel is its own light, so dark pixels cost almost
  nothing and white costs the most; blue pixels draw noticeably more than red or green.
  Where brand guidelines allow, lean toward darker palettes with less heavy blue — it saves
  device energy and extends battery life. (The effect only applies to OLED and is modest
  next to imagery, so treat it as a tiebreaker, not a mandate.)
- **File size.** More color variation means larger image files. Monochrome and grayscale
  imagery generally produces smaller files across the whole network; CSS blend modes can
  even re-tint a small grayscale asset in the browser to fake full color — though that shifts
  cost onto CPU, so measure before assuming it's a net win.

## Be mindful with motion

Motion can sharpen an experience or drain a battery, confuse users, and burn CPU. Use it
only where it earns its cost.

- **Respect the reduced-motion preference.** Honor `prefers-reduced-motion` so users who opt
  out get a calmer, lower-power experience.
- **Avoid needless video.** Video, once present, tends to dominate a page's footprint.
  Skip it when it isn't the point; when content genuinely wants to be watched, keep clips
  short, compress hard, and never autoplay — put a play button in front so bytes load only
  on intent (also better for motion-sensitive users).
- **Prefer interactive animation to video** for explaining processes — lightweight,
  code-driven animation (e.g. Lottie) can be a fraction of a video's weight while offering
  better accessibility and control.
- **Treat GIFs as a last resort.** Animated GIFs store every frame as a full image and are
  wildly inefficient; a short video or animated WebP is almost always lighter.
- **Budget the "icing."** Hover effects, scroll animations, carousels, and fade-ins feel
  effortless but can spike CPU and drain batteries. Test the energy and file-size cost of
  each flourish and keep only those that genuinely improve the experience.

## Use typography efficiently

Web fonts expand creative range but add data transfer and requests.

- **Default to system fonts.** Fonts already installed on the device (Arial, Helvetica,
  Times New Roman, Roboto, etc.) cost zero bytes and zero requests. The trade-off is less
  control over presentation.
- **Spend custom fonts where they count.** Headings and menus carry more visual weight than
  body text, so a distinctive display face there — with system fonts for body copy — often
  captures most of the design value at a fraction of the cost.
- **Self-host over subscription services.** Hosting font files yourself avoids extra third-
  party requests and keeps optimization in your hands (subscription/CDN font services add
  weight and limit tuning).
- **Cut the number of weights.** Each weight is usually a separate file. Few designs truly
  need light, regular, semibold, bold, *and* black — trim to what's used. Where wide
  variation is genuinely needed, a single variable font can replace many static files.

---

## Further reading

These principles draw on ideas popularized in *Sustainable Web Design* by Tom Greenwood
(A Book Apart, No. 34, 2021) — recommended for the fuller argument and worked examples.
