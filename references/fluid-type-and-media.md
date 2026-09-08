# Fluid Type, Touch Targets & Media

Contents:
1. Fluid typography with `clamp()`
2. The zoom trap (why pure `vw` fails accessibility)
3. A complete fluid type scale
4. Fluid space
5. Touch targets
6. Responsive images and layout shift
7. Fonts and layout shift
8. The CLS checklist

---

## 1. Fluid typography with `clamp()`

`clamp(MIN, PREFERRED, MAX)` lets a value scale continuously between two viewport widths instead
of jumping at breakpoints. It replaces the three-media-query pattern for every size that should
grow smoothly — headings, section padding, gaps.

**The formula.** Given a size that should be `minSize` at `minVw` and `maxSize` at `maxVw` (all in
rem):

```
slope     = (maxSize − minSize) / (maxVw − minVw)
intercept = minSize − slope × minVw
preferred = intercept rem + (slope × 100) vw
```

**Worked example** — body text from 1 rem at 320 px (20 rem) to 1.125 rem at 1440 px (90 rem):

```
slope     = (1.125 − 1) / (90 − 20) = 0.00179
intercept = 1 − 0.00179 × 20        = 0.9643
```

```css
body { font-size: clamp(1rem, 0.9643rem + 0.1786vw, 1.125rem); }
```

Use the same two anchor widths (320 px and 1440 px is a good default pair) for every fluid value
in the system, so everything scales in step and the design keeps its proportions.

## 2. The zoom trap (why pure `vw` fails accessibility)

```css
h1 { font-size: clamp(2rem, 5vw, 4rem); }        /* ✗ breaks browser zoom */
h1 { font-size: clamp(2rem, 1.5rem + 2.5vw, 4rem); } /* ✓ */
```

Viewport units do not respond to the user's font-size preference or to browser zoom in the way
`rem` does — when the preferred term is *only* `vw`, text can effectively stop scaling, which
fails **WCAG 1.4.4 Resize Text (AA)**.

The rule: **the preferred term always contains a `rem` component**, and that component should be
large enough to carry the value on its own if `vw` contributed nothing. As a sanity check, zoom
the browser to 200 % — the text must get visibly larger.

Two more guards:

- Never set `font-size` on `html` in `px` (e.g. `html { font-size: 62.5% }` is fine; `16px` is
  not) — a fixed root font size overrides the user's browser setting.
- Keep body copy at **16 px minimum** on mobile. Below it, iOS Safari zooms on input focus and
  legibility drops for everyone.

## 3. A complete fluid type scale

A 1.2 (minor third) ratio on mobile opening to 1.25 on desktop, anchored 320 → 1440 px:

```css
:root {
  --step--1: clamp(0.833rem, 0.813rem + 0.102vw, 0.9rem);   /* small / captions */
  --step-0:  clamp(1rem,     0.964rem + 0.179vw, 1.125rem); /* body */
  --step-1:  clamp(1.2rem,   1.139rem + 0.304vw, 1.406rem); /* lead, h5 */
  --step-2:  clamp(1.44rem,  1.341rem + 0.496vw, 1.758rem); /* h4 */
  --step-3:  clamp(1.728rem, 1.570rem + 0.789vw, 2.197rem); /* h3 */
  --step-4:  clamp(2.074rem, 1.827rem + 1.232vw, 2.746rem); /* h2 */
  --step-5:  clamp(2.488rem, 2.113rem + 1.875vw, 3.433rem); /* h1 */
  --step-6:  clamp(2.986rem, 2.427rem + 2.795vw, 4.291rem); /* display */
}

h1 { font-size: var(--step-5); }

/* Line height tightens as size grows — a constant 1.5 looks loose on display type. */
h1, h2, h3 { line-height: 1.15; text-wrap: balance; }
p          { line-height: 1.6;  text-wrap: pretty; max-width: 68ch; }
```

`text-wrap: balance` on headings prevents the single-word orphan line that appears at awkward
widths; `text-wrap: pretty` does the same for the last line of a paragraph. Both degrade silently
where unsupported.

## 4. Fluid space

Apply the same treatment to padding and gaps so the rhythm of the page scales with the type:

```css
:root {
  --space-s:  clamp(0.75rem, 0.68rem + 0.36vw, 1rem);
  --space-m:  clamp(1rem,    0.86rem + 0.71vw, 1.5rem);
  --space-l:  clamp(1.5rem,  1.21rem + 1.43vw, 2.5rem);
  --space-xl: clamp(2.5rem,  1.79rem + 3.57vw, 5rem);   /* section padding */
}

section { padding-block: var(--space-xl); }
.stack > * + * { margin-block-start: var(--space-m); }
```

## 5. Touch targets

| Standard | Minimum | Applies to |
|---|---|---|
| **WCAG 2.5.8 Target Size (Minimum), AA** | **24 × 24 CSS px** | Everything interactive, unless spaced ≥ 24 px apart, inline in text, or browser-default styled |
| **WCAG 2.5.5 Target Size (Enhanced), AAA** | 44 × 44 CSS px | Everything interactive |
| **Apple HIG** | 44 × 44 pt | iOS/iPadOS |
| **Material Design** | 48 × 48 dp, 8 dp apart | Android |

