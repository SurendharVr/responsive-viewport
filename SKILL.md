---
name: responsive-viewport
description: "Production spec for responsive layout across mobile, tablet, laptop, desktop and ultra-wide: the viewport meta tag, safe-area insets for notches and home indicators, a breakpoint + container-width system, real device dimensions in CSS pixels, fluid type with clamp(), touch-target sizing, and CLS-safe images. Use this whenever the work touches breakpoints, media queries, container or max-width decisions, the meta name=viewport tag, viewport units (vh/dvh/svh/vw), mobile notches or safe areas, 'make this responsive', 'it breaks on mobile', 'looks wrong on iPad', horizontal scroll or overflow bugs, components that look wrong in one container but fine in another (container queries), device testing widths, tap target size, layout shift, or picking font sizes that scale, even when the user does not say the word 'responsive'."
metadata:
  version: "1.1.1"
---

# Responsive Viewport Spec

A concrete, framework-agnostic specification for making a web app render correctly from a
320 px phone to a 3440 px ultra-wide. It exists because "make it responsive" usually fails in
one of five predictable ways, and each has a settled answer:

1. The viewport meta tag is missing, or it disables pinch-zoom (an accessibility failure).
2. Breakpoints are copied from a device list instead of chosen where the content breaks.
3. Content is never capped, so line lengths become unreadable on wide screens.
4. `100vh` and `100vw` are used, so mobile chrome clips the layout and desktop scrollbars
   cause horizontal scroll.
5. Images and fonts load without reserved space, so the page jumps (CLS).

Work through the checklist below. Load a reference file when you need the detail behind a step.

## Reference map

| Need | Read |
|---|---|
| Viewport meta attributes, `viewport-fit`, safe areas, dvh/svh/lvh, PWA + keyboard cases | `references/viewport-and-safe-areas.md` |
| Breakpoint table, container max-widths, grid/gutter scale, CSS + Tailwind + SCSS implementations | `references/breakpoints-and-containers.md` |
| Logical CSS pixel dimensions for iPhone, Galaxy, iPad, MacBook, Windows laptops, 1080p/1440p/4K/ultra-wide | `references/device-matrix.md` |
| Fluid typography formulas, touch targets, responsive images, CLS budget | `references/fluid-type-and-media.md` |
| Drop-in starter stylesheet (tokens, container, breakpoints, safe areas, fluid scale) | `assets/responsive-base.css` |
| Static audit of an existing codebase | `scripts/check_responsive.py` |

**Load references only when you need the detail behind a number.** The tables in this file are
the answer for a spec or "what breakpoints should we use" question — reading four reference files
to produce a document you could have written from the tables costs tokens and adds nothing. Open
a reference when you are writing code that has to be *right* (the exact safe-area recipe, the
clamp arithmetic, a specific device width), not to check that a number you already have is real.

## The order of work

Responsive problems have a dependency order. Fixing them out of order wastes effort — you cannot
judge a breakpoint while the page is still zoom-locked or overflowing.

**1. Fix the document contract first.** The viewport meta tag, `box-sizing`, `overflow-x: clip`
on `html`/`body`, and a root that respects the user's font size. Nothing below matters until the
browser is measuring the page correctly.

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

That is the whole tag for a modern app. Do not add `maximum-scale` or `user-scalable=no` — see
the accessibility note in `references/viewport-and-safe-areas.md`.

**2. Establish the container and the breakpoints**, in that order. The container max-width is the
real decision; breakpoints are just where the container and its columns change shape. Default
system (full table with gutters and columns in `references/breakpoints-and-containers.md`):

| Tier | From | Container max-width |
|---|---|---|
| Mobile portrait | 320 px | fluid, 16 px gutters |
| Mobile landscape / small tablet | 480 px | fluid, 20 px gutters |
| Tablet portrait | 768 px | 720 px |
| Laptop / small desktop | 1024 px | 960 px |
| Large desktop | 1440 px | 1280 px |
| Ultra-wide | 1920 px | 1440 px (content stops growing; the page does not) |

Write breakpoints in `rem` (`48rem`, not `768px`) so a user who raises their browser font size
gets the simpler layout rather than a cramped desktop one.

**3. Make type and space fluid between those breakpoints**, so the design does not visibly
"snap". `clamp()` for anything that should scale continuously; media queries only for layout
changes that are discrete (one column becomes three).

**4. Then verify at real widths.** 320, 375, 390, 768, 1024, 1440, 1920. If a layout survives
320 px and 1920 px, the middle almost always takes care of itself.

## Rules that are not negotiable

These are the ones that cause visible bugs rather than aesthetic disagreements.

