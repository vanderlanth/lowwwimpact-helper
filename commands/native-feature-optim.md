# Native Features — Prefer HTML/CSS Over JavaScript

Audit and refactor this project to replace JavaScript-powered UI components with native HTML elements and CSS equivalents. Eliminate library dependencies for patterns the platform already solves. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. `<details>` / `<summary>` — Replace Custom Accordions

Any accordion built with `div` + click handler + `aria-expanded` can be replaced with `<details>` / `<summary>`. The browser handles toggle state, keyboard interaction, and accessibility with zero JavaScript.

### 1.1 Migration Pattern

```html
<!-- Before: custom accordion (~30 lines JS + ARIA management) -->
<div class="accordion">
  <button class="accordion__trigger" aria-expanded="false" aria-controls="panel-1">
    What is your return policy?
  </button>
  <div id="panel-1" class="accordion__panel" hidden>
    <p>We accept returns within 30 days…</p>
  </div>
</div>

<!-- After: native, zero JS, fully accessible -->
<details class="accordion">
  <summary class="accordion__trigger">What is your return policy?</summary>
  <div class="accordion__panel">
    <p>We accept returns within 30 days…</p>
  </div>
</details>
```

### 1.2 Styled with Animation

```css
/* Remove default marker and restyle */
details.accordion {
  border: 1px solid var(--color-border, hsl(220 14% 88%));
  border-radius: var(--radius-md, 0.5rem);
  overflow: hidden;
}

details.accordion + details.accordion {
  margin-top: -1px; /* collapse borders between items */
}

details.accordion summary {
  list-style: none; /* remove default triangle */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  cursor: pointer;
  font-weight: 600;
  user-select: none;
  gap: 1rem;
}

details.accordion summary::-webkit-details-marker { display: none; }

/* Custom chevron via CSS — no icon library needed */
details.accordion summary::after {
  content: '';
  width: 0.625rem;
  height: 0.625rem;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg);
  transition: transform 200ms ease;
  flex-shrink: 0;
}

details.accordion[open] summary::after {
  transform: rotate(-135deg);
}

details.accordion summary:focus-visible {
  outline: 2px solid var(--color-brand, hsl(220 90% 56%));
  outline-offset: -2px;
}

.accordion__panel {
  padding: 0 1.25rem 1.25rem;
}

/* Smooth open/close with CSS interpolate-size (progressive) */
@supports (interpolate-size: allow-keywords) {
  details.accordion {
    interpolate-size: allow-keywords;
  }

  details.accordion .accordion__panel {
    block-size: 0;
    overflow: hidden;
    transition: block-size 250ms ease, padding 250ms ease;
    padding-block: 0;
  }

  details.accordion[open] .accordion__panel {
    block-size: auto;
    padding-block-end: 1.25rem;
  }
}
```

### 1.3 Exclusive Accordion (One Open at a Time)

Add the `name` attribute — all `<details>` sharing the same `name` behave as a mutually exclusive group (Chrome 120+). For older browsers this degrades gracefully to independent panels:

```html
<details name="faq" class="accordion">
  <summary class="accordion__trigger">Question one</summary>
  <div class="accordion__panel"><p>Answer one.</p></div>
</details>

<details name="faq" class="accordion">
  <summary class="accordion__trigger">Question two</summary>
  <div class="accordion__panel"><p>Answer two.</p></div>
</details>
```

### 1.4 Svelte Component

```svelte
<!-- src/components/Accordion.svelte -->
<script>
  let { items, exclusive = false } = $props();
  const name = exclusive ? `accordion-${Math.random().toString(36).slice(2)}` : undefined;
</script>

{#each items as item}
  <details class="accordion" {name}>
    <summary class="accordion__trigger">{item.question}</summary>
    <div class="accordion__panel">
      {@html item.answer}
    </div>
  </details>
{/each}
```

### 1.5 Detection: Find Custom Accordion JS

