# Device Dimensions Reference

All figures are **logical CSS pixels** — the number a media query sees — not physical pixels.
`DPR` (device pixel ratio) is the multiplier between the two, and is what `srcset` densities and
`@2x`/`@3x` assets are for.

> Screen size ≠ viewport size. Subtract browser chrome: roughly **80–180 px of height** on mobile
> (URL bar + toolbar, varying as they collapse on scroll) and **90–140 px** on desktop (tab strip,
> address bar, bookmarks bar), plus ~15 px of width for a classic desktop scrollbar. Design to the
> width; treat the height as a moving target and use `dvh`/`svh` rather than fixed numbers.

Contents:
1. Mobile
2. Tablet
3. Laptop
4. Desktop & ultra-wide
5. The widths that actually matter
6. Foldables and other outliers

---

## 1. Mobile (portrait, CSS px)

| Device | Width × Height | DPR | Notes |
|---|---|---|---|
| iPhone SE (2nd/3rd gen) | **375 × 667** | 2 | The smallest current iPhone. Best small-screen test target. |
| iPhone 12 / 13 / 14 | **390 × 844** | 3 | |
| iPhone 13 mini | 375 × 812 | 3 | |
| iPhone 14 Pro / 15 / 15 Pro / 16 | **393 × 852** | 3 | Dynamic Island; safe-area-inset-top ≈ 59 px |
| iPhone 16 Pro | 402 × 874 | 3 | |
| iPhone 14 Plus | 428 × 926 | 3 | |
| iPhone 14 Pro Max / 15 Plus / 15 Pro Max / 16 Plus | **430 × 932** | 3 | |
| iPhone 16 Pro Max | 440 × 956 | 3 | |
| Samsung Galaxy S23 / S24 (base) | **360 × 780** | 3 | 360 px is the dominant Android width worldwide |
| Samsung Galaxy S23+ / S24+ | 384 × 832 | 3 | |
| Samsung Galaxy S23 Ultra / S24 Ultra | **384 × 824** | 3.75 | Samsung's system "display size" setting shifts this by ±10 %; treat as approximate |
| Google Pixel 7 / 8 | 412 × 915 | 2.625 | |
| Google Pixel 8 Pro | 448 × 998 | 2.625 | |
| Budget Android (very common in APAC/LatAm) | 360 × 640 | 2 | Still a meaningful share of global traffic |

**Safe-area insets, iPhone with notch/Island (portrait):** top ≈ 44–59 px, bottom ≈ 34 px.
**Landscape:** left/right ≈ 44–59 px, bottom ≈ 21 px. Android cutouts are usually 24–40 px top.

**Landscape widths** are the portrait heights: an iPhone 15 in landscape is 852 × 393, which lands
in the *tablet portrait* breakpoint tier with only ~393 px of height. Any layout with a fixed
header, fixed footer and a form is worth checking there — it is the tightest vertical case in the
whole matrix.

## 2. Tablet (portrait, CSS px)

| Device | Width × Height | DPR | Notes |
|---|---|---|---|
| iPad mini (6th gen) | **744 × 1133** | 2 | Just under the 768 px tablet breakpoint — deliberately awkward, always test it |
| iPad (10th gen) | 820 × 1180 | 2 | |
| iPad Air 11" (M2) | **820 × 1180** | 2 | |
| iPad Air 13" (M2) | 1024 × 1366 | 2 | |
| iPad Pro 11" | **834 × 1194** | 2 | M4 model: 834 × 1210 |
| iPad Pro 12.9" | **1024 × 1366** | 2 | M4 13": 1032 × 1376 |
| Samsung Galaxy Tab S9 | 800 × 1280 | 2.25 | |
| Surface Pro 9 | 912 × 1368 | 2 | |

Landscape iPad Pro 12.9" is **1366 × 1024** — a laptop-tier width with a touch pointer. This is
the case that proves width alone is not enough: use `@media (pointer: coarse)` to keep 44 px
targets there. iPadOS Split View also hands the page arbitrary widths as narrow as ~320 px, so
never assume an iPad means a wide viewport.

## 3. Laptop (CSS px, default OS scaling)

macOS ships HiDPI laptops at a *scaled* default resolution — the CSS pixel size is neither the
panel's native resolution nor half of it.