- **Never `width: 100vw`.** On desktop `100vw` includes the scrollbar gutter, so a full-width
  element is ~15 px wider than the viewport and the page scrolls sideways. Use `width: 100%`.
- **Never bare `vh` for full-height layouts.** Mobile browser chrome grows and shrinks as you
  scroll; `100vh` is the *largest* height, so a `100vh` hero has its bottom cut off on load. Use
  `100dvh` (dynamic) with a `100vh` fallback line above it for old browsers.
- **`min-width` media queries as the primary direction.** Mobile-first means the base styles are
  the mobile styles and everything else is an addition. Desktop-first `max-width` chains force
  every component to be undone at small sizes, which is where the overflow bugs come from.
- **Breakpoints in `rem`, and no more than about six of them.** A `px` breakpoint ignores the
  user's font-size setting, so someone reading at 20 px root gets the desktop layout crammed into
  a screen that is effectively 20 % narrower. And a list that has drifted to nine or ten values
  is no longer a system — nobody can say which tier a change belongs to.
- **Never a `px` `font-size` on `html` or `:root`.** It overrides the browser font-size
  preference and silently defeats every `rem` in the stylesheet. Scale the root with a percentage
  or leave it alone; scale *content* with `clamp()` instead.
- **`overflow-x: clip`, never `overflow-x: hidden`, on `html`/`body`.** `hidden` creates a scroll
  container, which silently kills `position: sticky` in every descendant. Both are a net anyway —
  find the element that actually overflows.
- **Affordances branch on capability, not width.** `@media (hover: hover)` before any hover
  effect, `@media (pointer: coarse)` for touch sizing. A 1024 px touchscreen laptop and a 1024 px
  mouse window need different affordances, and width cannot tell them apart.
- **`minmax(0, 1fr)`, never bare `1fr`,** on grid tracks that contain images or long text. A bare
  `1fr` track has an `auto` minimum, so one wide child expands the whole grid past the viewport.
- **Every image gets intrinsic dimensions** — `width`/`height` attributes or a CSS
  `aspect-ratio`. This is the single biggest source of layout shift.
- **Interactive targets are at least 24 × 24 CSS px** (WCAG 2.5.8, AA) and 44 × 44 on touch
  (Apple HIG / WCAG 2.5.5 AAA). Give coarse pointers the larger size via
  `@media (pointer: coarse)`.
- **Logical properties** (`padding-inline`, `margin-block`, `inset-inline-start`) rather than
  left/right, so RTL works without a second stylesheet.

## Applying this to an existing codebase

Run the auditor before proposing changes — it finds the mechanical failures fast and gives you
file:line evidence rather than guesses:

```bash
python ~/.claude/skills/responsive-viewport/scripts/check_responsive.py <path>
```

It reports: missing or zoom-locked viewport tags, `100vh`/`100vw` usage, images without
dimensions, desktop-first media query chains, `viewport-fit=cover` without any safe-area padding,
and an inventory of every breakpoint value in the codebase (fragmented breakpoint lists — 640,
680, 700, 768 — are usually accidental and worth consolidating).

Fix in the order of the four steps above, then re-run to confirm. When a finding is intentional
(a design that genuinely wants a fixed `100vh` panel on desktop only), say so rather than
silently changing it.

## Applying this to a new build

Copy `assets/responsive-base.css` in as the first stylesheet, before any component CSS. It
defines the breakpoint custom properties, the container, the fluid type scale, safe-area padding
and the document-level resets described above, and nothing else — it is a foundation, not a
design system, and it will not fight Tailwind, shadcn, or an existing token file.

If the project already uses Tailwind, do not import the CSS file; port the breakpoint and
container values into `tailwind.config` instead — the mapping is in
`references/breakpoints-and-containers.md`.

## Related skills

This skill is the dimensional layer only. It pairs with, and does not replace:

- `hallmark` — visual craft, anti-slop rules, and its own stricter mobile gate list.
- `ui-styling` — Tailwind and shadcn implementation detail.
- `ui-ux-pro-max` — style, palette and font-pairing selection.

When one of those is already driving the work, use this skill for the numbers (breakpoints,
container widths, device widths, target sizes) and let the other own the aesthetics.

## Reporting

When asked for a responsive spec or audit, structure the answer as:

```
## Viewport configuration      (the tag, and why each attribute is or is not there)
## Breakpoints & containers    (table: tier, range, container max-width, gutter, columns)
## Device targets              (only the devices relevant to this product's analytics)
## Findings                    (audit only — file:line, severity, the fix)
## Implementation              (the actual CSS/config diff)
```

Cite real widths, not adjectives. "Breaks below 360 px because the pricing table's third column
has a 140 px min-width" is actionable; "not fully mobile-optimised" is not.
