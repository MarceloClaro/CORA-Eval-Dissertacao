#!/usr/bin/env python3
"""
test_quality.py — TDD Test Suite 3: Quality Gate
======================================================================
RED CONDITION (fails when):
  1. Any overfull hbox >= 12.0pt (severe typographic overflow)
  2. More than 8 overfull boxes total (excessive typographic issues)
  3. Any underfull hbox with badness >= 10000 (severe underfill)
  4. Widow/orphan lines detected (club/widow penalty not configured)
  5. Font substitution warnings (LaTeX Font Warning: replacement)

GREEN CONDITION (passes when):
  All 5 tests pass -> document meets typographic quality standards

FIX STRATEGIES:
  - Overfull < 3pt: auto-fix via \begin{sloppypar}...\end{sloppypar} (F01)
  - Overfull >= 3pt: text shortening — remove adverbs, simplify
    connectives, contract expressions (F04)
  - Underfull in p{} columns: replace with raggedright column (F02)
  - Underfull in paragraphs: \looseness=-1 or sloppy local (F03)
  - Widow/orphan: configure \clubpenalty and \widowpenalty in preamble
  - Font warnings: ensure all font packages are properly loaded

THRESHOLDS:
  TOLERANCE_OVERFULL_PT    = 12.0   (pt)
  MAX_OVERFULL_COUNT       = 8      (boxes)
  TOLERANCE_UNDERFULL_BADNESS = 10000 (LaTeX badness scale)

RELATION TO FRAMEWORK:
  - This is the THIRD quality gate in the SDD+TDD pipeline
  - Must pass 100% for the document to be considered "clean"
  - Refer to SPEC_ORCHESTRATION.md §4.3 and FRAMEWORK.md §5 for
    the complete catalog of fix strategies
======================================================================
"""

import sys
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "artigo_150_questoes.log")
PASS = 0
FAIL = 1

TOLERANCE_OVERFULL_PT = 12.0  # max acceptable overfull in points
TOLERANCE_UNDERFULL_BADNESS = 10000  # max acceptable underfull badness
MAX_OVERFULL_COUNT = 8  # max number of overfull boxes


def load_log():
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def test_overfull_threshold():
    """Test 3.1: No overfull box exceeds tolerance."""
    print(f"  [TEST 3.1] Overfull boxes < {TOLERANCE_OVERFULL_PT}pt... ", end="")
    log = load_log()

    overfull_pattern = re.compile(
        r"Overfull \\hbox \(([0-9.]+)pt too wide\)",
        re.IGNORECASE
    )
    overfulls = [(float(m.group(1)), m.group(0)) for m in overfull_pattern.finditer(log)]

    violations = [o for o in overfulls if o[0] > TOLERANCE_OVERFULL_PT]

    if len(violations) == 0:
        if len(overfulls) > 0:
            print(f"PASS ({len(overfulls)} cosmetic, max {max(o[0] for o in overfulls):.1f}pt)")
        else:
            print("PASS (zero)")
        return True
    else:
        print(f"FAIL ({len(violations)} exceed {TOLERANCE_OVERFULL_PT}pt)")
        for pts, line in violations[:3]:
            print(f"    {line}")
        return False


def test_overfull_count():
    """Test 3.2: Total overfull boxes within limit."""
    print(f"  [TEST 3.2] Overfull count <= {MAX_OVERFULL_COUNT}... ", end="")
    log = load_log()

    overfull_pattern = re.compile(
        r"Overfull \\hbox",
        re.IGNORECASE
    )
    count = len(overfull_pattern.findall(log))

    if count <= MAX_OVERFULL_COUNT:
        print(f"PASS ({count} boxes)")
        return True
    else:
        print(f"FAIL ({count} boxes > {MAX_OVERFULL_COUNT})")
        return False


def test_underfull_threshold():
    """Test 3.3: No underfull box exceeds max badness."""
    print(f"  [TEST 3.3] Underfull badness < {TOLERANCE_UNDERFULL_BADNESS}... ", end="")
    log = load_log()

    underfull_pattern = re.compile(
        r"Underfull \\hbox \(badness (\d+)\)",
        re.IGNORECASE
    )
    underfulls = [(int(m.group(1)), m.group(0)) for m in underfull_pattern.finditer(log)]

    violations = [u for u in underfulls if u[0] >= TOLERANCE_UNDERFULL_BADNESS]

    if len(violations) == 0:
        if len(underfulls) > 0:
            print(f"PASS ({len(underfulls)} boxes, max badness {max(u[0] for u in underfulls)})")
        else:
            print("PASS (zero)")
        return True
    else:
        print(f"FAIL ({len(violations)} exceed badness {TOLERANCE_UNDERFULL_BADNESS})")
        return False


def test_widow_orphan():
    """Test 3.4: No widow/orphan warnings."""
    print("  [TEST 3.4] Widow/orphan lines... ", end="")
    log = load_log()

    widow_pattern = re.compile(r"(widow|orphan|club)", re.IGNORECASE)
    widows = widow_pattern.findall(log)

    if len(widows) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL ({len(widows)} warnings)")
        return False


def test_font_warnings():
    """Test 3.5: No font substitution warnings."""
    print("  [TEST 3.5] Font warnings... ", end="")
    log = load_log()

    font_warn_pattern = re.compile(
        r"LaTeX Font Warning:.*?replacement",
        re.IGNORECASE
    )
    font_warns = font_warn_pattern.findall(log)

    if len(font_warns) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL ({len(font_warns)} font substitutions)")
        return False


def main():
    print(f"\n{'='*60}")
    print("  TDD TEST SUITE — Quality Gate")
    print(f"{'='*60}\n")

    tests = [
        test_overfull_threshold,
        test_overfull_count,
        test_underfull_threshold,
        test_widow_orphan,
        test_font_warnings,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"  RESULT: {passed}/{len(tests)} passed, {failed} failed")
    print(f"{'='*60}\n")

    return PASS if failed == 0 else FAIL


if __name__ == "__main__":
    sys.exit(main())
