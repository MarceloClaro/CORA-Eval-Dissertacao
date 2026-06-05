#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORA-Benchmark Tracker — Rastreador Evolutivo para Ciências Exatas e da Natureza.

Acompanha a evolução do OpenCode Ecosystem no benchmark CORA-Eval,
calculando CORA-Score e CORA-V-Score com persistência JSON.

Uso:
    python cora_benchmark_tracker.py --init          # Inicializa scores.json
    python cora_benchmark_tracker.py --score D1 N3 5 5  # Registra N tarefas aprovadas
    python cora_benchmark_tracker.py --report         # Relatório completo
    python cora_benchmark_tracker.py --evolve         # Registra snapshot evolutivo
    python cora_benchmark_tracker.py --list           # Lista todas as tarefas pendentes
    python cora_benchmark_tracker.py --detail D3      # Detalha uma dimensão
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import OrderedDict

# Força UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─── Constantes ────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
SCORES_FILE = SCRIPT_DIR / "cora_scores.json"

WEIGHTS = {
    "D1": 0.14,  # Matemática
    "D2": 0.11,  # Física
    "D3": 0.11,  # Estatística
    "D4": 0.09,  # Química
    "D5": 0.09,  # Biologia
    "D6": 0.08,  # Geociências
    "D7": 0.09,  # Código Científico
    "D8": 0.08,  # Literatura
    "D9": 0.07,  # Metodologia
    "D10": 0.07, # Interdisciplinar
    "D11": 0.07, # Long-Horizon Reasoning (DAG)
}

DIMENSION_NAMES = {
    "D1": "Raciocínio Matemático Formal",
    "D2": "Modelagem de Sistemas Físicos",
    "D3": "Análise Estatística e Inferência",
    "D4": "Química Computacional e Estrutural",
    "D5": "Biologia Molecular e Genômica",
    "D6": "Geociências e Modelagem Climática",
    "D7": "Verificação de Código Científico",
    "D8": "Revisão Sistemática de Literatura",
    "D9": "Desenho Experimental e Metodologia",
    "D10": "Síntese Interdisciplinar",
    "D11": "Raciocínio Long-Horizon (DAG)",
}

LEVELS = {
    "N1": {"name": "Básico", "offset": 0.0, "factor": 0.9, "range": (0.1, 0.9)},
    "N2": {"name": "Graduação", "offset": 1.0, "factor": 0.9, "range": (1.0, 1.9)},
    "N3": {"name": "Pós-Graduação", "offset": 2.0, "factor": 0.9, "range": (2.0, 2.9)},
    "N4": {"name": "Pesquisa", "offset": 3.0, "factor": 1.0, "range": (3.0, 4.0)},
}

VERIFIERS = ["V1", "V2", "V3", "V4", "V5", "V6", "V7"]

# Total de tarefas por dimensão e nível (do benchmark)
TASK_TOTALS = {
    "D1": {"N1": 4, "N2": 5, "N3": 5, "N4": 5},
    "D2": {"N1": 3, "N2": 4, "N3": 4, "N4": 4},
    "D3": {"N1": 3, "N2": 5, "N3": 5, "N4": 5},
    "D4": {"N1": 3, "N2": 4, "N3": 4, "N4": 3},
    "D5": {"N1": 3, "N2": 4, "N3": 4, "N4": 3},
    "D6": {"N1": 3, "N2": 3, "N3": 3, "N4": 3},
    "D7": {"N1": 3, "N2": 4, "N3": 5, "N4": 5},
    "D8": {"N1": 3, "N2": 4, "N3": 4, "N4": 4},
    "D9": {"N1": 3, "N2": 4, "N3": 4, "N4": 4},
    "D10": {"N1": 2, "N2": 3, "N3": 3, "N4": 3},
    "D11": {"N1": 5, "N2": 7, "N3": 8, "N4": 10},
}


# ─── Funções de Cálculo ────────────────────────────────────────────

