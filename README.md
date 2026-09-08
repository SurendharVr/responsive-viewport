# responsive-viewport

[![CI](https://github.com/SurendharVr/responsive-viewport/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/SurendharVr/responsive-viewport/actions/workflows/ci.yml)

A **Claude Code [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) for responsive
web design**. It gives Claude the numbers and the rules
for making a web app render correctly from a 320px phone to a 3440px ultra-wide monitor: CSS
breakpoints, container max-widths, media queries and container queries, the `<meta name="viewport">`
tag, safe-area insets for the iPhone notch and home indicator, `dvh`/`svh` viewport units, fluid
typography with `clamp()`, 44px touch targets, and images that do not shift the layout (CLS).

Reach for it when a page has a **horizontal scrollbar on mobile**, a hero **cut off on iOS
Safari**, a fixed bar **under the home indicator**, a component that looks wrong in one container
but fine in another, a layout **stranded in the middle of an ultra-wide monitor**, or a team that
cannot agree on which breakpoints to use.

It is deliberately narrow. It has no opinions about how a page should look — only about the
numbers, and about the handful of mistakes that break layouts regardless of taste. Pair it with a
visual-design skill and let each own its half.

## Install

Copy the folder into your skills directory:

```bash
git clone https://github.com/SurendharVr/responsive-viewport.git ~/.claude/skills/responsive-viewport
```

Or download the packaged `.skill` from the
[latest release](https://github.com/SurendharVr/responsive-viewport/releases/latest),
drop it into Claude, and use **Save skill**.

## Usage

You don't invoke it by name. Once installed it loads on its own when a task touches responsive
layout — including when the word "responsive" never appears. These are verbatim prompts from its
trigger benchmark, all of which pull it in:

> our pricing table has a horizontal scrollbar on my galaxy s23 but only on the /pricing page,
> everything else is fine

> the checkout footer with the pay button sits underneath the home indicator on iphone and people
> keep mis-tapping it

> h1 on our landing page is a hardcoded 72px and it wraps like garbage on a phone. i'd rather it
> scaled smoothly than me adding a fourth media query

> QA currently tests 'mobile, tablet and desktop' which means nothing and they keep missing stuff

### What it actually changes

Given a page reported as "sideways scrollbar, hero cut off on load, bottom nav under the home
indicator", it works in dependency order — document contract, then container and breakpoints, then
fluid type, then verification at real widths. The diff it produced for exactly that report:

```css
/* before */
.hero       { height: 100vh; width: 100vw; }
.bottom-bar { position: fixed; left: 0; right: 0; bottom: 0; padding: 10px 0; }

/* after */
.hero {
  min-block-size: 100vh;                               /* fallback for old engines */
  min-block-size: calc(100dvh - var(--bottom-bar-h));  /* dvh tracks mobile chrome */
}
.bottom-bar {
  position: fixed;
  inset-inline: 0;                                     /* logical: RTL for free */
  inset-block-end: 0;
  /* pad past the home indicator rather than moving the bar, so its
     background still fills the inset */
  padding-block: var(--space-s) calc(var(--space-s) + var(--safe-bottom));
}
```

It also removed `user-scalable=no` from the viewport tag (a WCAG 1.4.4 failure), added
`viewport-fit=cover` so the safe-area insets resolve at all, and replaced the five desktop-first
`max-width` queries (1200/900/700/600/480 px) with four mobile-first `rem` ones — the feature grid
needed no breakpoint of its own once it used `repeat(auto-fit, minmax(min(18rem, 100%), 1fr))`.

### Auditing an existing codebase

```bash
python scripts/check_responsive.py ./src
```

Run this before asking for changes — it gives file:line evidence instead of guesses, so the
conversation starts from facts. See [The auditor](#the-auditor) for the full check list.

## What's inside

| Path | What it is |
|---|---|
| `SKILL.md` | The workflow, the breakpoint/container table, and the non-negotiable rules |
| `references/viewport-and-safe-areas.md` | Every viewport meta attribute, the WCAG case against locking zoom, `env(safe-area-inset-*)` recipes, `dvh`/`svh`/`lvh`, keyboard and PWA cases |
| `references/breakpoints-and-containers.md` | Six-tier breakpoint table with container max-widths, plain CSS / Tailwind v3 + v4 / SCSS implementations, container and capability queries |
| `references/device-matrix.md` | Logical CSS pixel dimensions for current iPhones, Galaxies, iPads, MacBooks, Windows laptops, 1080p/1440p/4K/ultra-wide, and foldables |
| `references/fluid-type-and-media.md` | `clamp()` arithmetic, a full fluid type and space scale, touch-target standards, responsive images, a CLS checklist |
| `assets/responsive-base.css` | Drop-in foundation stylesheet — tokens, container, safe areas, fluid scale. No colours, no components |
| `scripts/check_responsive.py` | Dependency-free static auditor, 12 checks |

## The auditor

```bash
python scripts/check_responsive.py <path-to-site>
```

Reports missing or zoom-locked viewport tags, `100vh`/`100vw` misuse, images without reserved
space, desktop-first media query chains, `viewport-fit=cover` with no safe-area padding, and an
inventory of every breakpoint value in the codebase. `--json` for machine output, `--strict` to
exit non-zero on errors. Python 3.8+, no dependencies.

## Does it actually help?

It was benchmarked against a no-skill baseline on the same model, using assertions written and
frozen *before* the runs: four tasks (fix a broken landing page, write a breakpoint spec, build a
hero + card grid, build an ultra-wide dashboard that also survives a folded phone), 53 assertions.

**With skill 100%, baseline 78%.** The baseline's failures were real defects — a `px` `font-size`
on `html` at ultra-wide breakpoints, `overflow-x: hidden` on `body` under a design that relies on
`position: sticky`, px-only breakpoints, and no `pointer: coarse` branch anywhere.

Two honest caveats:

- On the **pure knowledge task** (write a breakpoint spec) the skill and the baseline tied at 9/9.
  A capable model already knows this material; the skill's value is in applying it consistently
  in code, not in recalling it.
- It costs roughly **25k extra tokens** per task. Worth it for code, not obviously worth it for
  answering a question.

An earlier round with a weaker assertion set scored 100% for both configurations — that null
result is what prompted the harder assertions, and it is kept in the record rather than dropped.

## Tests

```bash
python tests/test_auditor.py
```

Standard library only, no pytest. Asserts every auditor check actually fires on a fixture that
violates it, that a clean fixture stays clean (including the `100vh` → `100dvh` fallback pattern,
which must not be flagged), that `--strict` exit codes are right, that `--json` is well formed,
and that the shipped `assets/responsive-base.css` passes its own auditor.

## Related skills

Pairs with, and does not replace, `hallmark` (visual craft), `ui-styling` (Tailwind/shadcn
implementation) and `ui-ux-pro-max` (style, palette, font pairing). Use this one for the numbers
and let those own the aesthetics.

## Licence

MIT.
