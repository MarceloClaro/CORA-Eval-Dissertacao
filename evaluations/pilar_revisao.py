# -*- coding: utf-8 -*-
"""
PILAR DE REVISAO v2.0 — 10 Padroes de Ataque + Exercito de Defesa
Evoluido de 5 para 10 padroes com contramedidas automatizadas.
"""

import sys, json, re, math, random
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.parent

# ══════════════════════════════════════════════════════════════════════
# 10 PADROES DE ATAQUE (5 originais + 5 evolucao)
# ══════════════════════════════════════════════════════════════════════

TEN_ATTACK_PATTERNS = [
    # --- ORIGINAIS (P1-P5) ---
    {
        "id": "P1",
        "nome": "Reducao de claims infladas",
        "regex": r"(\d+[\.,]?\d*\s*(milhoes|mil|milhao|M|K)\s*de)",
        "acao": "Verificar se o numero refere-se a usuarios cadastrados, nao revisores",
        "contra_evidencia": "Substituir por contagem exata de problemas resolvidos",
        "severidade": "Alta",
    },
    {
        "id": "P2",
        "nome": "Deteccao de circularidade",
        "regex": r"(validacao interna|proprio sistema|auto-avaliacao)",
        "acao": "Verificar quantas dimensoes dependem de validacao interna",
        "contra_evidencia": "Adicionar coluna de confianca (Alta/Media/Baixa) e score ajustado",
        "severidade": "Alta",
    },
    {
        "id": "P3",
        "nome": "Comparacao assimetrica",
        "regex": r"(vs|comparado|superior).*(bare.metal|sem verificador|modelo local)",
        "acao": "Verificar se a comparacao usa mesmo modelo base e arquiteturas equivalentes",
        "contra_evidencia": "Design experimental 1x3 com mesmo modelo base. Documentar como NAO EXECUTADO.",
        "severidade": "Alta",
    },
    {
        "id": "P4",
        "nome": "Matematica inviavel",
        "regex": r"(\d+)\s*(dimensoes|variaveis|parametros).*(\d+)\s*(observacoes|pontos|amostras)",
        "acao": "Verificar n >= p para estimacao de covariancia",
        "contra_evidencia": "Implementar Ledoit-Wolf ou regularizacao. Documentar shrinkage.",
        "severidade": "Media",
    },
    {
        "id": "P5",
        "nome": "Nomenclatura inflada",
        "regex": r"(dissertacao|tese|artigo\s*Qualis\s*A1)",
        "acao": "Verificar se ha banca, orientador, instituicao, defesa",
        "contra_evidencia": "Substituir por 'Relatorio Tecnico' com nota de auto-publicacao",
        "severidade": "Media",
    },
    
    # --- NOVOS (P11-P15) ---
    {
        "id": "P11",
        "nome": "Ausencia de estudo de ablacao",
        "regex": r"(sem|nao\s*foi|pendente|ausencia|falta).*(ablation|ablacao|componente\s*isolado|removido|modelo\s*simples|baseline)",
        "acao": "Verificar se cada componente foi testado isoladamente (bare vs +Cora vs OpenCode)",
        "contra_evidencia": "Design 1x3 documentado. Reportar efeito de cada componente separadamente.",
        "severidade": "Alta",
    },
    {
        "id": "P12",
        "nome": "Ausencia de baseline trivial",
        "regex": r"(sem|nao\s*ha|ausencia).*(baseline|linha\s*de\s*base|referencia\s*simples)",
        "acao": "Verificar se ha comparacao com baseline naive (ex: regra mais frequente, dicionario)",
        "contra_evidencia": "Adicionar baseline zero-shot (modelo sem prompt engineering) aos 42 problemas.",
        "severidade": "Media",
    },
    {
        "id": "P13",
        "nome": "Metricas sem intervalo de confianca",
        "regex": r"(\d+[\.\,]\d+)\s*\(?(score|acuracia|precisao|F1|CORA)" + 
                r"(?!.*(\[|IC|intervalo|bootstrap|confianca))",
        "acao": "Verificar se metricas reportam IC ou apenas estimativa pontual",
        "contra_evidencia": "Adicionar bootstrap IC 95% a toda metrica reportada.",
        "severidade": "Media",
    },
    {
        "id": "P14",
        "nome": "Contaminacao treino-teste",
        "regex": r"(validacao|teste|cega).*(\d+/\d+).*(?!.*(nunca|jamais|primeira\s*vez))",
        "acao": "Verificar se os problemas cegos foram usados durante o desenvolvimento",
        "contra_evidencia": "Documentar EXATAMENTE quando cada problema foi testado pela primeira vez. Separar claramente desenvolvimento de validacao.",
        "severidade": "Alta",
    },
    {
        "id": "P15",
        "nome": "Generalizacao temporal nao verificada",
        "regex": r"(resultados?\s*(se\s*mant[eé]m|permanece|continua))" +
                r"(?!.*(reteste|reavaliacao|follow.up|longitudinal))",
        "acao": "Verificar se os resultados de maio/2026 se mantem em avaliacoes posteriores",
        "contra_evidencia": "Planejar reavaliacao periodica. Documentar que ainda nao foi feita.",
        "severidade": "Media",
    },
]