def calc_dimension_score(dim: str, level: str, passed: int, verifiers_active: Optional[List[str]] = None) -> Tuple[float, float]:
    """Calcula score bruto e score com verificadores para uma dimensão."""
    total = TASK_TOTALS.get(dim, {}).get(level, 0)
    if total == 0:
        return 0.0, 0.0

    lvl = LEVELS[level]
    ratio = passed / total
    raw_score = ratio * lvl["factor"] + lvl["offset"]

    if verifiers_active:
        v_ratio = len(set(verifiers_active) & set(VERIFIERS)) / len(VERIFIERS)
        v_score = raw_score * (0.7 + 0.3 * v_ratio)
    else:
        v_score = raw_score

    return round(raw_score, 2), round(v_score, 2)


def calc_cora_score(scores: Dict) -> float:
    """Calcula CORA-Score global ponderado."""
    total = 0.0
    for dim in WEIGHTS:
        dim_data = scores.get("dimensions", {}).get(dim, {})
        best = dim_data.get("score", 0.0)
        total += WEIGHTS[dim] * best
    return round(total, 2)


def classify(score: float) -> str:
    """Classifica o CORA-Score."""
    if score <= 0.9:
        return "Básico"
    elif score <= 1.9:
        return "Graduação"
    elif score <= 2.9:
        return "Pós-Graduação"
    else:
        return "Pesquisa"


# ─── Persistência ───────────────────────────────────────────────────

def load_scores() -> Dict:
    """Carrega scores.json ou retorna estrutura padrão."""
    if SCORES_FILE.exists():
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "ecosystem": "OpenCode",
        "benchmark_version": "1.0.0",
        "last_evaluation": None,
        "cora_score": 0.0,
        "cora_v_score": 0.0,
        "classification": "Não avaliado",
        "dimensions": {dim: {
            "score": 0.0,
            "v_score": 0.0,
            "level": None,
            "tasks_passed": 0,
            "total_tasks": 0,
            "verifiers_active": [],
        } for dim in WEIGHTS},
        "evolution": [],
        "verifier_coverage": {v: {"dimensions": [], "approval_rate": 0.0} for v in VERIFIERS},
    }