```bash
# Find likely custom accordion patterns in source
grep -rn --include="*.js" --include="*.ts" --include="*.svelte" --include="*.vue" \
  -E "aria-expanded|accordion|\.toggle\(\)|\.classList\.toggle" src/
```

Any `aria-expanded` toggle managed by JavaScript is a candidate for replacement with `<details>`.

---

## 2. `<dialog>` — Replace Custom Modals and Drawers

The `<dialog>` element provides a fully accessible modal with a built-in focus trap, `Escape` key handling, backdrop rendering, and `inert` management on the rest of the document — all without any JavaScript modal library.

### 2.1 Migration Pattern

```html
<!-- Before: custom modal (~80 lines JS for focus trap, escape, scroll lock, ARIA) -->
<div class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal">
    <h2 id="modal-title">Confirm action</h2>
    <p>Are you sure?</p>
    <button class="modal__close" aria-label="Close">×</button>
  </div>
</div>

<!-- After: native <dialog>, browser handles all of the above -->
<dialog class="modal" aria-labelledby="modal-title">
  <h2 id="modal-title">Confirm action</h2>
  <p>Are you sure?</p>
  <form method="dialog">
    <button>Close</button>
  </form>
</dialog>
```

### 2.2 Opening and Closing

```js
const dialog = document.querySelector('#my-dialog');

// True modal: backdrop rendered, focus trapped, rest of page inert
dialog.showModal();

// Non-modal: visible but page remains interactive (for side panels, popovers)
dialog.show();

// Close programmatically (also fires 'close' event)
dialog.close();
dialog.close('confirmed'); // optional return value string
```

### 2.3 Close on Backdrop Click

The `<dialog>` backdrop is not part of the dialog's content box. Clicking it does not close the dialog by default — add one listener:

```js
dialog.addEventListener('click', e => {
  const rect = dialog.getBoundingClientRect();
  const outside = e.clientX < rect.left || e.clientX > rect.right
               || e.clientY < rect.top  || e.clientY > rect.bottom;
  if (outside) dialog.close();
});
```

### 2.4 Styling

```css
dialog.modal {
  border: none;
  border-radius: var(--radius-lg, 0.75rem);
  padding: 2rem;
  max-width: min(90vw, 32rem);
  width: 100%;
  box-shadow: 0 8px 32px hsl(0 0% 0% / 0.2);
}

/* Backdrop */
dialog.modal::backdrop {
  background: hsl(220 20% 12% / 0.6);
  backdrop-filter: blur(2px);
}

/* Entry animation using @starting-style (Chrome 117+, Firefox 129+) */
@supports (animation-timeline: scroll()) {
  dialog.modal {
    transition: opacity 200ms ease, transform 200ms ease, overlay 200ms ease allow-discrete, display 200ms ease allow-discrete;
    transform: translateY(0);
    opacity: 1;
  }

  @starting-style {
    dialog.modal[open] {
      opacity: 0;
      transform: translateY(1rem);
    }
  }

  dialog.modal::backdrop {
    transition: opacity 200ms ease, overlay 200ms ease allow-discrete, display 200ms ease allow-discrete;
    opacity: 1;
  }

  @starting-style {
    dialog.modal[open]::backdrop {
      opacity: 0;
    }
  }
}
```

### 2.5 Svelte Component

