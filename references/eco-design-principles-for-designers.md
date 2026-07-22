# Eco-Design Principles for Designers

A practical checklist for reducing the environmental impact of your website through design decisions alone — no code required.

---

## Images and media

The biggest single lever. For every image, ask: does it need to be there?

- Replace decorative hero images with CSS gradients, SVG illustrations, or typography where possible.
- Crop tighter and reduce dimensions to what's actually displayed.
- Note in your handoff where modern formats (WebP, AVIF) should be used.
- Push back on auto-playing videos and background videos — they're particularly heavy.

## Typography

Custom web fonts are surprisingly costly.

- Limit font families and weights — two weights of one family is usually plenty.
- Designs with 4–5 weights across two families can often be simplified without losing identity.
- System fonts (or font stacks falling back to them) cost zero bytes.

## Color and contrast

Respect the user's system preference rather than forcing a mode.

- Design your palette around `prefers-color-scheme` — both light and dark themes designed properly, not just one inverted into the other.
- Make sure contrast ratios hold up in both modes.
- A manual toggle is a nice addition if you want to give users control beyond their system setting.
- The OLED energy benefit of dark mode is real but marginal compared to other levers.

## Layout density and scroll length

Long, image-heavy scrolling pages load more content than users often consume.

- Condense sections where possible.
- Question whether infinite scroll is necessary.
- Move secondary content to separate pages that load only if someone wants them.

## Animations and motion

Decorative animations, parallax effects, and constant motion drain battery and CPU.

- Flag where motion adds real value versus where it's just polish.
- Respect `prefers-reduced-motion` for users who've opted out.

## Interaction patterns that reduce repeat loads

Designs that help users find what they need on the first try mean fewer page loads overall.

- Clear navigation.
- Good search.
- Prominent, unambiguous CTAs.

## Component reuse

If your design system has consistent components across pages, browsers can cache and reuse them.

- Note where one-off custom layouts could be replaced by existing patterns.
- Favor reusable components over bespoke ones.

## Text alternatives and graceful degradation

Design with the assumption that images might not load (slow connection, data-saver mode, failed request).

- Specify meaningful alt text in your handoff.
- Provide visual fallbacks: background color or placeholder that holds the layout.
- Write captions that make sense on their own.
- Pair icons with text labels rather than icons alone.

This helps accessibility *and* sustainability — users on poor connections get a usable page faster.

## Lazy-loading-friendly layouts

Design with the expectation that below-the-fold images load only when scrolled into view.

- Avoid designs that require all images to be present immediately (like complex collages above the fold).
- Ensure there's a sensible placeholder state.

## Print and share-friendly pages

If users save, bookmark, or share a page, they're less likely to reload it repeatedly.

- Clear page titles.
- Good URL structure cues in the design.
- Obvious save/bookmark affordances.

## Form efficiency

Every form submission is a server round-trip; reducing failed submissions and abandoned flows means less wasted compute.

- Fewer fields.
- Smarter defaults.
- Inline validation.

## Content hierarchy that loads top-down

Critical content (headline, primary CTA, key info) should live at the top of the page so it renders first and the user can act before the rest finishes loading.

- Avoid designs where the important stuff is buried under heavy hero elements.

## Avoiding tracking-heavy patterns

Designs that imply lots of third-party widgets drag in significant external scripts. Each one is a network request and ongoing CPU cost.

- Question whether social embeds, chat widgets, analytics dashboards, ad slots, and comment systems each earn their place.

## Search over browse

For content-heavy sites, a good search experience uses less energy than browsing through many category pages.

- Design search to be prominent and effective.

## Default to "off" for heavy features

Auto-playing carousels, auto-refreshing feeds, live data updates — design these as opt-in or with sensible pause states rather than running constantly.

## Accessibility (which is also performance)

Accessibility and sustainability solve the same problems with the same fixes. A lightweight site is more likely to be an inclusive site.

- For every image, ask "what does this communicate?" If you can't answer, it's likely decoration, consider replacing it with a CSS-friendly alternative (gradient, shape, type).
- Check every text/background combination with a contrast plugin (Stark, A11y, Contrast). Aim for 4.5:1 on body text, 3:1 on large text.
- Don't rely on color alone to communicate state. Add an icon, a label, or an underline alongside red/green/etc.
- Set minimum tap target sizes to 44×44px for anything clickable on mobile.
- Use real text in your designs, not text baked into images. Text baked into images can't be read by screen readers, can't be translated, and adds image weight.
- Label every form field visibly. Placeholder-only labels disappear when typing and fail for screen readers.
- Design a visible focus state for every interactive element — buttons, links, form fields, checkboxes, dropdowns, tabs. Not just hover. Keyboard users need to see where they are.
- For form fields specifically, design all the states: default, focus, filled, disabled, error (with a clear message, not just a red border), and success. Don't rely on color alone to signal errors — pair with an icon and text.
- Pair every icon with a text label, or note an accessible name in the layer for icon-only buttons.
- Design empty, loading, and error states for every component that fetches or displays data (lists, search results, dashboards, image galleries). Users on slow connections see these often — they shouldn't feel like the site is broken.

---

## Guiding principle

**Design for the worst-case context, not the best one.** A slow 3G connection, a five-year-old Android phone, a slightly outdated browser. If your design works there, it works beautifully everywhere — and uses far less energy doing it.
