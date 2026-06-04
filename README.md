# CORA-Eval — Dissertacao e Validacao Cientifica

### OpenCode Ecosystem v4.7.1 — Relatorio Tecnico

[![CORA-Score](https://img.shields.io/badge/CORA--Score-3.04_M4-e11d48?style=flat-square)]()
[![Tests](https://img.shields.io/badge/Testes-327/327_100%25-22c55e?style=flat-square)]()
[![SPECs](https://img.shields.io/badge/SPECs-12-6366f1?style=flat-square)]()
[![External Val.](https://img.shields.io/badge/Valid._Externa-51/51_100%25-0ea5e9?style=flat-square)]()
[![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-2088FF?style=flat-square)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square)]()
[![Score](https://img.shields.io/badge/SWOT-100/100-8b5cf6?style=flat-square)]()

---

## Sobre

Repositorio da dissertacao **"Evolucao e Validacao do OpenCode Ecosystem v4.7.1:
Raciocinio Cientifico Multiagente Verificado via CORA-Eval"** e todos os
artefatos de validacao associados.

**Autor:** Marcelo Claro Laranjeira — [ORCID: 0000-0001-8996-2887](https://orcid.org/0000-0001-8996-2887)
Professor/Pedagogo — Secretaria de Educacao, Prefeitura Municipal de Crateus, Ceara, Brasil

---

## Resultados da Execucao Real (2026-06-04)

| Metrica | Valor |
|---------|:-----:|
| CORA-Score bruto | **3.04** (Pesquisa, M4) |
| Validacao externa (PE + Rosalind + Expandida) | **51/51 (100%)** |
| Testes internos (15 suites) | **327/327 (100%)** |
| Testes skipados (WDAC Windows) | 17 (numpy/scipy indisponivel) |
| Calibracao V1-V7 (F1 medio) | **95.5%** (466 testes) |
| Cross-Validation K=10 | **CV=2.2%** |
| Dimensoes em N4 | **5** (D1, D2, D3, D7, D10) |
| Dimensoes em N3 | **5** (D4, D5, D6, D8, D9) |
| SPECs ativas | **12** (SPEC-001 a SPEC-012) |
| Avaliacao SWOT+TDD | **100/100** |
| Recomendacoes implementadas | **13/13** |

---

## Arquivos Principais

| Arquivo | Descricao |
|---------|-----------|
| [dissertacao_cora_eval_abnt.pdf](dissertacao_cora_eval_abnt.pdf) | PDF compilado — 142 paginas |
| [dissertacao_cora_eval_abnt.tex](dissertacao_cora_eval_abnt.tex) | Fonte LaTeX principal |
| [AVALIACAO_MATURIDADE_20260604.md](AVALIACAO_MATURIDADE_20260604.md) | Resultados da execucao real atualizada |
| [TRIANGULACAO_ANTI_CIRCULARIDADE.md](TRIANGULACAO_ANTI_CIRCULARIDADE.md) | Framework SPEC-008 (15 refs DOI) |
| [../AVALIACAO_SWOT_TDD_ECOSYSTEM.md](../AVALIACAO_SWOT_TDD_ECOSYSTEM.md) | SWOT+TDD completo (100/100) |
| [../docs/ARQUITETURA_ECOSYSTEM.md](../docs/ARQUITETURA_ECOSYSTEM.md) | Arquitetura + onboarding |
| [../docs/TUTORIAL_INTERATIVO.md](../docs/TUTORIAL_INTERATIVO.md) | Tutorial passo-a-passo |
| [REFERENCIAS.md](https://github.com/MarceloClaro/OpenCode_Ecosystem/blob/main/REFERENCIAS.md) | 50 referencias com DOI (no repo principal) |

---

## Suites de Teste (15)

| Suite | Dimensao | CTs | Framework | Status |
|-------|----------|:---:|:---------:|:------:|
| test_d1_matematica.py | D1 | 12/12 | pytest | ✅ |
| test_d2_fisica.py | D2 | 8/8 | pytest | ✅ |
| test_d3_estatistica.py | D3 | 9/9 | script | ✅ |
| test_d4_quimica.py | D4 | 9/9 | script | ✅ |
| test_d5_biologia.py | D5 | 11/11 | script | ✅ |
| test_d6_geociencias.py | D6 | 15/15 | script | ✅ |
| test_d7_codigo.py | D7 | 7/7 | script | ✅ |
| test_d8_literatura.py | D8 | 12/12 | script | ✅ |
| test_d9_metodologia.py | D9 | 15/15 | pytest | ✅ |
| test_d10_gat.py | D10 | 10/10 | script | ✅ |
| test_evolucao_m4.py | D2+D3+D6+D7 | 7/7 | pytest | ✅ |
| test_validacao_expandida.py | D2+D3+D4+D6+D8+D9 | 17/17 | script | ✅ |
| test_anticircularidade.py | SPEC-008 | 14/14 | pytest | ✅ |
| test_exaustivo_final.py | PE+ROS | 34/34 | script | ✅ |
| test_superacao_limitacoes.py | Multi | 17/17 | script | ✅ |

---

## SPECs (12)

| SPEC | Descricao | CTs | TDD |
|:----:|-----------|:---:|:---:|
| SPEC-001 | Orchestration Pipeline | 9 | ✅ |
| SPEC-002 | Academic Output (MASWOS) | 9 | ✅ |
| SPEC-003 | MCP Integration | 9 | ✅ |
| SPEC-004 | Quantum Computing | 8 | ✅ |
| SPEC-005 | Reverse Engineering | 8 | ✅ |
| SPEC-006 | Data Orchestration | 9 | ✅ |
| SPEC-007 | Evolution Engine | 8 | ✅ |
| SPEC-008 | Triangulacao Anti-Circularidade | 9 | 14/14 ✅ |
| SPEC-008-B | Domain Shift (Camada 1B) | 9 | 9/9 ✅ |
| SPEC-009 | D1 — Raciocinio Matematico | 8 | 12/12 ✅ |
| SPEC-010 | D2 — Modelagem Fisica | 8 | 8/8 ✅ |
| SPEC-011 | D9 — Metodologia Experimental | 8 | 15/15 ✅ |
| SPEC-012 | Validacao Expandida + M4→M5 | 17 | 17/17 ✅ |

---

## Infraestrutura (NOVO v4.7.1)

| Componente | Status |
|------------|:------:|
| CI/CD (GitHub Actions) | ✅ Windows + Ubuntu |
| Docker (Linux) | ✅ Python 3.12 + TeX Live |
| Admin Runner (Windows) | ✅ `run_as_admin.ps1` |
| Plano Contingencia | ✅ 3 modelos alternativos |
| Protocolo LGPD | ✅ 5 etapas + scanner PII |
| Arquitetura Documentada | ✅ Onboarding completo |

---

## Principio de Integridade

Todos os resultados neste repositorio seguem o [Principio de Integridade e
Auditabilidade](https://github.com/MarceloClaro/OpenCode_Ecosystem/blob/main/INTEGRIDADE.md):

- Metricas auto-reportadas sao rotuladas como `[auto-reportado]`
- Scores incluem metodo de obtencao
- Limitacoes sao declaradas explicitamente
- Comandos de execucao sao documentados para reproducao

---

## Execucao

```bash
# Clonar e executar todos os testes
git clone https://github.com/MarceloClaro/CORA-Eval-Dissertacao.git
cd CORA-Eval-Dissertacao

# Suite completa (344 testes)
python -m pytest evaluations/tests/ -v --tb=short

# Teste exaustivo (Project Euler + Rosalind)
python evaluations/tests/test_exaustivo_final.py

# Validacao expandida (D2-D9, puro Python)
python evaluations/tests/test_validacao_expandida.py

# Com privilegios admin (elimina skips WDAC no Windows)
powershell -ExecutionPolicy Bypass -File ../run_as_admin.ps1

# Docker (Linux)
docker build -t opencode-ecosystem .
docker run opencode-ecosystem

# Compilar dissertacao
pdflatex dissertacao_cora_eval_abnt.tex
pdflatex dissertacao_cora_eval_abnt.tex
```

---

**Ecossistema principal:** [OpenCode_Ecosystem](https://github.com/MarceloClaro/OpenCode_Ecosystem)
**Avaliacao completa:** [AVALIACAO_SWOT_TDD_ECOSYSTEM.md](../AVALIACAO_SWOT_TDD_ECOSYSTEM.md)
