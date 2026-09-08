# responsive-viewport

An [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) that supplies the
*dimensional* layer of responsive web work: the viewport meta tag, safe-area insets, a breakpoint
and container-width system, real device widths in CSS pixels, fluid type, touch targets, and
CLS-safe images.

It is deliberately narrow. It does not have opinions about how a page should look — it has
opinions about the numbers, and about the handful of mistakes that break layouts regardless of
taste.

## Install

Copy the folder into your skills directory:

```bash
git clone https://github.com/SurendharVr/responsive-viewport.git ~/.claude/skills/responsive-viewport
```

Or drop the packaged `.skill` file into Claude and use **Save skill**.

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