```svelte
<!-- src/components/Dialog.svelte -->
<script>
  let { open = $bindable(false), title, onclose, children } = $props();

  let dialog = $state();

  $effect(() => {
    if (!dialog) return;
    if (open) dialog.showModal();
    else       dialog.close();
  });

  function handleClose() {
    open = false;
    onclose?.();
  }

  function handleBackdropClick(e) {
    const rect = dialog.getBoundingClientRect();
    if (
      e.clientX < rect.left || e.clientX > rect.right ||
      e.clientY < rect.top  || e.clientY > rect.bottom
    ) handleClose();
  }
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<dialog
  class="modal"
  bind:this={dialog}
  aria-labelledby={title ? 'dialog-title' : undefined}
  onclose={handleClose}
  onclick={handleBackdropClick}
>
  <!-- Stop click events from the content propagating to the backdrop listener -->
  <div class="modal__inner" role="presentation" onclick={e => e.stopPropagation()}>
    {#if title}
      <h2 id="dialog-title" class="modal__title">{title}</h2>
    {/if}

    <div class="modal__body">
      {@render children()}
    </div>

    <form method="dialog" class="modal__footer">
      <button class="modal__close" aria-label="Close dialog">Close</button>
    </form>
  </div>
</dialog>

<style>
  .modal {
    border: none;
    border-radius: var(--radius-lg, 0.75rem);
    padding: 0;
    max-width: min(90vw, 32rem);
    width: 100%;
    box-shadow: 0 8px 32px hsl(0 0% 0% / 0.2);
  }

  .modal::backdrop {
    background: hsl(220 20% 12% / 0.6);
    backdrop-filter: blur(2px);
  }

  .modal__inner  { padding: 2rem; }
  .modal__title  { margin: 0 0 1rem; font-size: 1.25rem; }
  .modal__body   { margin-bottom: 1.5rem; }
  .modal__footer { display: flex; justify-content: flex-end; }

  .modal__close {
    padding: 0.5rem 1.25rem;
    background: var(--color-brand, hsl(220 90% 56%));
    color: #fff;
    border: none;
    border-radius: var(--radius-md, 0.5rem);
    font-weight: 600;
    cursor: pointer;
  }
</style>
```

**Usage:**

```svelte
<script>
  let showDialog = $state(false);
</script>

<button onclick={() => showDialog = true}>Open</button>

<Dialog bind:open={showDialog} title="Confirm action">
  <p>Are you sure you want to continue?</p>
</Dialog>
```

### 2.6 Detection: Find Custom Modal JS

```bash
grep -rn --include="*.js" --include="*.ts" --include="*.svelte" --include="*.vue" \
  -E "aria-modal|modal.*show|modal.*open|focusTrap|trapFocus|\.modal\b" src/
```

---

## 3. CSS Scroll Snap — Replace Custom Sliders and Carousels

CSS `scroll-snap-type` replaces most carousel and slider libraries. The browser handles touch swipe, keyboard arrow navigation, and scroll physics natively. Add minimal JavaScript only for dot indicators or programmatic scrolling — never for the core scroll behaviour.

### 3.1 Horizontal Carousel

```html
<div class="carousel" role="region" aria-label="Product images">
  <ul class="carousel__track">
    <li class="carousel__slide"><img src="..." alt="Product view 1" /></li>
    <li class="carousel__slide"><img src="..." alt="Product view 2" /></li>
    <li class="carousel__slide"><img src="..." alt="Product view 3" /></li>
  </ul>
</div>
```

```css
.carousel {
  overflow: hidden;               /* clip overflow; scrollbar hidden below */
}

.carousel__track {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  gap: var(--space-4, 1rem);
  padding: 0;
  margin: 0;
  list-style: none;

  /* Hide scrollbar visually while keeping scroll functionality */
  scrollbar-width: none;
}

.carousel__track::-webkit-scrollbar { display: none; }

.carousel__slide {
  flex: 0 0 100%;                 /* full-width slides; change to e.g. 80% for peek */
  scroll-snap-align: start;
  scroll-snap-stop: always;       /* prevent momentum scroll skipping slides */
}

.carousel__slide img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: var(--radius-md, 0.5rem);
}
```

### 3.2 Optional: Prev/Next Buttons and Dot Indicators

Add buttons only if UX requires them — touch and keyboard already work without them:

