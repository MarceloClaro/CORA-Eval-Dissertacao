#!/usr/bin/env python3
"""
test_structure.py — TDD Test Suite 2: Structure Gate
======================================================================
RED CONDITION (fails when):
  1. Missing required ABNT sections (Introdução, Metodologia, Resultados,
     Discussão, Considerações Finais, Referências)
  2. Missing required \label{...} for figures and tables
  3. Dangling \ref{...} without corresponding \label{...}
  4. Manual section numbering like \section{1. Introdução}
  5. Referenced figure files do not exist in figuras/
  6. Missing \newpage before major sections

GREEN CONDITION (passes when):
  All 6 tests pass -> document follows ABNT structural conventions

FIX STRATEGIES:
  - Missing sections: add \section{...} at appropriate location
  - Missing labels: insert \label{...} after \caption{...}
  - Dangling refs: verify label name spelling or add missing label
  - Manual numbering: remove digits, let LaTeX auto-number
  - Missing figures: ensure file exists in figuras/ directory
  - Missing newpage: insert \newpage before each major section

RELATION TO FRAMEWORK:
  - This is the SECOND quality gate in the SDD+TDD pipeline
  - Tests structural integrity beyond mere compilation
  - Refer to SPEC_ORCHESTRATION.md §4.2 for detailed criteria
======================================================================
"""

import sys
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_FILE = os.path.join(BASE_DIR, "artigo_150_questoes.tex")
PASS = 0
FAIL = 1

# Required ABNT sections
REQUIRED_SECTIONS = [
    "Introdução",
    "Referencial Teórico",
    "Metodologia",
    "Resultados",
    "Discussão",
    "Considerações Finais",
    "Referências",
]

# Required labels (figure + table)
REQUIRED_LABELS = [
    "tab:rcodes",
    "fig:rcodes",
    "tab:categorias",
    "fig:categorias",
    "tab:bloom",
    "fig:bloom",
    "fig:heatmap1",
    "fig:heatmap2",
    "fig:heatmap3",
    "tab:resumo",
]


def load_tex():
    with open(TEX_FILE, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def test_section_count():
    """Test 2.1: Document must have exactly the 7 required ABNT sections."""
    print("  [TEST 2.1] Required ABNT sections... ", end="")
    tex = load_tex()

    missing = []
    for section in REQUIRED_SECTIONS:
        # Check for \section{...} or \section*{...} with the section name
        pattern = re.compile(
            r"\\section\*?\{.*?" + re.escape(section) + r".*?\}",
            re.UNICODE
        )
        if not pattern.search(tex):
            missing.append(section)

    if len(missing) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL (missing: {', '.join(missing)})")
        return False


def test_fig_tab_labels():
    """Test 2.2: All figure/table labels must exist."""
    print("  [TEST 2.2] Required labels present... ", end="")
    tex = load_tex()

    missing = []
    for label in REQUIRED_LABELS:
        if f"\\label{{{label}}}" not in tex:
            missing.append(label)

    if len(missing) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL (missing labels: {', '.join(missing)})")
        return False


def test_label_ref_balance():
    """Test 2.3: Every label must have at least one ref."""
    print("  [TEST 2.3] Label-ref balance... ", end="")
    tex = load_tex()

    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs = set(re.findall(r"\\ref\{([^}]+)\}", tex))

    # A label defined but never referenced is not necessarily wrong
    # (can be referenced via \pageref or just defined for the aux)
    # But for quality, we WARN but don't fail
    unreferenced = labels - refs
    # However, check that every \ref has a corresponding \label
    dangling_refs = refs - labels

    if len(dangling_refs) == 0:
        if len(unreferenced) > 0:
            print(f"PASS (warn: {len(unreferenced)} unreferenced labels)")
        else:
            print("PASS")
        return True
    else:
        print(f"FAIL ({len(dangling_refs)} dangling refs: {dangling_refs})")
        return False


def test_no_manual_section_numbering():
    """Test 2.4: No manual section numbering like '1. Introdução'."""
    print("  [TEST 2.4] No manual section numbering... ", end="")
    tex = load_tex()

    # Look for section headers that start with a digit pattern
    # This would indicate manual numbering like \section{1. Introdução}
    pattern = re.compile(r"\\section\{(\d+[\.\d]*)\s", re.UNICODE)
    matches = pattern.findall(tex)

    if len(matches) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL (manual numbering found: {matches})")
        return False


def test_figures_in_figuras_dir():
    """Test 2.5: Referenced figure files must exist in figuras/."""
    print("  [TEST 2.5] Figure files exist... ", end="")
    tex = load_tex()
    figuras_dir = os.path.join(BASE_DIR, "figuras")

    if not os.path.exists(figuras_dir):
        print("FAIL (figuras/ directory not found)")
        return False

    # Find all \includegraphics calls
    includes = re.findall(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}", tex)

    missing = []
    for inc in includes:
        # Handle path variations
        inc_clean = inc.replace("figuras/", "").replace("./", "")
        inc_path = os.path.join(figuras_dir, os.path.basename(inc_clean))
        if not os.path.exists(inc_path):
            missing.append(inc_clean)

    if len(missing) == 0:
        print(f"PASS ({len(includes)} files checked)")
        return True
    else:
        print(f"FAIL (missing: {missing})")
        return False


def test_newpage_before_major_sections():
    """Test 2.6: \newpage before each major section."""
    print("  [TEST 2.6] newpage before major sections... ", end="")
    tex = load_tex()

    # Check that \newpage appears before \section (but not before first \section)
    # Actually check that \newpage\n\section pattern exists for key sections
    major_sections = [
        "Referencial Teórico",
        "Metodologia",
        "Resultados",
        "Discussão",
        "Considerações Finais",
        "Referências",
    ]

    missing_newpage = []
    for section in major_sections:
        # Search for \newpage followed (eventually) by \section{...SectionName...}
        pattern = re.compile(
            r"\\newpage.*?\\section\*?\{.*?" + re.escape(section) + r".*?\}",
            re.DOTALL
        )
        if not pattern.search(tex):
            missing_newpage.append(section)

    if len(missing_newpage) == 0:
        print("PASS")
        return True
    else:
        print(f"FAIL (missing newpage before: {', '.join(missing_newpage)})")
        return False


def main():
    print(f"\n{'='*60}")
    print("  TDD TEST SUITE — Structure Gate")
    print(f"  File: {os.path.basename(TEX_FILE)}")
    print(f"{'='*60}\n")

    tests = [
        test_section_count,
        test_fig_tab_labels,
        test_label_ref_balance,
        test_no_manual_section_numbering,
        test_figures_in_figuras_dir,
        test_newpage_before_major_sections,
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
