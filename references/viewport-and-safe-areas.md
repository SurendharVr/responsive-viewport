# Viewport Configuration & Safe Areas

Contents:
1. The tag
2. Attribute-by-attribute
3. The accessibility case against locking zoom
4. `viewport-fit` and safe-area insets
5. Viewport units: vh vs dvh / svh / lvh
6. The mobile keyboard, PWAs, and installed apps
7. Verification

---

## 1. The tag

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

That is the correct tag for essentially every modern responsive web app. Anything longer is
either redundant or actively harmful.

Without it, mobile browsers assume the page was written for desktop and render it into a virtual
980 px-wide canvas, then shrink that canvas to fit the screen — which is why an unconfigured site
appears as a zoomed-out desktop page on a phone. Media queries then evaluate against 980 px, so
the mobile CSS never applies.

Place it in `<head>` before any stylesheet, so the browser knows the layout width before it
begins layout.

## 2. Attribute-by-attribute

| Attribute | Value | What it does | Use it? |
|---|---|---|---|
| `width` | `device-width` | Sets the layout viewport to the device's width in CSS pixels (e.g. 390 on an iPhone 15) instead of the 980 px default. This is what makes `min-width` media queries evaluate against the real screen. | Always |
| `initial-scale` | `1` | Zoom level on first paint: 1 CSS px = 1 layout px. Also fixes an old iOS bug where rotating to landscape re-zoomed the page. | Always |
| `viewport-fit` | `cover` | Lets the page paint into the display cutout / rounded-corner region, and is the precondition for `env(safe-area-inset-*)` returning non-zero values. Without it the browser letterboxes the page inside the "safe" rectangle (`auto`, the default). | When the design has full-bleed surfaces, fixed headers/footers, or edge-to-edge media |
| `maximum-scale` | `1` … `5` | Caps how far the user may pinch-zoom. | No — see below |
| `minimum-scale` | `1` | Floor on zoom-out. Rarely useful; the default is fine. | No |
| `user-scalable` | `no` / `yes` | Disables pinch-zoom entirely. | No — see below |
| `interactive-widget` | `resizes-content` / `resizes-visual` / `overlays-content` | Declares how the on-screen keyboard affects the viewport. Default is `resizes-visual`. | Only for app-shell layouts, see §6 |

## 3. The accessibility case against locking zoom

`user-scalable=no` and `maximum-scale=1` both prevent a user from pinch-zooming the page.

- **WCAG 2.1 SC 1.4.4 Resize Text (Level AA)** requires that text can be scaled to 200 % without
  loss of content or function. Blocking pinch-zoom removes the mechanism most mobile users
  actually use to do that, so it is a direct AA failure.
- **WCAG 2.1 SC 1.4.10 Reflow (Level AA)** then compounds it: the user cannot zoom in to read,
  and the layout was never tested at that zoom level.
- Low-vision users, users with motor tremor who zoom to enlarge tap targets, and anyone reading a
  small-type table are all affected. This is not a hypothetical population — it is the most
  commonly cited mobile accessibility defect in real audits.

Practical note: **iOS Safari has ignored `user-scalable=no` since iOS 10**, so the attribute buys
nothing on iPhone while still breaking zoom on Android Chrome. It is pure cost.

The usual motivation for adding it is the iOS "auto-zoom on input focus" behaviour, where Safari
zooms in when a form field has a font-size below 16 px. Fix the cause, not the symptom:

```css
/* iOS Safari zooms the viewport when a focused field's text is under 16px.
   Setting 16px on the control removes the trigger without touching zoom. */
input, select, textarea { font-size: max(16px, 1rem); }
```

If a product decision genuinely requires locked zoom (a canvas/map surface, a game), lock it on
that one element with `touch-action`, not on the document.

## 4. `viewport-fit` and safe-area insets

`env(safe-area-inset-top | right | bottom | left)` expose the distance from each viewport edge to
the nearest safe area: the notch or Dynamic Island at the top, the home indicator at the bottom,
the rounded corners and (in landscape) the sensor housing at the sides. On Android they cover
display cutouts and gesture-navigation bars.

They return `0px` unless `viewport-fit=cover` is set, so it is safe to apply them unconditionally.