```js
// scripts/carousel.js — minimal, no framework required
export function initCarousel(container) {
  const track  = container.querySelector('.carousel__track');
  const slides = [...container.querySelectorAll('.carousel__slide')];
  const prev   = container.querySelector('[data-carousel-prev]');
  const next   = container.querySelector('[data-carousel-next]');
  const dots   = container.querySelectorAll('[data-carousel-dot]');

  function currentIndex() {
    const w = track.offsetWidth;
    return Math.round(track.scrollLeft / w);
  }

  function scrollTo(index) {
    track.scrollTo({ left: index * track.offsetWidth, behavior: 'smooth' });
  }

  prev?.addEventListener('click', () => scrollTo(Math.max(0, currentIndex() - 1)));
  next?.addEventListener('click', () => scrollTo(Math.min(slides.length - 1, currentIndex() + 1)));
  dots.forEach((dot, i) => dot.addEventListener('click', () => scrollTo(i)));

  // Update active dot on scroll
  const observer = new IntersectionObserver(
    entries => entries.forEach(e => {
      if (!e.isIntersecting) return;
      const i = slides.indexOf(e.target);
      dots.forEach((d, j) => d.setAttribute('aria-current', j === i ? 'true' : 'false'));
    }),
    { root: track, threshold: 0.5 }
  );

  slides.forEach(slide => observer.observe(slide));
}
```

### 3.3 Svelte Component

```svelte
<!-- src/components/Carousel.svelte -->
<script>
  let { items, label = 'Carousel' } = $props();

  let track    = $state();
  let current  = $state(0);

  function scrollTo(index) {
    current = Math.max(0, Math.min(items.length - 1, index));
    track?.scrollTo({ left: current * track.offsetWidth, behavior: 'smooth' });
  }

  function onScroll() {
    if (!track) return;
    current = Math.round(track.scrollLeft / track.offsetWidth);
  }
</script>

<div class="carousel" role="region" aria-label={label}>
  <ul class="carousel__track" bind:this={track} onscroll={onScroll}>
    {#each items as item, i}
      <li class="carousel__slide" aria-label="Slide {i + 1} of {items.length}">
        {@render item()}
      </li>
    {/each}
  </ul>

  {#if items.length > 1}
    <div class="carousel__controls">
      <button
        class="carousel__btn"
        onclick={() => scrollTo(current - 1)}
        disabled={current === 0}
        aria-label="Previous slide"
      >‹</button>

      <div class="carousel__dots" role="tablist" aria-label="Slides">
        {#each items as _, i}
          <button
            class="carousel__dot"
            class:active={i === current}
            role="tab"
            aria-selected={i === current}
            aria-label="Go to slide {i + 1}"
            onclick={() => scrollTo(i)}
          ></button>
        {/each}
      </div>

      <button
        class="carousel__btn"
        onclick={() => scrollTo(current + 1)}
        disabled={current === items.length - 1}
        aria-label="Next slide"
      >›</button>
    </div>
  {/if}
</div>
```

---

## 4. Native Form Validation — Replace Custom Validation Libraries

HTML5 constraint validation covers the majority of form validation use cases with zero JavaScript: required fields, email format, URL format, number ranges, pattern matching, and length limits. The browser renders error messages in the user's language automatically.

### 4.1 Native Constraints

```html
<form>
  <!-- Required text -->
  <input type="text" name="name" required minlength="2" maxlength="100" />

  <!-- Email format — browser validates MX-style format -->
  <input type="email" name="email" required />

  <!-- URL -->
  <input type="url" name="website" placeholder="https://" />

  <!-- Number range -->
  <input type="number" name="quantity" min="1" max="99" step="1" required />

  <!-- Pattern match — e.g. UK postcode -->
  <input type="text" name="postcode" pattern="[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}" />

  <!-- Date range -->
  <input type="date" name="departure" min="2025-01-01" required />

  <!-- Telephone — pattern for custom format -->
  <input type="tel" name="phone" pattern="\+?[0-9\s\-()]{7,15}" />
</form>
```

### 4.2 CSS Validation States