| Device | CSS viewport width × height | DPR | Notes |
|---|---|---|---|
| MacBook Air 13" (M1) | 1440 × 900 | 2 | |
| MacBook Air 13" (M2/M3) | **1470 × 956** | 2 | Native 2560 × 1664, default scaled |
| MacBook Pro 14" | **1512 × 982** | 2 | Native 3024 × 1964 |
| MacBook Air 15" | 1710 × 1112 | 2 | |
| MacBook Pro 16" | **1728 × 1117** | 2 | Native 3456 × 2234 |
| Windows 13–14", 1080p @ 150 % scaling | **1280 × 720** | 1.5 | |
| Windows 13–14", 1080p @ 125 % scaling | **1536 × 864** | 1.25 | Consistently one of the top widths in real analytics |
| Windows 15–16", 1080p @ 100 % | **1920 × 1080** | 1 | |
| Windows 14", 1440p @ 150 % | 1707 × 960 | 1.5 | |
| Chromebook (typical) | 1366 × 768 | 1 | |

Because of OS scaling, **DPR on Windows is frequently fractional** (1.25, 1.5, 1.75). Do not
write `@media (-webkit-min-device-pixel-ratio: 2)` asset switches; use `srcset` density or width
descriptors and let the browser choose.

## 4. Desktop & ultra-wide (CSS px at 100 % OS scaling)

| Class | Screen | Typical maximised viewport | Notes |
|---|---|---|---|
| 1080p standard | **1920 × 1080** | ~1920 × 940 | Still the most common desktop resolution |
| 1200p | 1920 × 1200 | ~1920 × 1060 | |
| 1440p / 2K | **2560 × 1440** | ~2560 × 1300 | At the common 125 % scaling this reports **2048 × 1152** |
| 4K / UHD | **3840 × 2160** | ~3840 × 2020 | Almost always scaled: 150 % → **2560 × 1440** CSS, DPR 1.5; 200 % → 1920 × 1080 CSS, DPR 2 |
| Ultra-wide 21:9 | **3440 × 1440** | ~3440 × 1300 | |
| Ultra-wide 21:9 (entry) | 2560 × 1080 | ~2560 × 940 | Note the *short* height — vertical space is the constraint here, not width |
| Super ultra-wide 32:9 | **5120 × 1440** | ~5120 × 1300 | Users overwhelmingly run browsers windowed/tiled here, so the real viewport is often 1700–2500 px |
| 5K iMac / Studio Display | 5120 × 2880 | 2560 × 1440 CSS | DPR 2 |

The practical consequence: a 4K monitor almost never reports a 3840 px viewport. Above about
1920 px you are designing for *windowed* browsers as much as for maximised ones, which is another
reason the container caps out rather than tracking the screen.

## 5. The widths that actually matter

Testing every row above is waste. Test these seven, which bracket every tier:

| Width | Stands for |
|---|---|
| **320** | Absolute floor; iPhone SE 1st gen, and the WCAG reflow endpoint |
| **375** | iPhone SE 2/3 — the smallest device in meaningful current use |
| **390** | The modal iPhone |
| **768** | iPad portrait / the tablet breakpoint boundary |
| **1024** | iPad landscape / small laptop / the laptop boundary |
| **1440** | Large desktop, MacBook Pro class |
| **1920** | 1080p maximised, and the ultra-wide entry point |

Add **744** (iPad mini) if the product has real tablet traffic, and **360** if Android is a major
segment. Always check at least one *landscape phone* (e.g. 852 × 393) for vertical crowding.

Then confirm against the product's own analytics rather than this table — the top five viewport
sizes in a real audience are often surprising, and they are the ones worth pixel-polishing.

## 6. Foldables and other outliers

| Device | Folded | Unfolded | Note |
|---|---|---|---|
| Galaxy Z Fold 5/6 | 344 × 882 | 673 × 841 | Folded is *narrower than 360* — the real modern floor |
| Galaxy Z Flip 5/6 | 360 × 748 (cover 720 × 748) | 360 × 748 | |
| Surface Duo | 540 × 720 | 720 × 720 (dual) | |

Foldables resize the viewport mid-session with no page reload, which is a good stress test: if a
layout survives a live 344 → 673 px transition, it has no hidden width assumptions. The CSS
Viewport Segments API (`@media (horizontal-viewport-segments: 2)`) exists for dual-screen layout
but is not worth targeting unless the audience demands it.
