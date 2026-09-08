#!/usr/bin/env python3
"""Tests for scripts/check_responsive.py. Standard library only, no pytest.

    python tests/test_auditor.py

Fixtures are written to a temp directory rather than committed, so the repo
stays free of files that look like real source but are deliberately broken.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDITOR = ROOT / "scripts" / "check_responsive.py"

BAD_HTML = """<!doctype html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>t</title></head>
<body>
<img src="a.jpg" alt="a">
<div class="w-screen h-screen"></div>
</body></html>
"""

BAD_CSS = """html { font-size: 16px; }
body { overflow-x: hidden; }
.hero { width: 100vw; }
.tall { min-height: 100vh; }
.tiny { font-size: 10px; }
@media (max-width: 767px) { .a { display: none } }
@media (max-width: 900px) { .b { display: none } }
@media (max-width: 1199px) { .c { display: none } }
"""

GOOD_HTML = """<!doctype html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>t</title></head>
<body>
<img src="a.jpg" alt="a" width="800" height="600">
</body></html>
"""

GOOD_CSS = """html, body { overflow-x: clip; }
body { padding-bottom: env(safe-area-inset-bottom, 0px); }
.hero { width: 100%; min-height: 100vh; min-height: 100dvh; }
.btn { min-height: 44px; }
@media (width >= 48rem) { .a { display: block } }
@media (width >= 64rem) { .b { display: block } }
"""

NO_META = "<!doctype html><html><head><title>t</title></head><body><p>hi</p></body></html>"

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  PASS  %s" % name)
    else:
        print("  FAIL  %s %s" % (name, detail))
        failures.append(name)


def run(path, *args):
    proc = subprocess.run(
        [sys.executable, str(AUDITOR), str(path), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def write(directory, **files):
    for name, body in files.items():
        (directory / name.replace("__", ".")).write_text(body, encoding="utf-8")


def main():
    print("auditor tests")
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad"
        bad.mkdir()
        write(bad, index__html=BAD_HTML, style__css=BAD_CSS)
        (bad / "nometa.html").write_text(NO_META, encoding="utf-8")

        code, out = run(bad)
        # Each check must actually fire on a fixture that violates it. A check
        # that never fires is worse than no check - it reads as a clean bill.
        for expected in ("viewport-zoom-locked", "viewport-missing", "vw-width",
                         "vh-unit", "img-no-dimensions", "desktop-first",
                         "root-font-px", "tiny-font", "overflow-hidden-root"):
            check("detects %s" % expected, expected in out)
        check("exit 0 without --strict", code == 0, "(got %d)" % code)

        code, _ = run(bad, "--strict")
        check("exit 1 with --strict when errors exist", code == 1, "(got %d)" % code)

        good = Path(tmp) / "good"
        good.mkdir()
        write(good, index__html=GOOD_HTML, style__css=GOOD_CSS)
        code, out = run(good)
        check("clean fixture reports no errors", "0 errors" in out, out[:120])
        check("clean fixture reports no warnings", "0 warnings" in out, out[:120])
        check("dvh fallback is not flagged", "vh-unit" not in out)
        check("exit 0 with --strict on a clean tree", run(good, "--strict")[0] == 0)

        code, out = run(good, "--json")
        try:
            payload = json.loads(out)
            check("--json emits valid JSON", True)
            check("--json carries the expected keys",
                  {"root", "files_scanned", "breakpoints_px", "findings"} <= set(payload))
            check("--json findings are empty on a clean tree",
                  [f for f in payload["findings"] if f["severity"] == "error"] == [])
        except json.JSONDecodeError as exc:
            check("--json emits valid JSON", False, str(exc))

    # The skill ships a foundation stylesheet; it must satisfy its own auditor,
    # or the advice and the example disagree.
    code, out = run(ROOT / "assets")
    check("assets/responsive-base.css passes the auditor",
          "0 errors" in out and "0 warnings" in out, out[:160])

    if failures:
        print("\n%d FAILED: %s" % (len(failures), ", ".join(failures)))
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
