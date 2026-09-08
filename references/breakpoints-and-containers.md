# Breakpoints & Containers

Contents:
1. The breakpoint system
2. Container max-widths and why they stop growing
3. Range syntax (`min-width` and `max-width` together)
4. Implementation — plain CSS
5. Implementation — Tailwind
6. Implementation — SCSS mixins
7. Container queries: when to prefer them
8. Capability queries: hover, pointer, motion

---

## 1. The breakpoint system

Six tiers. `rem` values assume the standard 16 px root, so `48rem` = 768 px at default settings
and correctly *increases* if the user has enlarged their browser font.

| Tier | Range (CSS px) | `min-width` | `max-width` (upper bound) | Container max-width | Gutter | Grid columns | Body copy |
|---|---|---|---|---|---|---|---|
| **Mobile portrait** | 320 – 479 | base / none | `29.9375rem` (479 px) | 100 % (fluid) | 16 px | 4 | 16 px |
| **Mobile landscape / small tablet** | 480 – 767 | `30rem` (480 px) | `47.9375rem` (767 px) | 100 % (fluid) | 20 px | 4 | 16 px |
| **Tablet portrait** | 768 – 1023 | `48rem` (768 px) | `63.9375rem` (1023 px) | **720 px** | 24 px | 8 | 17 px |
| **Laptop / small desktop** | 1024 – 1439 | `64rem` (1024 px) | `89.9375rem` (1439 px) | **960 px** | 32 px | 12 | 17 px |
| **Large desktop** | 1440 – 1919 | `90rem` (1440 px) | `119.9375rem` (1919 px) | **1280 px** | 40 px | 12 | 18 px |
| **Ultra-wide** | 1920+ | `120rem` (1920 px) | — | **1440 px** | 48 px | 12 | 18 px |

Notes on the choices:

- **320 px is the floor.** It is the iPhone SE (1st gen) and the narrowest width any current
  browser reports. Below it, users are zoomed in and the browser handles it.
- **The `.9375rem` upper bounds** are `1/16` of a rem = 1 px, avoiding the classic overlap bug
  where `max-width: 768px` and `min-width: 768px` both match at exactly 768 px. Modern range
  syntax (§3) removes the need for this arithmetic entirely.
- **768 and 1024 are load-bearing**, because they are the iPad portrait and iPad landscape widths
  and the two most common places a real layout changes shape.
- **1440 exists** because a MacBook Pro 14"/16" and most 1440p monitors land at or above it, and
  because a 1280 px container inside a 1440 px window still has comfortable margins.
- **Treat these as the default, not the law.** The right breakpoint is where *this content*
  breaks. If a card grid gets an awkward orphan at 900 px, add a breakpoint at 900 px. What you
  should not do is invent five breakpoints within 100 px of each other, or add a tier that no
  device and no content change occupies.

## 2. Container max-widths and why they stop growing

The container is the constraint that makes wide screens readable. Two things drive it:

**Line length.** Comfortable reading is 45–75 characters. At a 17 px body size that is roughly
600–700 px of text. A prose column should therefore be capped near **65ch** regardless of what
the page container does — a 1440 px-wide paragraph is unreadable no matter how wide the monitor.

**Scan distance.** On an ultra-wide, content spanning the full width forces head movement between
a left-hand label and a right-hand value. Capping at 1440 px and centring keeps a single visual
field.

```css
.container {
  width: 100%;
  margin-inline: auto;
  padding-inline: var(--gutter);
  max-width: var(--container-max);  /* set per tier — see §4 */
}

/* Prose is capped independently of the layout container. */
.prose { max-width: 68ch; }

/* Dashboards and data tables are the documented exception: they benefit from
   real estate, so let them run wider but still stop before the edge. */
.container--wide { max-width: 1760px; }
```

**Ultra-wide specifically.** Above 1920 px, do not simply keep widening the container. Pick one:

1. **Cap and centre** (default) — content stops at 1440 px, background/section colours still run
   full-bleed so the page does not look like a floating document.
2. **Add a column** — a 12-column grid becomes a genuine 3-up or 4-up layout, or a persistent
   sidebar/table-of-contents appears. This uses the space instead of discarding it.
3. **Increase density, not width** — for dashboards: more cards per row, same card size.

What fails is stretching a two-column marketing layout to 3440 px; the eye cannot connect the
halves.

## 3. Range syntax (`min-width` and `max-width` together)

Modern browsers (Chrome/Edge 104+, Firefox 102+, Safari 16.4+) support comparison operators,
which are clearer and have no off-by-one gaps:

```css
/* Modern range syntax — preferred */
@media (width >= 48rem) { }                    /* tablet and up */
@media (48rem <= width < 64rem) { }            /* tablet portrait only */
@media (width < 48rem) { }                     /* below tablet */

/* Classic equivalent, for older baselines */
@media (min-width: 48rem) { }
@media (min-width: 48rem) and (max-width: 63.9375rem) { }
@media (max-width: 47.9375rem) { }
```

Use `max-width` queries only for *exceptions* — "this one component collapses below tablet" —
never as the primary direction of the stylesheet. A mobile-first sheet reads as a progression;
a desktop-first sheet reads as a list of undo statements, and the undo is always incomplete.

## 4. Implementation — plain CSS