def save_scores(data: Dict):
    """Salva scores.json."""
    data["last_evaluation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["cora_score"] = calc_cora_score(data)
    data["classification"] = classify(data["cora_score"])

    # Calcula CORA-V-Score
    v_total = 0.0
    for dim in WEIGHTS:
        v_total += WEIGHTS[dim] * data["dimensions"][dim].get("v_score", 0.0)
    data["cora_v_score"] = round(v_total, 2)

    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─── Comandos ───────────────────────────────────────────────────────

def cmd_init(force: bool = False):
    """Inicializa scores.json."""
    if SCORES_FILE.exists():
        print(f"⚠ scores.json já existe em {SCORES_FILE}")
        if not force:
            try:
                resp = input("Sobrescrever? (s/N): ").strip().lower()
            except EOFError:
                print("  (modo não-interativo: use --init --force para sobrescrever)")
                return
            if resp != "s":
                return

    data = load_scores()
    save_scores(data)
    print(f"✓ scores.json criado em {SCORES_FILE}")
    print(f"  Benchmark: CORA-Eval v{data['benchmark_version']}")
    print(f"  10 dimensões × 4 níveis = 150 tarefas")


def cmd_score(dim: str, level: str, passed: int, total: Optional[int] = None,
              verifiers: Optional[str] = None):
    """Registra score para uma dimensão e nível."""
    data = load_scores()

    if dim not in WEIGHTS:
        print(f"✗ Dimensão inválida: {dim}. Use D1-D10.")
        return

    if level not in LEVELS:
        print(f"✗ Nível inválido: {level}. Use N1-N4.")
        return

    max_tasks = TASK_TOTALS[dim][level]
    if total is None:
        total = max_tasks
    if passed > total:
        print(f"✗ passed ({passed}) > total ({total}). Corrigido para total={total}.")
        passed = total

    v_list = []
    if verifiers:
        v_list = [v.strip().upper() for v in verifiers.split(",") if v.strip().upper() in VERIFIERS]

    raw_score, v_score = calc_dimension_score(dim, level, passed, v_list)

    # Atualiza dimensão (mantém melhor score entre níveis)
    current_best = data["dimensions"][dim]["score"]
    if raw_score > current_best:
        data["dimensions"][dim] = {
            "score": raw_score,
            "v_score": v_score,
            "level": level,
            "tasks_passed": passed,
            "total_tasks": total,
            "verifiers_active": v_list,
        }

    save_scores(data)

    level_name = LEVELS[level]["name"]
    print(f"✓ {dim} ({DIMENSION_NAMES[dim]})")
    print(f"  Nível: {level} ({level_name})")
    print(f"  Tarefas: {passed}/{total}")
    print(f"  Score bruto: {raw_score}")
    if v_list:
        print(f"  V-Score: {v_score} (verificadores: {', '.join(v_list)})")
    print(f"  CORA-Score global: {data['cora_score']} → {data['classification']}")


def cmd_report():
    """Gera relatório completo."""
    data = load_scores()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║   CORA-Eval: Relatório de Maturidade Científica          ║")
    print("║   OpenCode Ecosystem — Ciências Exatas e da Natureza     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"  CORA-Score: {data['cora_score']} ({data['classification']})")
    print(f"  CORA-V-Score: {data.get('cora_v_score', 'N/A')}")
    print(f"  Última avaliação: {data.get('last_evaluation', 'Nunca')}")
    print()

    # Tabela de dimensões
    print("  ┌──────────┬────────────────────────────────┬─────────┬──────────┬────────┬──────────┐")
    print("  │ Dim.     │ Descrição                       │ Nível   │ Tarefas  │ Score  │ V-Score  │")
    print("  ├──────────┼────────────────────────────────┼─────────┼──────────┼────────┼──────────┤")

    for dim in WEIGHTS:
        d = data["dimensions"][dim]
        name = DIMENSION_NAMES[dim]
        level = d.get("level") or "-"
        if level in LEVELS:
            level = f"{level} ({LEVELS[level]['name']})"
        tasks = f"{d.get('tasks_passed', 0)}/{d.get('total_tasks', 0)}"
        score = f"{d.get('score', 0):.2f}"
        vscore = f"{d.get('v_score', 0):.2f}"
        print(f"  │ {dim:8s} │ {name:30s} │ {level:7s} │ {tasks:8s} │ {score:6s} │ {vscore:8s} │")

    print("  └──────────┴────────────────────────────────┴─────────┴──────────┴────────┴──────────┘")
    print()

    # Barra de progresso
    max_score = sum(LEVELS["N4"]["offset"] * w for w in WEIGHTS.values()) + sum(
        LEVELS["N4"]["factor"] * w for w in WEIGHTS.values())
    bar_len = 40
    filled = int(data["cora_score"] / max_score * bar_len) if max_score > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"  Progresso: [{bar}] {data['cora_score']:.2f}/{max_score:.2f}")
    print()

    # Próximo nível alvo
    next_milestone = None
    for ms, ms_data in [
        ("M1 - Fundação (0.9)", 0.9),
        ("M2 - Graduação (1.9)", 1.9),
        ("M3 - Especialização (2.5)", 2.5),
        ("M4 - Pesquisa (3.0)", 3.0),
        ("M5 - Fronteira (4.0)", 4.0),
    ]:
        if data["cora_score"] < ms_data:
            next_milestone = (ms, ms_data)
            break

    if next_milestone:
        diff = next_milestone[1] - data["cora_score"]
        print(f"  Próximo marco: {next_milestone[0]} (faltam {diff:.2f})")

    # Evolução
    evo = data.get("evolution", [])
    if evo:
        print(f"\n  Histórico evolutivo ({len(evo)} snapshots):")
        for e in evo[-10:]:
            print(f"    {e['date']}: CORA-Score {e['cora_score']:.2f} ({e['classification']})")

    # Dimensões pendentes
    pending = [dim for dim in WEIGHTS if data["dimensions"][dim].get("level") is None]
    if pending:
        print(f"\n  Dimensões não avaliadas: {', '.join(pending)}")


def cmd_evolve():
    """Registra snapshot evolutivo no histórico."""
    data = load_scores()

    if data["cora_score"] == 0.0:
        print("⚠ Nenhuma pontuação registrada. Use --score primeiro.")
        return

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "cora_score": data["cora_score"],
        "cora_v_score": data.get("cora_v_score", 0.0),
        "classification": data["classification"],
        "dimensions_scored": sum(1 for d in WEIGHTS if data["dimensions"][d]["level"] is not None),
    }

    data["evolution"].append(snapshot)
    save_scores(data)
    print(f"✓ Snapshot evolutivo registrado:")
    print(f"  Data: {snapshot['date']}")
    print(f"  CORA-Score: {snapshot['cora_score']:.2f} ({snapshot['classification']})")
    print(f"  Dimensões avaliadas: {snapshot['dimensions_scored']}/10")


