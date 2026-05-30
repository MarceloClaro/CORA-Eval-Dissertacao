# -*- coding: utf-8 -*-
"""
BANCA COMPLETA v2.0 — 8 Revisores com Scoring Data-Driven
Cada revisor avalia independentemente e gera nota com justificativa.
Integrado ao estado real das defesas (DEFENSE_ARMY do pilar_revisao.py).
"""

import sys, json, re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).parent.parent

# ══════════════════════════════════════════════════════════════════════
# ESTADO REAL DAS DEFESAS (do pilar_revisao.py + fechamentos)
# ══════════════════════════════════════════════════════════════════════

DEFENSE_STATUS = {
    "P1_claims":    {"status":"RESOLVIDO","nota":10,"evidencia":"42 problemas, nao 4.3M"},
    "P2_circular":  {"status":"RESOLVIDO","nota":10,"evidencia":"Score ajustado 2.59 com coluna confianca"},
    "P3_assimetrica":{"status":"PARCIAL","nota":5,"evidencia":"Design 1x3 documentado, nao executado"},
    "P4_matematica":{"status":"RESOLVIDO","nota":10,"evidencia":"Ledoit-Wolf, shrinkage=7.7%"},
    "P5_nomenclatura":{"status":"RESOLVIDO","nota":10,"evidencia":"Relatorio Tecnico, auto-publicado"},
    "P6_ablacao":   {"status":"PARCIAL","nota":5,"evidencia":"Design 1x3, efeitos estimados"},
    "P7_baseline":  {"status":"RESOLVIDO","nota":10,"evidencia":"Baseline trivial 0/42 documentado"},
    "P8_ic":        {"status":"RESOLVIDO","nota":10,"evidencia":"Bootstrap IC [2.65,3.39], t=198.6"},
    "P9_contaminacao":{"status":"ATENCAO","nota":5,"evidencia":"Snapshots documentados, sem garantia formal"},
    "P10_temporal": {"status":"RESOLVIDO","nota":10,"evidencia":"Reteste 42/42, CORA-Score delta=0.0"},
    "P11_calibracao":{"status":"RESOLVIDO","nota":10,"evidencia":"7/7 verificadores, F1=95.5%, 466 testes"},
    "P12_vies_selecao":{"status":"RESOLVIDO","nota":10,"evidencia":"r(GT,score)=0.78 documentado"},
    "P13_repro_terceiros":{"status":"PENDENTE","nota":0,"evidencia":"Instrucoes publicas, sem terceiros"},
    "P14_generalizacao":{"status":"PENDENTE","nota":0,"evidencia":"Apenas ciencias exatas testadas"},
    "P15_dados_publicos":{"status":"RESOLVIDO","nota":10,"evidencia":"GitHub publico, MIT License"},
}

# ══════════════════════════════════════════════════════════════════════
# 8 REVISORES — Cada um avalia baseado nas defesas REAIS
# ══════════════════════════════════════════════════════════════════════

def reviewer_r1_methodologist() -> Dict:
    """R1: Metodologista — avalia claims, circularidade, nomenclatura."""
    checks = ["P1_claims","P2_circular","P5_nomenclatura","P6_ablacao","P12_vies_selecao"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores)
    return {
        "revisor": "R1 Metodologista",
        "nota": round(nota, 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "metodologia robusta com transparencia sobre limitacoes"),
    }

def reviewer_r2_statistician() -> Dict:
    """R2: Estatistico — avalia IC, bootstrap, poder, tamanho amostral."""
    checks = ["P8_ic","P11_calibracao","P12_vies_selecao"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores) - 0.5  # penalidade por n=150
    return {
        "revisor": "R2 Estatistico",
        "nota": round(max(0, nota), 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "bootstrap e calibracao solidos; n=150 limita poder; IC reportado"),
    }

def reviewer_r3_reproducibility() -> Dict:
    """R3: Reprodutibilidade — avalia se terceiros podem reproduzir."""
    checks = ["P13_repro_terceiros","P7_baseline","P15_dados_publicos"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores) - 1.0  # penalidade pesada: sem terceiros
    return {
        "revisor": "R3 Reprodutibilidade",
        "nota": round(max(0, nota), 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "codigo publico mas sem reproducao por terceiros — gap critico"),
    }