Style validated state without JavaScript using `:user-valid` / `:user-invalid` (only fires after the user has interacted with the field — avoids red borders on untouched inputs):

```css
/* Only show state after user interaction */
input:user-valid {
  border-color: hsl(140 60% 36%);
  outline-color: hsl(140 60% 36%);
}

input:user-invalid {
  border-color: hsl(0 72% 51%);
  outline-color: hsl(0 72% 51%);
}

/* Fallback for browsers without :user-valid (use :focus + :invalid) */
@supports not selector(:user-valid) {
  input:not(:placeholder-shown):valid   { border-color: hsl(140 60% 36%); }
  input:not(:placeholder-shown):invalid { border-color: hsl(0 72% 51%); }
}

/* Inline error message — shown only when input is invalid after blur */
input:user-invalid + .field-error {
  display: block;
}

.field-error {
  display: none;
  color: hsl(0 72% 51%);
  font-size: 0.8125rem;
  margin-top: 0.25rem;
}
```

### 4.3 Custom Error Messages

Override the browser's default message text with `setCustomValidity()` for branded, specific error copy:

```js
// src/lib/validation.js
export function initCustomMessages(form) {
  form.querySelectorAll('[data-custom-validity]').forEach(input => {
    const messages = JSON.parse(input.dataset.customValidity);

    input.addEventListener('invalid', () => {
      const validity = input.validity;

      if (validity.valueMissing)    return input.setCustomValidity(messages.required  ?? '');
      if (validity.typeMismatch)    return input.setCustomValidity(messages.type      ?? '');
      if (validity.patternMismatch) return input.setCustomValidity(messages.pattern   ?? '');
      if (validity.tooShort)        return input.setCustomValidity(messages.minlength ?? '');
      if (validity.tooLong)         return input.setCustomValidity(messages.maxlength ?? '');
      if (validity.rangeUnderflow)  return input.setCustomValidity(messages.min       ?? '');
      if (validity.rangeOverflow)   return input.setCustomValidity(messages.max       ?? '');
      input.setCustomValidity('');
    });

    input.addEventListener('input', () => input.setCustomValidity(''));
  });
}
```

### 4.4 Progressive Enhancement — Styled Validation with JS

When the browser's validation popup UI does not match the design system, suppress it and render errors in custom elements using the Constraint Validation API. This keeps all validation logic in HTML attributes — the JS only controls presentation:

```js
// src/lib/styled-validation.js
export function initStyledValidation(form) {
  form.setAttribute('novalidate', '');

  form.addEventListener('submit', e => {
    if (!form.checkValidity()) {
      e.preventDefault();
      showAllErrors(form);
      form.querySelector(':invalid')?.focus();
    }
  });

  form.querySelectorAll('input, textarea, select').forEach(input => {
    input.addEventListener('blur', () => showError(input));
    input.addEventListener('input', () => clearError(input));
  });
}

function showError(input) {
  clearError(input);
  if (input.validity.valid) return;

  const errorEl = input.closest('.field')?.querySelector('.field-error');
  if (errorEl) {
    errorEl.textContent = input.validationMessage;
    errorEl.style.display = 'block';
    input.setAttribute('aria-describedby', errorEl.id || (errorEl.id = `err-${input.name}`));
    input.setAttribute('aria-invalid', 'true');
  }
}

function clearError(input) {
  const errorEl = input.closest('.field')?.querySelector('.field-error');
  if (errorEl) {
    errorEl.textContent = '';
    errorEl.style.display = 'none';
    input.removeAttribute('aria-describedby');
    input.removeAttribute('aria-invalid');
  }
}

function showAllErrors(form) {
  form.querySelectorAll('input, textarea, select').forEach(showError);
}
```

### 4.5 Detection: Find Custom Validation Libraries