```css
:root {
  /* Named so component CSS never has to repeat the env() calls. */
  --safe-top:    env(safe-area-inset-top, 0px);
  --safe-right:  env(safe-area-inset-right, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-left:   env(safe-area-inset-left, 0px);

  --gutter: 1rem;
}

/* Page gutters: max() keeps the design's own padding as a floor, and only grows
   where the hardware actually intrudes (landscape sides, home indicator). */
body {
  padding-inline: max(var(--gutter), var(--safe-left)) max(var(--gutter), var(--safe-right));
}

/* A fixed bottom bar must clear the home indicator, or the last 34px of it
   are un-tappable on an iPhone. Pad the bar; don't just move it up. */
.app-bottom-bar {
  position: fixed;
  inset-inline: 0;
  bottom: 0;
  padding-block: 0.75rem;
  padding-bottom: calc(0.75rem + var(--safe-bottom));
}

/* A sticky/fixed top bar under the notch. Same principle at the top edge. */
.app-top-bar {
  position: sticky;
  top: 0;
  padding-top: calc(0.75rem + var(--safe-top));
}

/* Full-bleed media should ignore the gutters but still respect the corners. */
.full-bleed {
  width: 100%;
  margin-inline: calc(-1 * max(var(--gutter), var(--safe-left)))
                 calc(-1 * max(var(--gutter), var(--safe-right)));
}

/* Scroll containers need the inset as padding, not margin, so content can
   scroll under the indicator but come to rest above it. */
.scroll-area {
  overflow-y: auto;
  padding-bottom: var(--safe-bottom);
  scroll-padding-bottom: var(--safe-bottom);
  -webkit-overflow-scrolling: touch;
}
```

Two related environment variables are worth knowing:

- `env(safe-area-max-inset-bottom)` — the largest the bottom inset will ever get, useful for
  reserving space that does not animate while browser chrome collapses.
- `env(titlebar-area-height)` / `env(titlebar-area-x|y|width)` — for installed desktop PWAs using
  `display_override: window-controls-overlay`.

## 5. Viewport units: vh vs dvh / svh / lvh

Mobile browser chrome (URL bar, toolbar) hides as you scroll down and reappears as you scroll up,
which changes the visible height without a resize event in older engines.

| Unit | Means | Behaviour |
|---|---|---|
| `vh` | Legacy | Equals `lvh` on mobile — the height with chrome *hidden*. A `100vh` element is therefore taller than the screen on load, and its bottom is cut off. |
| `lvh` | Large viewport height | Chrome retracted. Stable, but too tall on first paint. |
| `svh` | Small viewport height | Chrome expanded. Stable, and guaranteed fully visible — the right choice for anything that must be seen without scrolling. |
| `dvh` | Dynamic viewport height | Tracks the current chrome state live. The right choice for full-height panels; can cause reflow while scrolling if used on many elements. |

```css
.hero {
  min-height: 100vh;   /* fallback for engines without dynamic units */
  min-height: 100dvh;  /* overrides where supported */
}

/* A layout that must never be clipped, e.g. a login card centred on screen. */
.viewport-lock { min-height: 100svh; }
```

`vw` has its own trap: **`100vw` includes the classic scrollbar's width** on desktop Windows and
Linux, so `width: 100vw` on a block inside a scrolling page is ~15 px wider than the visible area
and produces horizontal scroll. Use `width: 100%`, or `100dvw` where a true viewport width is
genuinely needed. Pair with:

```css
html, body { overflow-x: clip; }  /* clip, not hidden — `hidden` breaks position: sticky */
```

## 6. The mobile keyboard, PWAs, and installed apps

**Keyboard.** By default the on-screen keyboard shrinks the *visual* viewport only, so a
`position: fixed` footer stays behind the keyboard. Two options:

```html
<!-- Layout viewport resizes with the keyboard: fixed bars sit above it.
     Good for chat/composer UIs; it does reflow the page, so test it. -->
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content">
```

or read the visual viewport directly and let the layout stay put:

```js
// Mirror the keyboard's occluded height into a custom property.
const vv = window.visualViewport;
if (vv) {
  const sync = () => document.documentElement.style.setProperty(
    '--keyboard-inset', `${Math.max(0, window.innerHeight - vv.height - vv.offsetTop)}px`
  );
  vv.addEventListener('resize', sync);
  vv.addEventListener('scroll', sync);
  sync();
}
```

**Installed PWAs.** In `standalone` / `fullscreen` display modes there is no browser chrome, so
`100vh` and `100dvh` converge — but the safe areas matter *more*, because nothing else is padding
the notch. Always ship `viewport-fit=cover` in an installable app, and set
`theme_color`/`background_color` in the manifest so the area behind the status bar is not white.

**Detecting standalone mode in CSS:**

```css
@media (display-mode: standalone) {
  .browser-only-banner { display: none; }
}
```

## 7. Verification

- DevTools device toolbar at 320 / 375 / 390 / 768 / 1024 / 1440 / 1920 px.
- Toggle "Show device frame" for an iPhone with a notch, in **both** orientations — landscape is
  where side insets bite and where most safe-area bugs actually appear.
- Zoom the browser to 200 % at 1280 px wide (this is the WCAG Reflow test: it is equivalent to a
  640 px viewport) and confirm no content is lost and no two-dimensional scrolling appears.
- Set the OS/browser base font size to 20 px and confirm `rem`-based breakpoints move the layout
  to a simpler tier rather than clipping.