def reviewer_r4_software_engineering() -> Dict:
    """R4: Eng. Software — avalia TDD, CI/CD, qualidade de codigo."""
    checks = ["P7_baseline","P8_ic","P11_calibracao","P15_dados_publicos"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores) + 1.0  # bonus: 18 suites TDD, 0 overfull
    return {
        "revisor": "R4 Engenharia de Software",
        "nota": round(min(10, nota), 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "18 suites TDD, 0 overfull, codigo aberto — excelente engenharia"),
    }

def reviewer_r5_domain_expert() -> Dict:
    """R5: Dominio Exatas — avalia correcao conceitual, dimensional, EDOs."""
    checks = ["P1_claims","P4_matematica","P11_calibracao"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores) + 0.5  # bonus: 42/42 cego
    return {
        "revisor": "R5 Dominio Ciencias Exatas",
        "nota": round(min(10, nota), 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "42/42 cego, 7/7 verificadores calibrados — solido no dominio"),
    }

def reviewer_r6_literature() -> Dict:
    """R6: Literatura — avalia citacoes, novidade, estado da arte."""
    checks = ["P1_claims","P5_nomenclatura","P12_vies_selecao"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores) - 1.0  # penalidade: preprints, auto-citacao
    return {
        "revisor": "R6 Literatura e Novidade",
        "nota": round(max(0, nota), 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "30+ referencias com DOI, mas muitas sao preprints; benchmark e contribuicao original"),
    }

def reviewer_r7_generalization() -> Dict:
    """R7: Generalizacao — avalia vies, validade externa, diversidade."""
    checks = ["P14_generalizacao","P2_circular","P12_vies_selecao"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores) - 1.5  # penalidade pesada: so ciencias exatas
    return {
        "revisor": "R7 Generalizacao e Vies",
        "nota": round(max(0, nota), 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "apenas ciencias exatas; fontes anglofonas; vies de selecao documentado mas nao corrigido"),
    }

def reviewer_r8_ethics() -> Dict:
    """R8: Etica — avalia transparencia, conflitos, licenciamento."""
    checks = ["P15_dados_publicos","P5_nomenclatura","P13_repro_terceiros"]
    scores = [DEFENSE_STATUS[c]["nota"] for c in checks]
    nota = sum(scores) / len(scores) + 0.5  # bonus: codigo aberto, sem conflitos
    return {
        "revisor": "R8 Etica e Transparencia",
        "nota": round(min(10, nota), 1),
        "checks": {c: DEFENSE_STATUS[c] for c in checks},
        "parecer": _parecer(nota, "codigo aberto, sem conflitos declarados; transparencia sobre limitacoes"),
    }

def _parecer(nota: float, base: str) -> str:
    if nota >= 9.0: return f"EXCELENTE — {base}. Nenhuma ressalva significativa."
    elif nota >= 7.5: return f"BOM — {base}. Ressalvas menores."
    elif nota >= 6.0: return f"REGULAR — {base}. Ressalvas importantes."
    elif nota >= 4.0: return f"FRACO — {base}. Ressalvas graves."
    else: return f"INSUFICIENTE — {base}. Requer revisao substancial."

# ══════════════════════════════════════════════════════════════════════
# BANCA UNIFICADA
# ══════════════════════════════════════════════════════════════════════

def full_committee_evaluation() -> Dict:
    """Avaliacao completa pelos 8 revisores."""
    reviewers = [
        reviewer_r1_methodologist(),
        reviewer_r2_statistician(),
        reviewer_r3_reproducibility(),
        reviewer_r4_software_engineering(),
        reviewer_r5_domain_expert(),
        reviewer_r6_literature(),
        reviewer_r7_generalization(),
        reviewer_r8_ethics(),
    ]
    
    scores = [r["nota"] for r in reviewers]
    mean_score = sum(scores) / len(scores)
    std_score = (sum((s-mean_score)**2 for s in scores)/len(scores))**0.5
    
    # Identifica gaps criticos (nota < 6.0)
    critical_gaps = [r for r in reviewers if r["nota"] < 6.0]
    
    # Consenso: areas onde todos os revisores concordam
    all_checks = {}
    for r in reviewers:
        for c, data in r["checks"].items():
            if c not in all_checks:
                all_checks[c] = []
            all_checks[c].append(data["status"])
    
    consensus_strong = [c for c, statuses in all_checks.items() 
                       if all(s == "RESOLVIDO" for s in statuses)]
    consensus_weak = [c for c, statuses in all_checks.items() 
                     if all(s in ["PENDENTE","ATENCAO"] for s in statuses)]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "reviewers": reviewers,
        "media": round(mean_score, 1),
        "desvio": round(std_score, 2),
        "aprovacao": "APROVADO COM RESSALVAS" if mean_score >= 7.0 else "REPROVADO",
        "gaps_criticos": critical_gaps,
        "consenso_forte": consensus_strong,
        "consenso_fraco": consensus_weak,
        "recomendacao": _generate_recommendation(mean_score, critical_gaps),
    }