```bash
# Find common JS validation library signatures
grep -rn --include="*.js" --include="*.ts" --include="*.json" \
  -E "validate\.js|vee-validate|yup|joi|zod.*schema|formik" src/ package.json

# Find manual validation patterns that native constraints could replace
grep -rn --include="*.js" --include="*.ts" --include="*.svelte" \
  -E "\.test\(.*email|regex.*email|isEmail\(|validateEmail" src/
```

---

## 5. Other Native Replacements

### 5.1 Popover API — Tooltips and Dropdowns

Replace JS-positioned tooltip and dropdown libraries with the native Popover API (Chrome 114+, Firefox 125+, Safari 17+). Progressive enhancement: falls back to a visible block on older browsers.

```html
<!-- Trigger -->
<button popovertarget="my-tooltip" popovertargetaction="toggle">
  Help
</button>

<!-- Popover — positioned in the top layer automatically -->
<div id="my-tooltip" popover role="tooltip">
  This field is required for account creation.
</div>
```

### 5.2 CSS-Only Toggle / Switch

Replace JS-managed toggle switches with a styled `<input type="checkbox">`:

```html
<label class="toggle" aria-label="Enable notifications">
  <input type="checkbox" class="toggle__input" role="switch" />
  <span class="toggle__track" aria-hidden="true"></span>
</label>
```

### 5.3 Native Date, Time, and Color Inputs

Replace date/time picker libraries and color picker libraries with native inputs:

```html
<!-- Date picker (replaces flatpickr, Pikaday, react-datepicker, etc.) -->
<input type="date" name="dob" min="1900-01-01" max="2099-12-31" />

<!-- Date + time (ISO format) -->
<input type="datetime-local" name="appointment" />

<!-- Time only -->
<input type="time" name="alarm" min="09:00" max="18:00" step="900" />

<!-- Color picker (replaces color picker libraries for non-critical uses) -->
<input type="color" name="theme-color" value="#0070f3" />

<!-- Range slider (replaces JS slider libraries) -->
<input type="range" name="volume" min="0" max="100" step="5" value="50" />
```

### 5.4 `<progress>` and `<meter>` Elements

Replace JS-drawn progress bars and gauge components:

```html
<!-- Progress bar (indeterminate or determinate) -->
<label for="upload-progress">Uploading…</label>
<progress id="upload-progress" value="65" max="100">65%</progress>

<!-- Meter — for scalar measurements with known range and thresholds -->
<label for="disk-usage">Disk usage</label>
<meter id="disk-usage" value="0.72" min="0" max="1" low="0.5" high="0.8" optimum="0.2">
  72%
</meter>
```

### 5.5 `position: sticky` — Replace JS Scroll Listeners

Replace JavaScript scroll listeners that pin headers, sidebars, or section labels:

```css
/* Sticky header — no JS needed */
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-surface, #fff);
}

/* Sticky sidebar table of contents */
.toc {
  position: sticky;
  top: 2rem;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
}
```

```bash
# Find scroll listeners that may be position: sticky candidates
grep -rn --include="*.js" --include="*.ts" --include="*.svelte" \
  -E "addEventListener.*scroll|window\.scroll|onscroll" src/
```

### 5.6 `IntersectionObserver` — Replace Scroll-Position JS

For scroll-triggered animations and lazy effects, always prefer `IntersectionObserver` over `scroll` event listeners with `getBoundingClientRect()`:

```js
// IntersectionObserver — fires only when element enters/exits viewport
const observer = new IntersectionObserver(
  entries => entries.forEach(e => e.target.classList.toggle('visible', e.isIntersecting)),
  { threshold: 0.15 }
);

document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el));
```

### 5.7 `loading="lazy"` — Replace JS Lazy Loaders

```html
<!-- Native — no JS library needed -->
<img src="photo.jpg" alt="..." loading="lazy" decoding="async" />
<iframe src="..." loading="lazy"></iframe>
```

```bash
# Find JS lazy loader library signatures
grep -rn --include="*.js" --include="*.ts" --include="*.json" \
  -E "lazysizes|lozad|lazyload|vanilla-lazyload|data-src=" src/ package.json
```