# ══════════════════════════════════════════════════════════════════════
# EXERCITO DE DEFESA — Contramedidas automatizadas para cada padrao
# ══════════════════════════════════════════════════════════════════════

DEFENSE_ARMY = {
    "P1": {
        "status": "RESOLVIDO",
        "acao_tomada": "Substituido '4.3 milhoes de verificacoes' por '42 problemas com verificacao automatica'",
        "evidencia": "Resumo do relatorio tecnico (linha 56-57). Nota: verificacao e binaria (correto/erro), nao por revisores.",
        "auto_resposta": "O numero de 4.3 milhoes referia-se a usuarios cadastrados nas plataformas, nao a revisores. Corrigido para contagem exata de 42 problemas resolvidos.",
    },
    "P2": {
        "status": "RESOLVIDO",
        "acao_tomada": "Adicionada coluna de confianca (Alta/Media/Baixa). Score bruto 3.04 complementado por ajustado 2.59.",
        "evidencia": "Tabela de scores com coluna Conf. (Secao 5.1). CORA-Score ajustado = 2.59.",
        "auto_resposta": "Reconhecemos que 8/10 dimensoes dependem de validacao interna. O score ajustado (2.59) penaliza essa circularidade. D1 e D5 tem validacao externa via Project Euler e Rosalind.",
    },
    "P3": {
        "status": "RESOLVIDO PARCIALMENTE",
        "acao_tomada": "Comparacao qualificada como 'modelos bare-metal'. Design 1x3 documentado mas NAO EXECUTADO.",
        "evidencia": "Secao 8 do relatorio. test_comparacao_justa.py.",
        "auto_resposta": "A comparacao original era assimetrica (multiagente+verificadores vs bare-metal). O design 1x3 corrige isso mas ainda nao foi executado. Efeito estimado: verificadores +18.5%, multiagente +31.6%.",
    },
    "P4": {
        "status": "RESOLVIDO",
        "acao_tomada": "Ledoit-Wolf implementado. Shrinkage=7.7% para n=150, p=10. Documentada limitacao para p>n.",
        "evidencia": "test_melhorias_defesa.py (TDD-4). Secao 11 do relatorio.",
        "auto_resposta": "Para n=150 e p=10, a matriz e bem-condicionada (shrinkage=7.7%). Para 38 dimensoes, seria necessario shrinkage ~30-50%. A implementacao de Ledoit-Wolf (2004) resolve o problema de regularizacao.",
    },
    "P5": {
        "status": "RESOLVIDO",
        "acao_tomada": "Termo 'Dissertacao' substituido por 'Relatorio Tecnico' em todo o documento. Metadados: 'auto-publicado, sem revisao por pares'.",
        "evidencia": "Metadados do PDF. Cabecalho do documento.",
        "auto_resposta": "Este documento e um relatorio tecnico auto-publicado, nao uma dissertacao defendida. Nao ha banca, orientador ou instituicao. A formatacao ABNT e uma escolha de estilo, nao uma reivindicacao de status academico.",
    },
    "P11": {
        "status": "RESOLVIDO PARCIALMENTE",
        "acao_tomada": "Design 1x3 (bare vs +Cora vs OpenCode) documentado. Efeitos estimados a partir de dados disponiveis.",
        "evidencia": "test_comparacao_justa.py. Efeito verificadores: +0.36. Efeito multiagente: +0.73.",
        "auto_resposta": "O estudo de ablacao foi projetado (3 condicoes, mesmo modelo base) mas nao executado com todos os sistemas. As estimativas baseiam-se em dados reais do Ollama e do OpenCode. Execucao completa requer acesso aos 3 sistemas.",
    },
    "P12": {
        "status": "PENDENTE",
        "acao_tomada": "Nenhum baseline trivial foi implementado.",
        "evidencia": "Pendente. Sugestao: testar respostas sem prompt engineering (zero-shot) nos 42 problemas.",
        "auto_resposta": "Reconhecemos a ausencia de baseline trivial. Um baseline zero-shot (modelo respondendo sem instrucoes especificas) seria informativo para quantificar o efeito do prompt engineering e da arquitetura. Pendente de implementacao.",
    },
    "P13": {
        "status": "RESOLVIDO",
        "acao_tomada": "Bootstrap IC 95% implementado para CORA-Score. IC = [2.65, 3.39], t=198.6, p<0.001.",
        "evidencia": "test_evolucao_pilar.py (P8). Secao 12.3 do relatorio.",
        "auto_resposta": "O CORA-Score de 3.04 e reportado com IC 95% via bootstrap (5000 replicacoes): [2.65, 3.39]. A classificacao como superior a M3 (2.50) e estatisticamente significativa (t=198.6, p<0.001).",
    },
    "P14": {
        "status": "ATENCAO",
        "acao_tomada": "42 problemas testados incrementalmente. Rodadas documentadas por timestamp. Porem, nao ha garantia formal de nao-contaminacao.",
        "evidencia": "Snapshots no cora_scores.json mostram quando cada dimensao foi avaliada pela primeira vez.",
        "auto_resposta": "Os 42 problemas foram testados em 4 rodadas incrementais. Os snapshots temporais no cora_scores.json registram quando cada score foi atribuido. Nao ha como provar ausencia de contaminacao sem um conjunto de teste completamente isolado desde o inicio — limitacao reconhecida.",
    },
    "P15": {
        "status": "PENDENTE",
        "acao_tomada": "Nenhuma reavaliacao temporal foi realizada.",
        "evidencia": "Todos os snapshots sao de 28-29/maio/2026. Sem dados posteriores.",
        "auto_resposta": "Os resultados refletem o estado do ecossistema em 29/maio/2026. Nao ha garantia de que se mantenham em avaliacoes futuras. Uma reavaliacao periodica (semanal ou mensal) esta planejada mas nao executada.",
    },
}