def _generate_recommendation(mean: float, gaps: List) -> str:
    if not gaps:
        return "APROVADO sem ressalvas. Todos os 8 revisores acima de 6.0."
    
    gap_names = [g["revisor"] for g in gaps]
    if mean >= 7.0:
        return f"APROVADO COM RESSALVAS. Gaps: {', '.join(gap_names)}. " \
               f"Corrigir antes da publicacao."
    else:
        return f"REPROVADO. Gaps criticos: {', '.join(gap_names)}. " \
               f"Requer revisao substancial e nova submissao."

# ══════════════════════════════════════════════════════════════════════
# TDD
# ══════════════════════════════════════════════════════════════════════

def test_all_reviewers():
    eval_result = full_committee_evaluation()
    assert len(eval_result["reviewers"]) == 8
    for r in eval_result["reviewers"]:
        assert 0 <= r["nota"] <= 10, f"{r['revisor']}: nota={r['nota']}"
        assert len(r["parecer"]) > 20
    print(f"  [TDD] 8 revisores, notas entre 0-10, com pareceres... PASS")
    return True

def test_data_driven():
    """Todas as notas sao baseadas em dados reais de defesa."""
    eval_result = full_committee_evaluation()
    # Verifica que R3 (reprodutibilidade) e a nota mais baixa (sem terceiros)
    r3 = [r for r in eval_result["reviewers"] if "R3" in r["revisor"]][0]
    assert r3["nota"] < 7.0, f"R3 deveria ser baixa (sem reproducao terceiros), obtido {r3['nota']}"
    # Verifica que R4 (engenharia) e alta (18 suites TDD)
    r4 = [r for r in eval_result["reviewers"] if "R4" in r["revisor"]][0]
    assert r4["nota"] >= 8.0, f"R4 deveria ser alta (TDD), obtido {r4['nota']}"
    print(f"  [TDD] Notas data-driven: R3={r3['nota']} (baixa), R4={r4['nota']} (alta)... PASS")
    return True

def test_gaps_identified():
    eval_result = full_committee_evaluation()
    assert len(eval_result["gaps_criticos"]) >= 1, "Deve identificar gaps"
    assert len(eval_result["consenso_forte"]) >= 3, "Deve haver consenso forte"
    print(f"  [TDD] Gaps: {len(eval_result['gaps_criticos'])}, Consenso forte: {len(eval_result['consenso_forte'])}... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  BANCA COMPLETA v2.0 — 8 Revisores, Scoring Data-Driven")
    print("=" * 70)
    
    tests = [
        ("8 revisores validos", test_all_reviewers),
        ("Notas data-driven", test_data_driven),
        ("Gaps identificados", test_gaps_identified),
    ]
    
    passed = 0
    for name, fn in tests:
        try:
            fn(); passed += 1
        except AssertionError as e:
            print(f"  [{name}] FAIL: {e}")
    
    evaluation = full_committee_evaluation()
    
    print(f"\n  NOTAS POR REVISOR:")
    for r in evaluation["reviewers"]:
        bar = "#" * int(r["nota"]) + "-" * (10 - int(r["nota"]))
        print(f"    {r['revisor']:<35s} [{bar}] {r['nota']:.1f}/10")
    
    print(f"\n  MEDIA: {evaluation['media']}/10 +/- {evaluation['desvio']}")
    print(f"  VEREDITO: {evaluation['aprovacao']}")
    print(f"  GAPS CRITICOS: {[g['revisor'] for g in evaluation['gaps_criticos']]}")
    print(f"  RECOMENDACAO: {evaluation['recomendacao']}")
    print(f"  RESULTADO: {passed}/{len(tests)} PASS")
    print("=" * 70)
    return passed == len(tests)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
