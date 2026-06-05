# -*- coding: utf-8 -*-
"""
CORA-Eval TDD Benchmark Runner — 10 Dimensoes
Executa todas as suites de teste TDD e gera relatorio JSON.
Suites com main(): D3, D4, D5, D6, D8, D10
Suites pytest:     D1, D2, D7, D9
"""
import sys, os, json, subprocess
from datetime import datetime

# Forca UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))
from test_d3_estatistica import main as run_d3
from test_d4_quimica import main as run_d4
from test_d5_biologia import main as run_d5
from test_d6_geociencias import main as run_d6
from test_d8_literatura import main as run_d8
from test_d10_gat import main as run_d10


def run_pytest(name, test_file):
    """Executa suite pytest e retorna (ok, output)"""
    print(f"> {name}")
    print("-" * 60)
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v"],
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace"
        )
        # Mostra linhas relevantes do output
        for line in result.stdout.split("\n"):
            if any(kw in line for kw in ["PASSED", "FAILED", "ERROR", "passed", "failed", "error", "=="]):
                print(f"  {line.strip()}")
        ok = result.returncode == 0
        return ok
    except subprocess.TimeoutExpired:
        print("  [TIMEOUT] Excedeu 300s")
        return False


def run_all():
    # Suites com funcao main() — execucao direta
    direct_suites = {
        "D3 - Estatistica (N2+N3)": run_d3,
        "D4 - Quimica (N1)":        run_d4,
        "D5 - Biologia (N1)":       run_d5,
        "D6 - Geociencias (N1)":    run_d6,
        "D8 - Literatura (N1)":     run_d8,
        "D10 - Interdisciplinar(N4)": run_d10,
    }
    # Suites pytest
    pytest_suites = {
        "D1 - Matematica (N4)":      "test_d1_matematica.py",
        "D2 - Fisica (N4)":          "test_d2_fisica.py",
        "D7 - Codigo (N3, pytest)":  "test_d7_codigo.py",
        "D9 - Metodologia (N4)":     "test_d9_metodologia.py",
    }

    print("\n" + "=" * 70)
    print("  CORA-Eval v2.0: TDD Benchmark Runner — 10 Dimensoes")
    print("=" * 70 + "\n")

    results = {}
    all_ok = 0
    total = len(direct_suites) + len(pytest_suites)

    # Fase 1: Suites com main()
    for name, runner in direct_suites.items():
        print(f"> {name}")
        print("-" * 70)
        try:
            ok = runner()
        except Exception as e:
            print(f"  [EXCEPTION] {e}")
            ok = False
        results[name] = "PASS" if ok else "FAIL"
        if ok: all_ok += 1
        print()

    # Fase 2: Suites pytest
    for name, test_file in pytest_suites.items():
        ok = run_pytest(name, test_file)
        results[name] = "PASS" if ok else "FAIL"
        if ok: all_ok += 1
        print()

    # Relatorio final
    print("=" * 70)
    print("  RESUMO FINAL")
    print("=" * 70)
    for name, status in results.items():
        print(f"  [{status}] {name}")
    print("-" * 70)
    print(f"  TOTAL: {all_ok}/{total} suites passing")
    print("=" * 70)

    # Salva relatorio JSON
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(report_dir, f"report_{ts}.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "benchmark": "CORA-Eval v2.0",
            "timestamp": ts,
            "suites": results,
            "total_suites": total,
            "passing": all_ok,
            "all_green": all_ok == total,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  Relatorio salvo em: {report_file}")
    return all_ok == total


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