def cmd_list():
    """Lista todas as tarefas pendentes por dimensão e nível."""
    data = load_scores()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Tarefas Pendentes — CORA-Eval                           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    total_pending = 0
    for dim in WEIGHTS:
        dim_data = data["dimensions"][dim]
        current_level = dim_data.get("level")

        for level in ["N1", "N2", "N3", "N4"]:
            if current_level and LEVELS[level]["offset"] <= LEVELS[current_level]["offset"]:
                continue  # Já superou este nível

            max_tasks = TASK_TOTALS[dim][level]
            pending_tasks = max_tasks  # Todas pendentes se não avaliado neste nível
            total_pending += pending_tasks

            level_name = LEVELS[level]["name"]
            print(f"  {dim} {level} ({level_name}): {pending_tasks} tarefas — {DIMENSION_NAMES[dim]}")

    print(f"\n  Total pendente: ~{total_pending} tarefas")


def cmd_detail(dim: str):
    """Detalha uma dimensão específica."""
    data = load_scores()

    if dim not in WEIGHTS:
        print(f"✗ Dimensão inválida: {dim}. Use D1-D10.")
        return

    d = data["dimensions"][dim]
    print(f"  {dim} — {DIMENSION_NAMES[dim]}")
    print(f"  Peso: {WEIGHTS[dim]*100:.0f}%")
    print(f"  Score atual: {d.get('score', 0):.2f}")
    print(f"  V-Score: {d.get('v_score', 0):.2f}")
    print(f"  Nível: {d.get('level') or 'Não avaliado'}")
    print(f"  Tarefas aprovadas: {d.get('tasks_passed', 0)}/{d.get('total_tasks', 0)}")
    print(f"  Verificadores ativos: {', '.join(d.get('verifiers_active', [])) or 'Nenhum'}")
    print()

    # Mostra todos os níveis
    for level in ["N1", "N2", "N3", "N4"]:
        max_tasks = TASK_TOTALS[dim][level]
        level_name = LEVELS[level]["name"]
        level_range = LEVELS[level]["range"]
        print(f"    {level} ({level_name}): {max_tasks} tarefas | Alcance: {level_range[0]}-{level_range[1]}")


# ─── CLI ────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "--init":
        force = "--force" in args
        cmd_init(force=force)

    elif cmd == "--score":
        if len(args) < 4:
            print("Uso: --score <D1-D10> <N1-N4> <passed> [total] [--verifiers V1,V2]")
            return
        dim = args[1].upper()
        level = args[2].upper()
        passed = int(args[3])
        total = int(args[4]) if len(args) > 4 and args[4].isdigit() else None
        verifiers = None
        if "--verifiers" in args:
            idx = args.index("--verifiers")
            if idx + 1 < len(args):
                verifiers = args[idx + 1]
        cmd_score(dim, level, passed, total, verifiers)

    elif cmd == "--report":
        cmd_report()

    elif cmd == "--evolve":
        cmd_evolve()

    elif cmd == "--list":
        cmd_list()

    elif cmd == "--detail":
        if len(args) < 2:
            print("Uso: --detail <D1-D10>")
            return
        cmd_detail(args[1].upper())

    else:
        print(f"Comando desconhecido: {cmd}")
        print("Use --help para lista de comandos.")


if __name__ == "__main__":
    main()
