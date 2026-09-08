#!/usr/bin/env python3
"""Static responsive/viewport auditor.

Finds the mechanical responsive failures - the ones that are true regardless of
design taste - and reports them with file:line evidence so they can be fixed or
consciously waived. No dependencies; Python 3.8+.

    python check_responsive.py <path> [--json] [--strict] [--ext .html,.css]

Checks
  E  viewport-missing        an HTML document with no <meta name="viewport">
  E  viewport-zoom-locked    user-scalable=no / maximum-scale - WCAG 1.4.4 failure
  E  vw-width                width: 100vw (or w-screen) - includes the scrollbar
  W  vh-unit                 100vh with no dvh/svh fallback beside it
  W  img-no-dimensions       <img> with no width/height and no aspect-ratio
  W  desktop-first           max-width media queries outnumber min-width
  W  root-font-px            a px font-size on html/:root overrides user settings
  W  tiny-font               font-size below 12px
  W  safe-area-unused        viewport-fit=cover set, but no env(safe-area-inset-*)
  I  viewport-no-fit         viewport tag without viewport-fit=cover
  I  overflow-hidden-root    overflow-x: hidden on html/body (clip is safer)
  I  breakpoints             inventory of every breakpoint value found
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

MARKUP_EXT = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro",
              ".php", ".erb", ".hbs", ".ejs", ".liquid", ".twig", ".mdx"}
STYLE_EXT = {".css", ".scss", ".sass", ".less", ".styl", ".pcss"}
CODE_EXT = {".js", ".ts", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out",
             "vendor", "coverage", "__pycache__", ".venv", "venv", ".cache",
             "target", "bower_components", ".svelte-kit", "public/build"}

SEV_ORDER = {"error": 0, "warn": 1, "info": 2}
SEV_LABEL = {"error": "ERROR", "warn": "WARN ", "info": "INFO "}

RE_VIEWPORT_TAG = re.compile(r"""<meta[^>]*name\s*=\s*["']viewport["'][^>]*>""", re.I)
RE_VIEWPORT_CONTENT = re.compile(r"""content\s*=\s*["']([^"']*)["']""", re.I)
RE_HEAD = re.compile(r"<head[\s>]|<Head[\s>]|<html[\s>]", re.I)
RE_IMG = re.compile(r"<img\b[^>]*>", re.I | re.S)
RE_MEDIA = re.compile(r"@media[^{]{0,300}", re.I)
RE_MQ_LEGACY = re.compile(r"\b(min|max)-width\s*:\s*([\d.]+)\s*(px|rem|em)", re.I)
RE_MQ_RANGE = re.compile(r"\bwidth\s*(>=|<=|>|<)\s*([\d.]+)\s*(px|rem|em)", re.I)
RE_VH = re.compile(r"(?<![\w.-])(\d{2,3})vh\b")
RE_VW_WIDTH = re.compile(r"(?:^|[\s;{])(?:min-|max-)?width\s*:\s*100vw", re.I)
RE_TW_SCREEN = re.compile(r"\bw-screen\b")
RE_TW_HSCREEN = re.compile(r"\bh-screen\b")
RE_ROOT_FONT_PX = re.compile(
    r"(?:^|})\s*(?:html|:root)[^{}]{0,80}\{[^{}]{0,400}?font-size\s*:\s*(\d+)px", re.I | re.S)
RE_TINY_FONT = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
RE_OVERFLOW_HIDDEN = re.compile(
    r"(?:^|})\s*(?:html|body)[^{}]{0,80}\{[^{}]{0,400}?overflow(?:-x)?\s*:\s*hidden", re.I | re.S)


class Finding:
    def __init__(self, severity, check, path, line, message, fix):
        self.severity = severity
        self.check = check
        self.path = path
        self.line = line
        self.message = message
        self.fix = fix

    def as_dict(self):
        return {"severity": self.severity, "check": self.check, "file": self.path,
                "line": self.line, "message": self.message, "fix": self.fix}


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def iter_files(root, exts):
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for name in filenames:
            if os.path.splitext(name)[1].lower() in exts:
                yield os.path.join(dirpath, name)


def read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def to_px(value, unit):
    value = float(value)
    return value * 16 if unit.lower() in ("rem", "em") else value


def check_viewport(path, text, rel, findings, state):
    tags = list(RE_VIEWPORT_TAG.finditer(text))
    is_document = bool(RE_HEAD.search(text)) or path.lower().endswith((".html", ".htm"))

    if not tags:
        # Only a full document is expected to carry the tag; a partial/component is not.
        if is_document and "<body" in text.lower():
            findings.append(Finding(
                "error", "viewport-missing", rel, 1,
                "HTML document has no <meta name=\"viewport\">, so mobile browsers "
                "lay it out in a 980px virtual viewport and the mobile CSS never applies.",
                'Add <meta name="viewport" content="width=device-width, initial-scale=1, '
                'viewport-fit=cover"> as the first element in <head>.'))
        return

    for tag in tags:
        line = line_of(text, tag.start())
        content_match = RE_VIEWPORT_CONTENT.search(tag.group(0))
        content = (content_match.group(1) if content_match else "").lower()

        if "user-scalable" in content and re.search(r"user-scalable\s*=\s*(no|0)", content):
            findings.append(Finding(
                "error", "viewport-zoom-locked", rel, line,
                "user-scalable=no blocks pinch-zoom - a WCAG 1.4.4 (AA) failure. "
                "iOS Safari ignores it anyway, so it only breaks Android.",
                "Remove user-scalable. If the goal was stopping iOS input auto-zoom, set "
                "font-size: max(16px, 1rem) on input/select/textarea instead."))
        max_scale = re.search(r"maximum-scale\s*=\s*([\d.]+)", content)
        if max_scale and float(max_scale.group(1)) < 2:
            findings.append(Finding(
                "error", "viewport-zoom-locked", rel, line,
                "maximum-scale=%s caps zoom below 200%%, failing WCAG 1.4.4 (AA)."
                % max_scale.group(1),
                "Remove maximum-scale."))
        if "width=device-width" not in content.replace(" ", ""):
            findings.append(Finding(
                "error", "viewport-missing", rel, line,
                "Viewport tag does not set width=device-width, so media queries "
                "evaluate against the default 980px canvas.",
                'Use content="width=device-width, initial-scale=1, viewport-fit=cover".'))
        if "viewport-fit=cover" in content.replace(" ", ""):
            state["fit_cover"] = True
        elif is_document:
            findings.append(Finding(
                "info", "viewport-no-fit", rel, line,
                "No viewport-fit=cover, so env(safe-area-inset-*) will always return 0px "
                "and full-bleed surfaces stay letterboxed inside the notch area.",
                "Add viewport-fit=cover if the design has fixed bars or edge-to-edge media."))


def check_images(path, text, rel, findings):
    for tag in RE_IMG.finditer(text):
        raw = tag.group(0)
        lowered = raw.lower()
        has_dims = ("width=" in lowered and "height=" in lowered)
        has_ratio = ("aspect-ratio" in lowered or "aspect-[" in lowered
                     or re.search(r"\baspect-(video|square|auto|\w+)\b", lowered) is not None)
        # A JSX spread ({...props}) may carry width/height that we cannot see.
        has_spread = "{..." in raw
        if has_dims or has_ratio or has_spread:
            continue
        findings.append(Finding(
            "warn", "img-no-dimensions", rel, line_of(text, tag.start()),
            "<img> has no width/height attributes and no aspect-ratio, so the browser "
            "reserves no space and the page shifts when it loads (CLS).",
            "Add the intrinsic width/height attributes, or wrap in a box with "
            "aspect-ratio and object-fit: cover."))


def check_units(path, text, rel, findings):
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if RE_VW_WIDTH.search(line) or RE_TW_SCREEN.search(line):
            findings.append(Finding(
                "error", "vw-width", rel, index + 1,
                "100vw includes the desktop scrollbar gutter, making the element ~15px "
                "wider than the viewport and causing horizontal scroll.",
                "Use width: 100% (Tailwind: w-full), or 100dvw where a true viewport "
                "width is genuinely required."))
        for match in RE_VH.finditer(line):
            if match.group(1) != "100":
                continue
            # The correct pattern is a vh line immediately followed by a dvh/svh
            # line for the SAME property, so only that counts as a fallback -
            # a dvh anywhere else in the block is a different declaration.
            if re.search(r"(?:dvh|svh|lvh)\b", line):
                continue
            prop = re.search(r"([-\w]+)\s*:\s*[^;{]*100vh", line)
            nxt = lines[index + 1] if index + 1 < len(lines) else ""
            same_rule = "}" not in line[match.end():] and "{" not in nxt
            if (prop and same_rule and prop.group(1) in nxt
                    and re.search(r"(?:dvh|svh|lvh)\b", nxt)):
                continue
            findings.append(Finding(
                "warn", "vh-unit", rel, index + 1,
                "100vh equals the viewport height with mobile browser chrome hidden, so "
                "the bottom of the element is cut off on load.",
                "Keep 100vh as the fallback line and add min-height: 100dvh (or 100svh "
                "for content that must be fully visible) directly after it."))
        if RE_TW_HSCREEN.search(line):
            findings.append(Finding(
                "warn", "vh-unit", rel, index + 1,
                "Tailwind h-screen compiles to 100vh, which overflows mobile chrome.",
                "Use h-dvh (Tailwind 3.4+) or min-h-svh."))


def check_media_queries(path, text, rel, findings, state):
    mins = maxs = 0
    for block in RE_MEDIA.finditer(text):
        chunk = block.group(0)
        for kind, value, unit in RE_MQ_LEGACY.findall(chunk):
            px = to_px(value, unit)
            state["breakpoints"][int(round(px))] += 1
            if kind.lower() == "min":
                mins += 1
            else:
                maxs += 1
            if unit.lower() == "px" and px >= 480:
                state["px_breakpoints"] += 1
        for op, value, unit in RE_MQ_RANGE.findall(chunk):
            px = to_px(value, unit)
            state["breakpoints"][int(round(px))] += 1
            if op in (">=", ">"):
                mins += 1
            else:
                maxs += 1
            if unit.lower() == "px" and px >= 480:
                state["px_breakpoints"] += 1

    if maxs >= 3 and maxs > mins:
        findings.append(Finding(
            "warn", "desktop-first", rel, 1,
            "%d max-width queries vs %d min-width: this stylesheet is desktop-first, so "
            "every component must be undone at small sizes - the usual source of mobile "
            "overflow bugs." % (maxs, mins),
            "Invert: make the base styles the mobile styles and add min-width queries "
            "upward. Keep max-width for genuine exceptions only."))


def check_css_details(path, text, rel, findings, state):
    if "env(safe-area-inset" in text:
        state["uses_safe_area"] = True

    for match in RE_ROOT_FONT_PX.finditer(text):
        inner = text.rfind("font-size", match.start(), match.end())
        findings.append(Finding(
            "warn", "root-font-px", rel, line_of(text, inner if inner > 0 else match.start()),
            "A px font-size on html/:root overrides the user's browser font-size "
            "preference and makes every rem-based size ignore it.",
            "Use a percentage (100% / 62.5%) or drop the declaration entirely."))

    for match in RE_TINY_FONT.finditer(text):
        size = float(match.group(1))
        if size < 12:
            findings.append(Finding(
                "warn", "tiny-font", rel, line_of(text, match.start()),
                "font-size: %gpx is below the 12px legibility floor." % size,
                "Raise to at least 12px; body copy should be 16px on mobile."))

    for match in RE_OVERFLOW_HIDDEN.finditer(text):
        inner = text.rfind("overflow", match.start(), match.end())
        findings.append(Finding(
            "info", "overflow-hidden-root", rel, line_of(text, inner if inner > 0 else match.start()),
            "overflow: hidden on html/body silently disables position: sticky in "
            "descendants.",
            "Use overflow-x: clip instead, and find the element that actually overflows."))


def audit(root, exts):
    findings = []
    state = {"fit_cover": False, "uses_safe_area": False,
             "breakpoints": Counter(), "px_breakpoints": 0, "files": 0}

    for path in iter_files(root, exts):
        text = read(path)
        if not text:
            continue
        state["files"] += 1
        rel = os.path.relpath(path, root if os.path.isdir(root) else os.path.dirname(root))
        ext = os.path.splitext(path)[1].lower()

        if ext in MARKUP_EXT:
            check_viewport(path, text, rel, findings, state)
            check_images(path, text, rel, findings)
        if ext in STYLE_EXT or ext in CODE_EXT or ext in MARKUP_EXT:
            check_units(path, text, rel, findings)
        if ext in STYLE_EXT or ext in CODE_EXT:
            check_media_queries(path, text, rel, findings, state)
        if ext in STYLE_EXT:
            check_css_details(path, text, rel, findings, state)
        if "env(safe-area-inset" in text:
            state["uses_safe_area"] = True

    if state["fit_cover"] and not state["uses_safe_area"]:
        findings.append(Finding(
            "warn", "safe-area-unused", "(project)", 0,
            "viewport-fit=cover is set, so the page paints under the notch and home "
            "indicator, but no env(safe-area-inset-*) padding was found anywhere.",
            "Pad fixed bars and page gutters with max(<design padding>, "
            "env(safe-area-inset-*))."))

    return findings, state


def report(findings, state, root):
    findings.sort(key=lambda f: (SEV_ORDER[f.severity], f.check, f.path, f.line))
    counts = Counter(f.severity for f in findings)

    print("responsive-viewport audit - %s" % os.path.abspath(root))
    print("%d files scanned | %d errors | %d warnings | %d info\n"
          % (state["files"], counts["error"], counts["warn"], counts["info"]))

    if not findings:
        print("No mechanical responsive failures found.")
    else:
        grouped = defaultdict(list)
        for finding in findings:
            # Group on the message too: one check can have distinct causes
            # (a CSS 100vh and a Tailwind h-screen) that need different fixes.
            grouped[(finding.severity, finding.check, finding.message)].append(finding)
        for key in sorted(grouped, key=lambda k: (SEV_ORDER[k[0]], k[1], k[2])):
            severity, check = key[0], key[1]
            items = grouped[key]
            print("%s %s  (%d)" % (SEV_LABEL[severity], check, len(items)))
            print("  %s" % items[0].message)
            print("  fix: %s" % items[0].fix)
            seen = []
            for finding in items:
                where = "%s:%d" % (finding.path, finding.line)
                if where not in seen:
                    seen.append(where)
            for where in seen[:12]:
                print("    %s" % where)
            if len(seen) > 12:
                print("    ... and %d more" % (len(seen) - 12))
            print()

    if state["breakpoints"]:
        print("INFO  breakpoints - every media query width in the codebase, in px:")
        entries = sorted(state["breakpoints"].items())
        print("  " + ", ".join("%d (x%d)" % (px, n) for px, n in entries))
        if len(entries) > 6:
            print("  %d distinct breakpoints. More than ~6 is usually accidental - "
                  "consolidate onto one scale so a change is a one-line edit." % len(entries))
        if state["px_breakpoints"]:
            print("  %d queries use px. rem breakpoints (48rem, 64rem, 90rem) also respond "
                  "to the user's font-size setting." % state["px_breakpoints"])
        print()

    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", default=".", help="file or directory to audit")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    parser.add_argument("--strict", action="store_true", help="exit 1 when errors are found")
    parser.add_argument("--ext", help="comma-separated extension allowlist, e.g. .html,.css")
    args = parser.parse_args()

    exts = MARKUP_EXT | STYLE_EXT | CODE_EXT
    if args.ext:
        exts = {e if e.startswith(".") else "." + e
                for e in (x.strip().lower() for x in args.ext.split(",")) if e}

    if not os.path.exists(args.path):
        print("path not found: %s" % args.path, file=sys.stderr)
        return 2

    findings, state = audit(args.path, exts)

    if args.json:
        print(json.dumps({
            "root": os.path.abspath(args.path),
            "files_scanned": state["files"],
            "breakpoints_px": dict(sorted(state["breakpoints"].items())),
            "findings": [f.as_dict() for f in findings],
        }, indent=2))
        counts = Counter(f.severity for f in findings)
    else:
        counts = report(findings, state, args.path)

    return 1 if (args.strict and counts["error"]) else 0


if __name__ == "__main__":
    sys.exit(main())