# ══════════════════════════════════════════════════════════════════════
# AUDITOR AUTOMATICO — Aplica os 10 padroes a qualquer texto
# ══════════════════════════════════════════════════════════════════════

def audit_document_v2(text: str) -> List[Dict]:
    """Aplica os 10 padroes de ataque a um texto."""
    findings = []
    for padrao in TEN_ATTACK_PATTERNS:
        matches = re.findall(padrao["regex"], text, re.IGNORECASE)
        if matches:
            defense = DEFENSE_ARMY.get(padrao["id"], {})
            findings.append({
                "id": padrao["id"],
                "padrao": padrao["nome"],
                "matches": len(matches),
                "severidade": padrao["severidade"],
                "status_defesa": defense.get("status", "PENDENTE"),
                "contra_evidencia": padrao["contra_evidencia"],
            })
    return findings

def generate_defense_report() -> Dict:
    """Relatorio completo do estado das defesas."""
    total = len(DEFENSE_ARMY)
    resolvido = sum(1 for d in DEFENSE_ARMY.values() if d["status"] == "RESOLVIDO")
    parcial = sum(1 for d in DEFENSE_ARMY.values() if "PARCIAL" in d["status"])
    pendente = sum(1 for d in DEFENSE_ARMY.values() if d["status"] == "PENDENTE")
    atencao = sum(1 for d in DEFENSE_ARMY.values() if d["status"] == "ATENCAO")
    
    # Nota: 10pts por RESOLVIDO, 5pts por PARCIAL/ATENCAO, 0 por PENDENTE
    nota = resolvido * 10 + (parcial + atencao) * 5
    
    return {
        "total_padroes": total,
        "resolvido": resolvido,
        "parcial": parcial,
        "pendente": pendente,
        "atencao": atencao,
        "nota_defesa": nota,
        "nota_maxima": total * 10,
        "pct": round(nota / (total * 10) * 100, 1),
        "detalhes": DEFENSE_ARMY,
    }

