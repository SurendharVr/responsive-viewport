# Changelog

All notable changes to this skill are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) — where "behaviour" means the guidance
`SKILL.md` gives, the reference content, the stylesheet, and the auditor's output.

## [1.1.1] — 2026-09-08

Documentation only. Nothing in the skill's behaviour changed from 1.1.0; every file except
`README.md` is byte-identical.

### Added

- **Usage** section with a real before/after diff, taken from a benchmark run rather than written
  for the README — a `100vh` hero that clipped on iOS Safari becoming
  `min-block-size: calc(100dvh - var(--bottom-bar-h))`, and a fixed bottom bar padded past the
  home indicator so its background still fills the inset.
- **How to prompt it** — copy-pasteable prompts grouped by intent (fix / build / audit / decide /
  verify), the habits that make a prompt land, and a table of what belongs to other skills. Every
  row in that table is a query the trigger benchmark verified this skill declines.
- CI status badge, pinned to `main`.

### Changed

- README opens with the language people search for rather than "the dimensional layer of
  responsive web work". The scope statement kept its place, just not the first paragraph.
- Install links directly at the versioned `.skill` asset instead of the release page.

## [1.1.0] — 2026-09-08

First published release. Adds the rules that a benchmark showed were the difference between the
skill and an unaided model, and packages the whole thing.

### Added

- Four rules promoted into the non-negotiables list, each with its reasoning: breakpoints in `rem`
  and capped at about six; never a `px` `font-size` on `html`/`:root`; `overflow-x: clip` rather
  than `hidden`; affordances branching on `hover`/`pointer` capability rather than width.
- A reference-loading cost rule — the tables in `SKILL.md` answer a spec question, so the
  reference files are for when code has to be exactly right. Cut token use on knowledge tasks by
  roughly 13% with no loss of coverage.
- `container queries` named in the description, after the trigger benchmark found the skill was
  invisible for the one problem class it is most specifically useful for.
- `tests/test_auditor.py` — 19 checks, standard library only, asserting that every auditor check
  fires on a fixture that violates it.
- CI on Python 3.8 and 3.12; `README`, `LICENSE`, `.gitattributes`, `.gitignore`.

### Changed

- Description reworded to drop angle brackets, which the skill packager rejects.
- `version` moved under `metadata` in the frontmatter, for the same reason.

### Notes

Benchmarked against a no-skill baseline with assertions frozen before the runs: 100% versus 78%
across 53 assertions on four tasks. Tied on pure spec recall — see the README for the caveats.

## [1.0.0] — 2026-09-08

Initial version, before the repository existed. `SKILL.md`, the four references, the foundation
stylesheet, and `scripts/check_responsive.py`. Never tagged or released; it is recorded here so
the version history is complete.

## Withdrawn

- **1.2.0** — published briefly on 2026-09-08 and removed the same day. The change from 1.1.0 was
  `README.md` alone, which is a patch rather than a minor, so it was re-cut as 1.1.1. The tag and
  release were deleted rather than left standing as a misleading version number.

[1.1.1]: https://github.com/SurendharVr/responsive-viewport/releases/tag/v1.1.1
[1.1.0]: https://github.com/SurendharVr/responsive-viewport/releases/tag/v1.1.0
