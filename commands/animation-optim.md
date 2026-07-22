# Animation — Low Energy Motion

Audit and optimize all animations in this project for GPU efficiency, minimal CPU cost, and full accessibility safety. Apply every rule below. Report what was changed, what needs manual action, and why.

---

## 1. Respect `prefers-reduced-motion`

- Wrap every non-essential animation in a `prefers-reduced-motion` media query:
  ```css
  @media (prefers-reduced-motion: no-preference) {
    .animated-element {
      animation: slide-in 0.3s ease-out;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .animated-element {
      animation: none;
      /* Use a fade or no motion instead */
      opacity: 1;
    }
  }
  ```
- Where a transition conveys state change (e.g. modal open), replace with a **simple opacity fade** at reduced motion, not a removal:
  ```css
  @media (prefers-reduced-motion: reduce) {
    .modal {
      transition: opacity 0.15s ease;
    }
  }
  ```
- In JavaScript, always check before starting animations:
  ```js
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!prefersReduced) {
    element.animate([...], { duration: 300 });
  }
  ```
- Flag any animation, transition, or JS motion effect that does **not** check this preference.

## 2. Banned Animation Patterns

Identify and remove or replace the following:

- **Infinite animations** — Any `animation-iteration-count: infinite` or `loop: true` on non-essential elements. Replace with a single play or remove entirely.
- **Parallax scroll effects** — Any JS or CSS that moves elements at a different rate from scroll. Remove or offer a CSS `scroll-behavior: smooth` alternative.
- **Large scroll-bound JS animations** — Any `scroll` event listeners driving per-frame style mutations. Replace with `IntersectionObserver` for simpler enter/exit effects.
- **Blinking or flashing elements** — Any effect that flashes more than 3 times per second. Remove unconditionally (this is a WCAG 2.3.1 hard failure).
- **CSS `animation` on layout properties** — See section 4.

## 3. GPU-Safe Properties Only

Only animate or transition these two properties:

- `transform` (translate, scale, rotate, skew)
- `opacity`

These are the only properties the browser can promote to a compositor layer and animate without triggering layout or paint.

**Preferred pattern:**
```css
.card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.card:hover {
  transform: translateY(-4px);
  opacity: 0.9;
}
```

## 4. Properties Never to Animate

Flag and rewrite any animation or transition touching these properties:

| Banned property | GPU-safe replacement |
|---|---|
| `width`, `height` | `transform: scaleX()` / `scaleY()` |
| `top`, `left`, `right`, `bottom` | `transform: translate()` |
| `margin`, `padding` | `transform: translate()` |
| `box-shadow` | Use a pseudo-element with `opacity` |
| `filter` (blur, brightness, etc.) | Avoid or use sparingly with `will-change` only on hover |
| `border-radius` (animated) | `transform: scale()` with `border-radius` pre-set |
| `font-size`, `line-height` | `transform: scale()` |
| `background-color` (frequent) | Opacity crossfade over a colored layer |

## 5. CSS Over JavaScript

- Prefer CSS `transition` and `@keyframes` over JS-driven animations wherever possible.
- Only use JS animation APIs (`Web Animations API`, `requestAnimationFrame`, `GSAP`, etc.) when:
  - The animation requires dynamic values not expressible in CSS.
  - Sequencing or physics are needed.
- Flag any `setInterval` or `setTimeout` used to drive visual changes — replace with `requestAnimationFrame` or CSS.
- For enter/exit animations triggered by JS class toggles, keep the animation logic entirely in CSS:
  ```js
  // JS only adds/removes a class
  element.classList.add('is-visible');
  ```
  ```css
  /* All animation lives in CSS */
  .modal {
    opacity: 0;
    transform: translateY(8px);
    transition: opacity 0.2s ease, transform 0.2s ease;
  }
  .modal.is-visible {
    opacity: 1;
    transform: translateY(0);
  }
  ```

## 6. `will-change` Usage

- **Only add `will-change` when there is a measured GPU spike** — do not add it speculatively.
- Apply it immediately before the animation starts and remove it immediately after:
  ```js
  element.style.willChange = 'transform';
  element.addEventListener('transitionend', () => {
    element.style.willChange = 'auto';
  }, { once: true });
  ```
- In CSS, scope `will-change` to the active state only:
  ```css
  .card:hover {
    will-change: transform;
  }
  ```
- Never set `will-change: transform, opacity` on large numbers of elements simultaneously — it consumes GPU memory for every promoted layer.
- Flag any `will-change` that is set globally, on a parent element, or on elements that are never animated.

## 7. Infinite & Ambient Animations

- Remove all `animation-iteration-count: infinite` on elements visible during normal browsing.
- If a looping animation is intentional (e.g. a loading spinner), gate it under `prefers-reduced-motion: no-preference` and pause it when off-screen using `IntersectionObserver`:
  ```js
  const observer = new IntersectionObserver(([entry]) => {
    entry.target.style.animationPlayState = entry.isIntersecting ? 'running' : 'paused';
  });
  observer.observe(spinnerEl);
  ```

## 8. Scroll-Bound Animations

- Replace `scroll` event listener animation drivers with `IntersectionObserver` for simple appear effects:
  ```js
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      entry.target.classList.toggle('in-view', entry.isIntersecting);
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));
  ```
  ```css
  [data-animate] {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.3s ease, transform 0.3s ease;
  }
  [data-animate].in-view {
    opacity: 1;
    transform: translateY(0);
  }
  @media (prefers-reduced-motion: reduce) {
    [data-animate] {
      opacity: 1;
      transform: none;
      transition: none;
    }
  }
  ```
- For CSS Scroll-driven animations (`animation-timeline: scroll()`), ensure they only animate `transform` or `opacity` and are wrapped in a `@supports` block with a non-animated fallback.

## 9. DevTools Performance Audit

Flag the following for manual review in Chrome DevTools → Performance tab:

- Any frame that drops below 60 fps during an animation.
- Any "Recalculate Style" or "Layout" entry triggered by an animation (indicates a non-compositor property is being animated).
- Any "Paint" entry triggered more than once per frame during an animation.
- GPU memory usage exceeding 50 MB attributable to `will-change` or promoted layers.

Provide these audit instructions in the manual actions report when any of the above risks are present.

---

## Deliverables

After auditing the project, output a structured report with these sections:

### ✅ Changes Applied
List every file modified and exactly what changed — which animation was removed, which property was replaced, where `prefers-reduced-motion` was added, etc.

### ⚠️ Manual Actions Required
List items that require human action — e.g., measuring GPU cost in DevTools, removing infinite animations with intentional design purpose, replacing parallax features. Include exact file paths and recommended steps.

### DevTools Audit Checklist
For any at-risk animations remaining after changes, provide copy-paste steps:
- Open Chrome DevTools → Performance → Record while triggering the animation
- Check for "Layout", "Recalculate Style", or "Paint" in the flame chart
- Check Layers panel for unexpected promoted layers
- Check Memory → GPU Memory for elevated usage after `will-change`

### 📊 Estimated Impact
Provide a rough before/after summary of:
- Number of animations removed or replaced
- Properties no longer animating layout or paint
- `will-change` instances removed
- Infinite animations eliminated
- Elements now respecting `prefers-reduced-motion`