The practical target: **44 × 44 px on touch, 24 × 24 px absolute floor everywhere**, with at least
8 px of clear space between adjacent targets. Adjacent-but-tiny is worse than small-and-isolated,
because the failure mode is a mis-tap on the wrong control rather than a missed tap.

```css
/* Base: meets AA everywhere. */
.btn, .icon-btn, a[role="button"] {
  min-block-size: 2.75rem;   /* 44px */
  min-inline-size: 2.75rem;
  padding-inline: var(--space-m);
}

/* Small visual controls (a 20px close icon) keep their look but gain a
   hit area, via a pseudo-element rather than layout-shifting padding. */
.icon-btn--sm { position: relative; }
.icon-btn--sm::after {
  content: "";
  position: absolute;
  inset: 50%;
  inline-size: 44px;
  block-size: 44px;
  translate: -50% -50%;
}

/* Coarse pointers get the enhanced size regardless of viewport width —
   a touchscreen laptop at 1440px needs this as much as a phone does. */
@media (pointer: coarse) {
  .btn, .nav__link, .tab { min-block-size: 2.75rem; }
  .list-row { padding-block: 0.875rem; }
}

/* Thumb reach: on phones, primary actions belong in the lower third.
   Destructive actions belong away from it. */
```

Also: form fields at least 44 px tall, labels always clickable (`<label for>` or wrapping), and
never rely on a hover-revealed control as the only path to an action.

## 6. Responsive images and layout shift

Layout shift from images is caused by one thing: the browser does not know the image's aspect
ratio until it downloads, so it reserves zero height and everything below jumps when it arrives.

```html
<!-- width/height are the intrinsic pixel dimensions. The browser derives an
     aspect ratio from them and reserves the box before the file loads.
     They do NOT prevent CSS from resizing the image. -->
<img src="hero-800.jpg"
     srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1600.jpg 1600w, hero-2400.jpg 2400w"
     sizes="(width >= 64rem) 960px, (width >= 48rem) 720px, 100vw"
     width="1600" height="900"
     alt="…"
     fetchpriority="high"
     decoding="async">
```

```css
img, video, svg, iframe { max-width: 100%; height: auto; display: block; }

/* Where the intrinsic size is unknown (CMS content, user uploads), pin the box. */
.media { aspect-ratio: 16 / 9; }
.media > img { inline-size: 100%; block-size: 100%; object-fit: cover; }
```

Rules that matter in practice:

- **`sizes` must describe the rendered width**, not the viewport, or the browser picks a file that
  is too large (wasted bytes) or too small (blurry). If the image sits in a 960 px container,
  `sizes` says `960px` at that breakpoint — mirroring the container table.
- **`loading="lazy"` on below-the-fold images only.** Lazy-loading the LCP image measurably delays
  it. Pair the hero with `fetchpriority="high"` and no `loading` attribute.
- **`<picture>` for art direction**, not for sizing — a different crop (16:9 → 1:1) or a different
  format, never just a different scale of the same image:

```html
<picture>
  <source media="(width >= 48rem)" srcset="hero-wide.avif" type="image/avif">
  <source media="(width >= 48rem)" srcset="hero-wide.webp">
  <source srcset="hero-square.avif" type="image/avif">
  <img src="hero-square.jpg" width="800" height="800" alt="…">
</picture>
```

- **Background images have no intrinsic size** — the container must define one, or use
  `aspect-ratio`. This is a frequent hidden CLS source.
- **Reserve space for anything async**: ads, embeds, banners, skeletons. A skeleton that is a
  different height from the content it replaces causes exactly the shift it was meant to prevent.
- **Never insert content above existing content** after load (cookie bars, promo banners) unless
  it is `position: fixed` or its space was reserved.

## 7. Fonts and layout shift

Web fonts shift text when the fallback and the web font have different metrics.

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter.woff2") format("woff2");
  font-display: swap;          /* show fallback immediately, swap when ready */
  font-weight: 100 900;        /* variable font: one file, all weights */
}

/* Metric-matched fallback: these three descriptors make the fallback occupy
   almost exactly the same space as the real font, so the swap is invisible. */
@font-face {
  font-family: "Inter Fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
}

body { font-family: "Inter", "Inter Fallback", system-ui, sans-serif; }
```

Preload only the fonts used above the fold, and only in `woff2`:

```html
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
```

## 8. The CLS checklist

Target: **CLS < 0.1** at the 75th percentile (Core Web Vitals "good"). Verify in Lighthouse or
`web-vitals` — mobile field data, not desktop lab data.

- [ ] Every `<img>`, `<video>`, `<iframe>` has `width`/`height` or a CSS `aspect-ratio`
- [ ] The LCP image is not lazy-loaded and carries `fetchpriority="high"`
- [ ] `sizes` matches the container widths from the breakpoint table
- [ ] Fonts use `font-display: swap` plus a metric-matched fallback
- [ ] Ad, embed, and skeleton slots have reserved dimensions
- [ ] Nothing is inserted above existing content after first paint
- [ ] Animations use `transform`/`opacity` — animating `width`, `height`, `top` triggers layout
- [ ] `min-height` on containers whose content arrives asynchronously