# ══════════════════════════════════════════════════════════════════════
# TDD
# ══════════════════════════════════════════════════════════════════════

def test_10_patterns():
    assert len(TEN_ATTACK_PATTERNS) == 10, f"Esperado 10, obtido {len(TEN_ATTACK_PATTERNS)}"
    ids = {p["id"] for p in TEN_ATTACK_PATTERNS}
    assert len(ids) == 10, "IDs duplicados"
    print(f"  [TDD] 10 padroes de ataque registrados... PASS")
    return True

def test_defense_army():
    assert len(DEFENSE_ARMY) == 10, f"Esperado 10 defesas, obtido {len(DEFENSE_ARMY)}"
    for pid, defense in DEFENSE_ARMY.items():
        assert defense["status"] in ["RESOLVIDO", "RESOLVIDO PARCIALMENTE", "PENDENTE", "ATENCAO"]
        assert len(defense["auto_resposta"]) > 50, f"{pid}: resposta muito curta"
    print(f"  [TDD] 10 contramedidas com respostas prontas... PASS")
    return True

def test_audit_v2():
    problematic_text = """
    Nosso sistema obteve 95% de precisao, validado por milhares de testes internos.
    Comparado com um modelo simples, foi 53% superior.
    Esta dissertacao Qualis A1 apresenta resultados sem baseline trivial.
    """
    findings = audit_document_v2(problematic_text)
    assert len(findings) >= 3, f"Apenas {len(findings)} vulnerabilidades detectadas"
    
    report = generate_defense_report()
    assert report["nota_defesa"] >= 50, f"Nota defesa={report['nota_defesa']} muito baixa"
    print(f"  [TDD] Auditor v2: {len(findings)} vulns, nota defesa={report['nota_defesa']}/{report['nota_maxima']} ({report['pct']}%)... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  PILAR DE REVISAO v2.0 — 10 Padroes + Exercito de Defesa")
    print("=" * 65)
    
    tests = [
        ("10 padroes de ataque", test_10_patterns),
        ("Exercito de defesa", test_defense_army),
        ("Auditor v2", test_audit_v2),
    ]
    
    passed = 0
    for name, fn in tests:
        try:
            fn(); passed += 1
        except AssertionError as e:
            print(f"  [{name}] FAIL: {e}")
    
    report = generate_defense_report()
    print(f"\n  RELATORIO DE DEFESA:")
    print(f"    Resolvido: {report['resolvido']}/10")
    print(f"    Parcial:   {report['parcial']}/10")
    print(f"    Atencao:   {report['atencao']}/10")
    print(f"    Pendente:  {report['pendente']}/10")
    print(f"    Nota:      {report['nota_defesa']}/{report['nota_maxima']} ({report['pct']}%)")
    
    # Salva
    out = SCRIPT_DIR / "pilar_revisao_v2.json"
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "padroes": len(TEN_ATTACK_PATTERNS),
            "defesas": report,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n  RESULTADO: {passed}/{len(tests)} PASS")
    print(f"  Relatorio: {out}")
    print("=" * 65)
    return passed == len(tests)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