---

## 6. Progressive Enhancement Rules

### 6.1 Decision Table

| Pattern | Native solution | When to add JS |
|---|---|---|
| Accordion | `<details>` + `<summary>` | Only for animated close (CSS `interpolate-size` covers most cases) |
| Modal | `<dialog>` + `showModal()` | Backdrop click to close (one `click` listener) |
| Carousel | CSS `scroll-snap` | Prev/next buttons, dot indicators, autoplay |
| Form validation | HTML5 constraints + CSS `:user-invalid` | Custom error placement, cross-field validation |
| Tooltip | `popover` API or CSS `[data-tooltip]::after` | Complex positioning |
| Toggle / switch | `<input type="checkbox">` + CSS | Persisting state to server |
| Sticky header | `position: sticky` | Height changes requiring CSS variable updates |
| Scroll reveal | `IntersectionObserver` | Never needs a library |
| Lazy images | `loading="lazy"` | Never needs a library for standard images |
| Date picker | `<input type="date">` | Complex calendars (multi-select, disabled dates, custom ranges) |
| Progress bar | `<progress>` element | Animated streaming progress fed by JS |

---

## 7. Audit, Detection, and CI

### 7.1 Audit Script — Detect Replaceable Patterns

```js
// scripts/audit-native-features.js
import { readdirSync, readFileSync, statSync } from 'fs';
import { join, extname } from 'path';

const SRC  = './src';
const EXTS = new Set(['.html', '.svelte', '.vue', '.jsx', '.tsx', '.js', '.ts']);

const PATTERNS = [
  { re: /aria-expanded/g,                           msg: 'aria-expanded toggle — consider replacing with <details>/<summary>' },
  { re: /aria-modal\s*=\s*["']true["']/g,           msg: 'aria-modal="true" — consider replacing with <dialog>.showModal()' },
  { re: /role=["']dialog["']/g,                     msg: 'role="dialog" — consider replacing with native <dialog>' },
  { re: /\blazysizes\b|lozad|data-src=/g,           msg: 'JS lazy loader — replace with loading="lazy"' },
  { re: /addEventListener\(['"]scroll['"]/g,        msg: 'scroll event listener — consider IntersectionObserver or position:sticky' },
  { re: /focusTrap|trapFocus|focus-trap/g,          msg: 'focus trap library — native <dialog> traps focus automatically' },
  { re: /\byup\b|\bzod\b\.object|vee-validate|validate\.js/g, msg: 'JS validation library — consider HTML5 constraint validation' },
  { re: /swiper|splide|embla|keen-slider|slick/g,   msg: 'JS carousel library — consider CSS scroll-snap' },
];

function walk(dir) {
  return readdirSync(dir).flatMap(f => {
    const full = join(dir, f);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

const files = walk(SRC).filter(f => EXTS.has(extname(f)));
let issues  = 0;

for (const file of files) {
  const content = readFileSync(file, 'utf8');
  for (const { re, msg } of PATTERNS) {
    const matches = content.match(re);
    if (matches) {
      console.warn(`⚠️  ${msg}\n    ${file}  (${matches.length} occurrence${matches.length > 1 ? 's' : ''})`);
      issues++;
    }
  }
}

if (issues === 0) {
  console.log(`✅ No obvious native-feature replacement candidates found across ${files.length} files.`);
} else {
  console.log(`\n${issues} pattern(s) found. Review each — not all require changes.`);
}
```

### 7.2 Dependency Audit — Find Replaceable Packages