Custom properties cannot be used inside media query conditions (media queries are evaluated
before custom property substitution), so breakpoint *values* stay literal while everything the
breakpoint *sets* is a token:

```css
:root {
  --gutter: 1rem;
  --container-max: 100%;
}

@media (width >= 30rem) {  /* 480px */
  :root { --gutter: 1.25rem; }
}
@media (width >= 48rem) {  /* 768px */
  :root { --gutter: 1.5rem;  --container-max: 720px; }
}
@media (width >= 64rem) {  /* 1024px */
  :root { --gutter: 2rem;    --container-max: 960px; }
}
@media (width >= 90rem) {  /* 1440px */
  :root { --gutter: 2.5rem;  --container-max: 1280px; }
}
@media (width >= 120rem) { /* 1920px */
  :root { --gutter: 3rem;    --container-max: 1440px; }
}
```

Every component then reads `var(--gutter)` and `var(--container-max)` and needs no media queries
of its own. This is the main reason to centralise: it turns "change the tablet gutter" from a
codebase-wide find-and-replace into a one-line edit.

For grids, prefer intrinsic layouts that need no breakpoints at all:

```css
/* Wraps on its own from 1 to N columns. minmax(0, 1fr) prevents wide children
   (images, long words, <pre>) from blowing out the track. */
.auto-grid {
  display: grid;
  gap: var(--gutter);
  grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr));
}
```

## 5. Implementation — Tailwind

Tailwind's defaults (640 / 768 / 1024 / 1280 / 1536) are close but miss the 480 px and 1920 px
tiers. Map this system onto them:

**Tailwind v4** (CSS-first config):

```css
@import "tailwindcss";

@theme {
  --breakpoint-xs: 30rem;   /* 480px  mobile landscape */
  --breakpoint-sm: 40rem;   /* 640px  (kept for compatibility) */
  --breakpoint-md: 48rem;   /* 768px  tablet portrait */
  --breakpoint-lg: 64rem;   /* 1024px laptop */
  --breakpoint-xl: 90rem;   /* 1440px large desktop */
  --breakpoint-2xl: 120rem; /* 1920px ultra-wide */
}
```

**Tailwind v3** (`tailwind.config.js`):

```js
module.exports = {
  theme: {
    screens: {
      xs: '30rem', sm: '40rem', md: '48rem',
      lg: '64rem', xl: '90rem', '2xl': '120rem',
    },
    container: {
      center: true,
      padding: { DEFAULT: '1rem', xs: '1.25rem', md: '1.5rem', lg: '2rem', xl: '2.5rem', '2xl': '3rem' },
      screens: { md: '720px', lg: '960px', xl: '1280px', '2xl': '1440px' },
    },
  },
};
```

Usage stays mobile-first: `class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3"`. For the
detail of Tailwind's responsive utilities, `ui-styling/references/tailwind-responsive.md` covers
it thoroughly — this file only supplies the values.

## 6. Implementation — SCSS mixins

```scss
$breakpoints: (
  xs:  30rem,   // 480
  sm:  40rem,   // 640
  md:  48rem,   // 768
  lg:  64rem,   // 1024
  xl:  90rem,   // 1440
  xxl: 120rem,  // 1920
);

@mixin up($name) {
  $min: map-get($breakpoints, $name);
  @if $min == null { @error "Unknown breakpoint: #{$name}"; }
  @media (width >= #{$min}) { @content; }
}

/* Exception-only. If you reach for this more than a few times, the base
   styles are wrong — they are describing a desktop layout, not a mobile one. */
@mixin below($name) {
  @media (width < #{map-get($breakpoints, $name)}) { @content; }
}

.card { padding: 1rem; @include up(md) { padding: 1.5rem; } }
```

## 7. Container queries: when to prefer them

A media query asks how wide the *window* is. A container query asks how wide the *component's
parent* is — which is what a component actually needs to know. A card in a sidebar and the same
card in a main column should look different at the same window width, and only container queries
can express that.

```css
.card-grid { container-type: inline-size; container-name: cards; }

@container cards (width >= 30rem) {
  .card { grid-template-columns: 8rem 1fr; }  /* becomes horizontal */
}
```

Baseline-available in all current engines (Chrome/Edge 105+, Safari 16+, Firefox 110+).

**Choose container queries** for reusable components that appear in more than one context — cards,
media objects, form rows, table cells. **Choose media queries** for page-level structure — the
container width, the number of grid columns in the page shell, whether the nav is a rail or a
sheet — because those genuinely depend on the window.

## 8. Capability queries: hover, pointer, motion

Width is a poor proxy for input method. A 1024 px touchscreen laptop and a 1024 px mouse-driven
window need different affordances, and only these queries can tell them apart:

```css
/* Hover effects only where hover exists — otherwise touch users get a
   "sticky hover" state that survives the tap. */
@media (hover: hover) and (pointer: fine) {
  .card:hover { transform: translateY(-2px); }
}

/* Coarse pointers get bigger targets, regardless of screen size. */
@media (pointer: coarse) {
  .btn, .nav__link { min-height: 44px; min-width: 44px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Any interaction that exists only on hover — a dropdown that opens on mouseover, a tooltip
carrying information not available elsewhere — must have a click/tap equivalent, or it does not
exist for roughly half the traffic.
