#!/usr/bin/env python3
"""
run_all_tests.py — TDD Test Runner v1.0
AutoEvolve: SENSE → DISCOVER → INSTALL → VERIFY → EVOLVE → LEARN

Executes all TDD test suites and produces a structured report.
"""

import sys
import os
import json
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "tests", "reports")

# Test suites: (module_name, description)
TEST_SUITES = [
    ("test_compile", "Compilation Gate — pdflatex must compile with zero errors"),
    ("test_structure", "Structure Gate — ABNT sections, labels, figure files"),
    ("test_quality", "Quality Gate — overfull/underfull within tolerance"),
]


def run_test_suite(module_name):
    """Run a single test suite and return its output and exit code."""
    result = subprocess.run(
        [sys.executable, f"{module_name}.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True,
        timeout=120
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def compile_document():
    """Run pdflatex twice for cross-refs."""
    tex_file = os.path.join(BASE_DIR, "artigo_150_questoes.tex")
    result = None
    for _ in range(2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_file],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
    return result.returncode if result else -1


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*70}")
    print(f"  AutoEvolve: TDD Test Runner")
    print(f"  Document: artigo_150_questoes.tex")
    print(f"  Timestamp: {timestamp}")
    print(f"{'='*70}\n")

    # Phase 1: Compile
    print("-> Phase 1: Compiling document (2 passes)...")
    compile_document()
    print("  Done.\n")

    # Phase 2: Run test suites
    results = {}
    all_passed = True

    for module_name, description in TEST_SUITES:
        print(f"-> Phase 2: {description}")
        suite_result = run_test_suite(module_name)
        results[module_name] = suite_result

        if suite_result["exit_code"] == 0:
            print(f"  V SUITE PASSED\n")
        else:
            all_passed = False
            print(f"  X SUITE FAILED (exit code {suite_result['exit_code']})\n")

        # Print stdout (test details)
        for line in suite_result["stdout"].split("\n"):
            if line.strip():
                print(f"    {line}")

        if suite_result["stderr"].strip():
            print(f"  stderr: {suite_result['stderr'][:500]}")
        print()

    # Phase 3: Generate report
    report = {
        "timestamp": timestamp,
        "document": "artigo_150_questoes.tex",
        "all_passed": all_passed,
        "suites": {},
    }

    for module_name, _ in TEST_SUITES:
        report["suites"][module_name] = {
            "passed": results[module_name]["exit_code"] == 0,
        }

    report_path = os.path.join(REPORT_DIR, f"report_{timestamp}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"{'='*70}")
    if all_passed:
        print(f"  V ALL TEST SUITES PASSED")
    else:
        print(f"  X SOME TEST SUITES FAILED - check reports above")
    print(f"  Report: {report_path}")
    print(f"{'='*70}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
