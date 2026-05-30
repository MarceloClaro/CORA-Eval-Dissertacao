#!/usr/bin/env python3
"""
test_compile.py — TDD Test Suite 1: Compilation Gate
======================================================================
RED CONDITION (fails when):
  1. pdflatex returns non-zero exit code
  2. Any LaTeX error (lines starting with '!') in .log
  3. Any undefined reference or citation (LaTeX Warning)
  4. PDF file missing or < 100 KB
  5. Cross-references not settled (Rerun warnings)

GREEN CONDITION (passes when):
  All 5 tests pass -> compilation is sound, PDF is valid

FIX STRATEGIES:
  - Undefined refs: recompile with 2 passes
  - LaTeX errors: manual correction required (not auto-fixable)
  - Missing PDF: check pdflatex installation and disk space

RELATION TO FRAMEWORK:
  - This is the FIRST quality gate in the SDD+TDD pipeline
  - Must pass 100% before Structure and Quality gates run
  - Refer to SPEC_ORCHESTRATION.md §4.1 for detailed criteria
======================================================================
"""

import subprocess
import sys
import os
import re

# Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_FILE = os.path.join(BASE_DIR, "artigo_150_questoes.tex")
LOG_FILE = os.path.join(BASE_DIR, "artigo_150_questoes.log")
PDF_FILE = os.path.join(BASE_DIR, "artigo_150_questoes.pdf")
PASS = 0
FAIL = 1


def test_compilation_succeeds():
    """Test 1.1: pdflatex must return exit code 0."""
    print("  [TEST 1.1] Compilation exit code... ", end="")
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", TEX_FILE],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL (exit code {result.returncode})")
        # Print last 10 lines of output
        lines = result.stdout.split("\n")
        for line in lines[-10:]:
            print(f"    {line}")
        return False


def test_no_latex_errors():
    """Test 1.2: Log must contain no errors (lines starting with '!')."""
    print("  [TEST 1.2] LaTeX errors in log... ", end="")
    if not os.path.exists(LOG_FILE):
        print("FAIL (log not found)")
        return False

    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        log = f.read()

    errors = re.findall(r"^! ", log, re.MULTILINE)
    if len(errors) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL ({len(errors)} error(s) found)")
        for err in errors[:5]:
            print(f"    {err}")
        return False


def test_no_undefined_refs():
    """Test 1.3: No undefined references or citations."""
    print("  [TEST 1.3] Undefined refs/cites... ", end="")
    if not os.path.exists(LOG_FILE):
        print("FAIL (log not found)")
        return False

    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        log = f.read()

    # Check for LaTeX warnings about undefined refs
    undefined_refs = re.findall(
        r"LaTeX Warning: (Citation|Reference) `.*?' (on page \d+ )?undefined",
        log
    )
    if len(undefined_refs) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL ({len(undefined_refs)} undefined)")
        return False


def test_pdf_generated():
    """Test 1.4: PDF file must exist and be > 100 KB."""
    print("  [TEST 1.4] PDF generated and size... ", end="")
    if not os.path.exists(PDF_FILE):
        print("FAIL (PDF not found)")
        return False

    size_kb = os.path.getsize(PDF_FILE) / 1024
    if size_kb > 100:
        print(f"PASS ({size_kb:.0f} KB)")
        return True
    else:
        print(f"FAIL (PDF too small: {size_kb:.0f} KB)")
        return False


def test_no_rerun_warnings():
    """Test 1.5: No 'Rerun to get' warnings (cross-refs settled)."""
    print("  [TEST 1.5] Cross-ref finality... ", end="")
    if not os.path.exists(LOG_FILE):
        print("FAIL (log not found)")
        return False

    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        log = f.read()

    rerun_warnings = re.findall(
        r"LaTeX Warning: Rerun to get (cross-references|outlines)",
        log
    )
    if len(rerun_warnings) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL ({len(rerun_warnings)} rerun warnings)")
        return False


def main():
    print(f"\n{'='*60}")
    print("  TDD TEST SUITE — Compilation Gate")
    print(f"  File: {os.path.basename(TEX_FILE)}")
    print(f"{'='*60}\n")

    tests = [
        test_compilation_succeeds,
        test_no_latex_errors,
        test_no_undefined_refs,
        test_pdf_generated,
        test_no_rerun_warnings,
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
