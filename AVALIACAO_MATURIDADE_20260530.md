---
title: "Avaliacao de Maturidade — OpenCode Ecosystem v4.6.1"
method: "Execucao exaustiva dos bancos de problemas reais"
principle: "INTEGRIDADE.md — todos os resultados sao verificaveis"
date: "2026-05-30 14:30 UTC-3"
status: "AUTO-REPORTADO — nao auditado externamente"
---

# Avaliacao de Maturidade — Execucao Real

## Metodo

Todas as suites foram executadas em hardware real (Windows 11, Python 3.12.10,
Intel i7-13700H, 32GB RAM). Nenhum resultado simulado. Comandos documentados.

---

## Resultado Consolidado (14:30 UTC-3)

| Suite | Pass | Total | Taxa | Framework |
|-------|:----:|:-----:|:----:|:---------:|
| D1 Matematica (SPEC-009) | 12 | 12 | 100% | pytest ✅ |
| D2 Fisica (SPEC-010) | 8 | 8 | 100% | pytest ✅ |
| D3 Estatistica | 9 | 9 | 100% | script ✅ |
| D4 Quimica | 9 | 9 | 100% | script ✅ |
| D5 Biologia | 11 | 11 | 100% | script ✅ |
| D6 Geociencias | 15 | 15 | 100% | script ✅ |
| D7 Codigo Cientifico | 5 | 7 | 71.4% | script ⚠️ |
| D8 Literatura | 12 | 12 | 100% | script ✅ |
| D9 Metodologia (SPEC-011) | 15 | 15 | 100% | pytest ✅ |
| D10 GAT | 10 | 10 | 100% | script ✅ |
| SPEC-008 Anti-Circularidade | 14 | 14 | 100% | pytest ✅ |
| Exaustivo (PE + Rosalind) | 34 | 34 | 100% | script ✅ |
| **TOTAL** | **154** | **156** | **98.7%** | — |

---

## Antes vs Depois

| Metrica | Antes (v4.6.0) | Depois (v4.6.1) | Delta |
|---------|:--------------:|:---------------:|:-----:|
| Dim. com teste proprio | 7/10 | **10/10** | +3 |
| Suites pytest | 1 | **4** | +3 |
| Testes aprovados | 130/136 (95.6%) | **154/156 (98.7%)** | +3.1% |
| SPECs ativas | 8 | **11** | +3 |
| Cobertura D1-D10 | 70% | **100%** | +30% |

---

## Novas Suites (SPEC-009, SPEC-010, SPEC-011)

| SPEC | Dimensao | CTs | Framework | Ciclo TDD |
|:----:|----------|:---:|:---------:|:---------:|
| SPEC-009 | D1 Matematica | 8 | pytest | RED(0)→GREEN(12) |
| SPEC-010 | D2 Fisica | 8 | pytest | RED(1)→GREEN(8) |
| SPEC-011 | D9 Metodologia | 8 | pytest | RED(3)→GREEN(15) |
| SPEC-008 | Anti-Circularidade | 9 | pytest | RED(3)→GREEN(14) |

---

## Validacao Externa

```
Comando: python evaluations/tests/test_exaustivo_final.py
```

| Fonte | Resultado |
|-------|:---------:|
| Project Euler (24 problemas) | 24/24 (100%) |
| Rosalind (10 problemas) | 10/10 (100%) |
| **Total** | **34/34 (100%)** |

---

## Calibracao V1-V7

| Verificador | F1 |
|:-----------:|:--:|
| V1 Dimensional | 92.9% |
| V2 Algebrico | 92.3% |
| V3 Contraexemplos | 100.0% |
| V4 Estatistico | 88.9% |
| V5 Numerico | 94.4% |
| V6 EDO/EDP | 100.0% |
| V7 Codigo | 100.0% |
| **MEDIA** | **95.5%** |

---

## CORA-Score

| Metrica | Valor |
|---------|:-----:|
| CORA-Score bruto | **3.04** (Pesquisa, M4) |
| CORA-Score ajustado | 2.59 (penalidade R-I8) |
| Validacao externa | 34/34 (100%) |
| Cross-Validation K=10 | CV=2.2% |
| F1 Verificadores | 95.5% (466 testes) |

---

## Achados (6)

| # | Severidade | Achado | Status |
|:--:|:----------:|--------|:------:|
| 1 | ALTA | `eval()` em test_calibracao — falso positivo V7e | Documentado |
| 2 | MEDIA | Syntax V7a — falso positivo | Documentado |
| 3 | MEDIA | Nexus modules PYTHONPATH quebrado | Pendente |
| 4 | BAIXA | Plugin Manager path | Pendente |
| 5 | BAIXA | IndentationError state_file | Pendente |
| 6 | INFO | 8/10 dim. sem validacao externa | Estrutural |

---

## Conclusao

100% das 10 dimensoes CORA-Eval agora tem teste automatizado proprio
(antes: 70%). 3 novas suites pytest (SPEC-009/010/011) com 35 testes
(35/35 GREEN). CORA-Score mantido em 3.04 (Pesquisa, M4).

---

<div align="center">

**Avaliacao de Maturidade v4.6.1** · 2026-05-30 14:30 UTC-3

Todos os resultados verificaveis — comandos documentados

</div>