```js
// scripts/audit-native-deps.js
import { readFileSync } from 'fs';

const pkg  = JSON.parse(readFileSync('./package.json', 'utf8'));
const deps = { ...pkg.dependencies, ...pkg.devDependencies };

const REPLACEABLE = [
  { name: 'swiper',           replacement: 'CSS scroll-snap',            weight: '140 KB' },
  { name: 'splide',           replacement: 'CSS scroll-snap',            weight: '30 KB'  },
  { name: 'embla-carousel',   replacement: 'CSS scroll-snap',            weight: '15 KB'  },
  { name: 'keen-slider',      replacement: 'CSS scroll-snap',            weight: '14 KB'  },
  { name: 'slick-carousel',   replacement: 'CSS scroll-snap',            weight: '70 KB'  },
  { name: 'focus-trap',       replacement: '<dialog> native focus trap', weight: '4 KB'   },
  { name: 'a11y-dialog',      replacement: '<dialog> element',           weight: '3 KB'   },
  { name: 'micromodal',       replacement: '<dialog> element',           weight: '2 KB'   },
  { name: 'lazysizes',        replacement: 'loading="lazy" attribute',   weight: '22 KB'  },
  { name: 'lozad',            replacement: 'loading="lazy" attribute',   weight: '3 KB'   },
  { name: 'vanilla-lazyload', replacement: 'loading="lazy" attribute',   weight: '8 KB'   },
  { name: 'flatpickr',        replacement: '<input type="date">',        weight: '50 KB'  },
  { name: 'pikaday',          replacement: '<input type="date">',        weight: '15 KB'  },
  { name: 'validate.js',      replacement: 'HTML5 constraint validation', weight: '10 KB' },
  { name: 'yup',              replacement: 'HTML5 constraint validation (client-side)', weight: '40 KB' },
  { name: '@simonwep/pickr',  replacement: '<input type="color">',       weight: '30 KB'  },
];

let found = false;

for (const { name, replacement, weight } of REPLACEABLE) {
  if (deps[name]) {
    console.warn(`⚠️  ${name} (${weight}) — replaceable with: ${replacement}`);
    found = true;
  }
}

if (!found) {
  console.log('✅ No obviously replaceable UI dependencies found.');
} else {
  console.log('\nVerify each before removing — some projects have requirements that justify the library.');
}
```

### 7.3 package.json Scripts

```json
{
  "scripts": {
    "audit:native":      "node scripts/audit-native-features.js",
    "audit:native:deps": "node scripts/audit-native-deps.js",
    "audit:native:all":  "npm run audit:native && npm run audit:native:deps"
  }
}
```

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied

List every file created or modified — custom accordions replaced with `<details>`, modals replaced with `<dialog>`, carousels migrated to CSS scroll-snap, validation libraries removed and replaced with HTML5 constraints, JS lazy loaders removed, scroll listeners replaced with `IntersectionObserver` or `position: sticky`, audit scripts created.

### ⚠️ Manual Actions Required

List patterns that need human review before removal — JS carousel libraries where autoplay or advanced features are genuinely needed, date pickers requiring calendar UI beyond what `<input type="date">` provides, validation schemas with complex cross-field rules that cannot be expressed as HTML5 constraints, `<dialog>` browser support requirements to confirm against the project's stated support matrix.

### Current Native Feature Status

| Pattern | Count found | Status | JS removed |
|---|---|---|---|
| Custom accordions (`aria-expanded`) | X | Replaced / Remaining | ~X KB |
| Custom modals (`role="dialog"`) | X | Replaced / Remaining | ~X KB |
| JS carousel libraries | X | Replaced / Remaining | ~X KB |
| JS validation libraries | X | Replaced / Remaining | ~X KB |
| JS lazy loaders | X | Replaced / Remaining | ~X KB |
| Scroll event listeners | X | Replaced / Remaining | — |
| Replaceable npm packages removed | X | — | ~X KB total |

### Estimated Impact

- JavaScript removed from bundles: ~X KB (uncompressed), ~X KB (gzip)
- npm packages removed: X
- CPU savings: scroll listeners → IntersectionObserver eliminates per-frame main-thread work
- Accessibility improvements: native elements carry implicit ARIA roles, keyboard behaviour, and focus management that custom implementations must replicate manually
