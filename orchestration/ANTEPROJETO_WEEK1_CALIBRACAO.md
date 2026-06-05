# Plano Semana 1 — Aplicacao da Calibracao ao Anteprojeto PPGTE

**Data:** 31/05/2026 | **Versao:** 1.0.0
**Framework:** SDD+TDD+AutoEvolve v4.6.1
**Calibracao base:** CORRIGENDUM V2 + C6 Anotacao Humana (92.77% agreement)
**Orquestrador:** ReasoningOrchestrator v11 (68 tipos, 7 fases)
**Verificadores:** Cora-Debate V1-V7
**Anti-circularidade:** SPEC-008 (Matriz A)

---

## 1. Proposito

Aplicar os pesos recalibrados do ReasoningOrchestrator v11 e as licoes do
C6 (anotacao humana, agreement 92.77%) ao desenvolvimento do Anteprojeto PPGTE,
usando o framework SDD+TDD+AutoEvolve como template metodologico.

### 1.1 Objetivos da Semana 1

| # | Objetivo | Entregavel | Prazo |
|:-:|----------|------------|:-----:|
| 1 | Mapear os 4 modulos do guia pratico (Fase 2 do anteprojeto) para o pipeline de 7 fases do ReasoningOrchestrator | `MODULO_MAP.md` | D+1 |
| 2 | Criar SPECs de conformidade LGPD + etica IA para cada modulo | 4 SPECs (A-D) | D+3 |
| 3 | Implementar testes TDD para os 4 modulos usando pesos recalibrados | `tests/test_modulo_*.py` (12 testes) | D+5 |
| 4 | Executar laco AutoEvolve com calibrated weights + C6 learnings | `refinement_loop_modulos.py` | D+7 |
| 5 | Validar contra CORA-Eval (150 tarefas, D1-D10, N1-N4) | `cora_scores_atualizado.json` | D+7 |

---

## 2. Mapeamento: Modulos do Guia Practico × Pipeline ReasoningOrchestrator v11

### 2.1 Arquitetura de 4 Modulos

O Anteprojeto PPGTE propoe 4 modulos educacionais. Cada modulo sera
desenvolvido usando o pipeline de 7 fases do ReasoningOrchestrator v11,
com pesos recalibrados do CORRIGENDUM:

```
ANTEPROJETO PPGTE — Guia Pratico de Uso Etico de IA Multiagente
  │
  ├── Modulo A: Configuracao Etica do Ambiente
  │   ├── F0 (15%): SPEC de configuracao etica
  │   ├── F4 (gate): R22+R24+R26 — validacao de permissoes
  │   └── F5 (gate): R28 + V3 — auditoria LGPD
  │
  ├── Modulo B: Pesquisa Bibliografica com Rastreabilidade DOI
  │   ├── F1 (15%): R12-R16 — inducao de fontes confiaveis
  │   ├── F2 (15%): R06-R11 — deducao logica de citacoes
  │   └── F5 (gate): R28 — cross-reference com fontes externas
  │
  ├── Modulo C: Redacao Academica com Auditoria Integrada
  │   ├── F3 (10%): R17-R21 — construcao de argumentos
  │   ├── F4 (gate): R24 — deteccao de contradicoes internas
  │   └── F6 (10%): R31-R34 — ProofHealth + PCI
  │
  └── Modulo D: Protecao de Dados e Protocolos de Anonimizacao
      ├── F5 (gate): R27 + V3 — verificacao exaustiva de vazamentos
      ├── Cora-Debate V5-V7 — validacao de conformidade LGPD
      └── F6 (10%): reflexao meta-cognitiva sobre privacidade
```

### 2.2 Pesos Recalibrados por Modulo

| Modulo | R10 | R22 | R24 | R26 | R27 | R28 | V3 | Outros |
|:------:|:---:|:---:|:---:|:---:|:---:|:---:|:--:|:------:|
| A | 18% | **25%** | 15% | 15% | 10% | **15%** | **25%** | R01-R05: 15% |
| B | **22%** | 10% | 10% | 10% | 10% | **15%** | 15% | R12-R16: 15% |
| C | 15% | 15% | **20%** | **20%** | 10% | 10% | 15% | R31-R34: 10% |
| D | 15% | 15% | 10% | 10% | **15%** | **15%** | **25%** | V5-V7: 20% |

**Legenda:** Negrito = peso elevado pela calibracao CORRIGENDUM.

---

## 3. Criacao de SPECs de Conformidade (SDD Layer)

### 3.1 Estrutura de cada SPEC

Cada modulo tera uma SPEC seguindo o padrao SDD:

```
SPEC-M<A|B|C|D>: <nome do modulo>
  ├── Objetivo
  ├── Requisitos de conformidade (LGPD, Resolucao PRPPG 39/2025, Floridi 2023)
  ├── Criterios de aceitacao (CTs)
  ├── Gatilhos de raciocinio (mapeamento R* + V*)
  ├── Metricas de sucesso
  └── Testes TDD associados
```

### 3.2 Tabela de Conformidade

| Modulo | LGPD Art. | Res. 39/2025 | Floridi (2023) | Raciocinio Primario |
|:------:|:---------:|:------------:|:--------------:|:-------------------:|
| A | 6, 7, 8 | Art. 3, 4 | Beneficencia | R10 + R22 |
| B | 9, 10 | Art. 5, 6 | Explicabilidade | R28 + V3 |
| C | 18, 19 | Art. 7, 8 | Nao maleficencia | R24 + R26 |
| D | 5, 11, 45-49 | Art. 9, 10 | Autonomia | R27 + V5-V7 |

### 3.3 Gatilhos de Raciocinio (Calibrados)

Inspirado na Matriz de Gatilhos do CORRIGENDUM:

| Condicao | Raciocinios Ativados | Fase |
|----------|---------------------|:----:|
| Novo modulo (nunca especificado) | R01->R10->R05->R22->R24 | F0->F1->F4 |
| Conformidade LGPD suspeita | R22->R26->R27->R28 | F4->F5 (gate) |
| Contradicao etica detectada | R24->R26->R22->R28 | F4->F5 |
| Cross-check com fontes externas | R28 + V3 | F5 (mandatorio) |
| PCI < 85 | Retornar para F3 | Ciclo de refino |
| Validacao final | V1->V2->V3->V5->V6->V7->R31 | F5->F6 |

---

## 4. Implementacao de Testes TDD

### 4.1 Estrutura de Testes por Modulo

Seguindo o padrao do FRAMEWORK.md (16 testes em 3 gates), adaptado:

```
tests/
  ├── test_modulo_a_configuracao_etica.py   # 3 CTs (Gate Compilacao)
  ├── test_modulo_b_rastreabilidade_doi.py  # 3 CTs (Gate Estrutura)
  ├── test_modulo_c_auditoria_redacao.py    # 3 CTs (Gate Qualidade)
  ├── test_modulo_d_anonimizacao_lgpd.py    # 3 CTs (Gate Conformidade)
  ├── test_pipeline_reasoning.py            # 2 CTs (Gate Pipeline)
  └── test_calibracao_pesos.py              # 2 CTs (Gate Calibracao)
  └── run_all_modulos.py                    # Runner central
```

### 4.2 Exemplo: CT para Modulo A

```
CT-A1: Configuracao Etica Inicial
  Dado: usuario iniciando o ambiente OpenCode pela primeira vez
  Quando: executa `opencode init --ethical`
  Entao: 
    - R22 (ContraexemploAgent) verifica permissoes de acesso
    - R27 (ExhaustiveAgent) busca exaustiva por vazamentos
    - R28 (CrossRefAgent) valida contra LGPD Art. 6-8
    - Todos os 3 devem passar (gate F4-F5)
  Peso: R22=25%, R27=15%, R28=15%
  Acao se falhar: retornar para F3 (construtiva) com diagnostico
```

### 4.3 Cobertura Esperada por Gate

| Gate | Testes | Cobertura | Criterio |
|:----:|:------:|:---------:|:--------:|
| Compilacao | 4 | SPEC-M*-* compilam | 4/4 passando |
| Estrutura | 4 | CTs por modulo | 4/4 passando |
| Qualidade | 4 | PCI >= 85 por modulo | 4/4 passando |
| Pipeline | 2 | 7 fases executam | 2/2 passando |
| Calibracao | 2 | Pesos recalibrados | 2/2 passando |
| **Total** | **16** | **16 CTs** | **16/16** |

---

## 5. Execucao do Laco AutoEvolve (Refinement Loop)

### 5.1 Pipeline Adaptado do FRAMEWORK.md

Para cada modulo (A-D), executar:

```
SENSE: Ler SPEC-M<modulo>.md + testes TDD
  │
  ▼
DIAGNOSE: Executar tests/test_modulo_<modulo>.py
  │       └── Falhas mapeadas por raciocinio (R22, R24, etc.)
  │
  ├─ PCI >= 85? → AVANCAR para VERIFY
  │
  ├─ PCI < 85? → ATIVAR ciclo de refino:
  │     │
  │     ├─ R22 (Contraexemplo): testar valores minimos/config basicas
  │     ├─ R24 (Contradicao): verificar inconsistencias internas
  │     ├─ R26 (StressTest): testar edge cases
  │     └─ Se falhar → retornar para F3 (construtiva)
  │
  ▼
FIX: Aplicar correcao automatica ou semi-automatica (Catalogo F01-F10)
  │
  ▼
VERIFY: Re-executar testes com pesos recalibrados
  │       └── R28 (CrossRef) obrigatorio em F5
  │
  ├─ Passou? → EVOLVE
  │
  └─ Falhou? → re-DIAGNOSE (max 5 iteracoes)
  │
  ▼
EVOLVE: Registrar licao em evolution/insight_*.md
  │
  ▼
LEARN: Atualizar memory.json com metricas da sessao
```

### 5.2 Parametros de Convergencia

| Parametro | Valor | Fonte |
|-----------|:-----:|-------|
| Max iteracoes por ciclo | 5 | FRAMEWORK.md Secao 9 |
| PCI minimo para avancar | 85 | CORRIGENDUM calibracao |
| PCI minimo para consolidar | 95 | CORRIGENDUM target |
| Agreement C6 para validacao | 0.9277 | RELATORIO_C6_ANOTACAO.md |
| Ciclos projetados para PCI >= 95 | 5 | CORRIGENDUM Secao 5 |
| Reducao de ciclos vs. baseline | 37.5% | CORRIGENDUM Secao 5 |

### 5.3 Ciclo de Refino com Raciocinios Calibrados

```
Ciclo 1: Proposicao inicial do modulo
  PCI: 65 → 70 (apos R10 decomposicao)

Ciclo 2: Apos R22 (contraexemplos)
  PCI: 70 → 80 (+10%)
  Gate: F4 ativado

Ciclo 3: Apos R24+R26 (refutacao)
  PCI: 80 → 88 (+8%)
  Gate: F5 ativado

Ciclo 4: Apos R27 (exaustao)
  PCI: 88 → 92 (+4%)
  V3 verifica contraexemplos

Ciclo 5: Apos R28 (cross-reference)
  PCI: 92 → 96 (+4%)
  Consolidacao: EVOLVE + LEARN
```

---

## 6. Integracao com C6 — Licoes da Anotacao Humana

### 6.1 O que o C6 nos ensinou

| Licao | Impacto | Aplicacao no Modulo |
|-------|---------|-------------------|
| R209 (KAM) agreement 0.6667 — menor confiabilidade | Nao usar R209 como gate principal | Usar combo R10+R22+R26 |
| R08 agreement 0.9425 — mais frequente (29 ocorrencias) | Confiavel para uso frequente | Gate F0 padrao |
| 17 tipos unicos em 30 docs (26.5% dos 68) | Cobertura suficiente para calibrar | Nao requer expansao |
| IC95% [0.8839, 0.9542] — precisao alta | Margem de erro ±3.5% | Incorporar nos thresholds |
| 3 perguntas/padrao (genuino, correto, sem_vies) | Framework de validacao 3D | Adaptar para 3 perguntas de auditoria |

### 6.2 Protocolo de Auditoria para cada Modulo (herdado do C6)

Cada modulo sera submetido a 3 perguntas de auditoria:

```
Pergunta 1 (Genuino): O conteudo do modulo faz sentido no contexto
  de uso etico de IA? (0/1)

Pergunta 2 (Correto): As instrucoes estao factualmente corretas
  e em conformidade com LGPD/Res. 39/2025? (0/1)

Pergunta 3 (Sem Vies): O modulo evita vies de auto-promocao da
  plataforma, apresentando limitacoes de forma transparente? (0/1)
```

Threshold: agreement >= 0.80 para avancar (baseado na Matriz A do C6).

---

## 7. Validacao CORA-Eval Pos-Calibracao

### 7.1 Projecao de Scores

| Dimensao | Score Atual | Alvo Semana 1 | Verificadores | Modulo Associado |
|:--------:|:-----------:|:-------------:|:-------------:|:----------------:|
| D1 (Matematica) | 3.8 | 4.2 | V1+V2+V3 | Estrutura logica |
| D2 (Fisica) | 3.5 | 3.8 | V1+V2 | Modelos causais |
| D3 (Computacao) | 3.4 | 3.8 | V2+V3 | Configuracao (Mod A) |
| D4 (Quimica) | 2.23 | 2.8 | V3 | Anonimizacao (Mod D) |
| D5 (Biologia) | 2.8 | 3.2 | V3+V4 | Dados sensiveis |
| D6 (Engenharia) | 2.6 | 3.0 | V2+V3 | Pipeline (Mod B) |
| D7 (Economia) | 3.2 | 3.5 | V4+V5 | Custo-beneficio |
| D8 (Literatura) | 2.23 | 2.8 | V3 | Redacao (Mod C) |
| D9 (Metodologia) | 2.67 | 3.2 | R24+R28 | Metodologia cientifica |
| D10 (Cross-domain) | 2.8 | 3.2 | R28 | Integracao modulos |
| **CORA-Score** | **3.04** | **3.45** | — | — |
| **CORA-V-Score** | **2.56** | **3.20** | V3+V7 | — |

### 7.2 Procedimento de Validacao

```
1. Executar cora_benchmark_tracker.py com pesos recalibrados
2. Medir CORA-Score e CORA-V-Score para cada dimensao
3. Comparar delta real vs. projetado
4. Identificar dimensoes com delta < 50% do projetado
5. Para cada dimensao abaixo do esperado:
   a. Ativar ciclo de refino com R22+R24+R26
   b. Re-testar com pesos ajustados
6. Atualizar cora_scores.json com novos valores
7. Gerar relatorio de convergencia
```

### 7.3 Verificadores Cora-Debate por Modulo

| Modulo | V1 | V2 | V3 | V4 | V5 | V6 | V7 |
|:------:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| A | Sim | Sim | **Gate** | — | Sim | Sim | Sim |
| B | Sim | Sim | Sim | — | Sim | Sim | — |
| C | — | Sim | Sim | Sim | Sim | Sim | — |
| D | — | — | **Gate** | — | **Gate** | **Gate** | Sim |

**Legenda:** Gate = obrigatorio na fase F5, com peso aumentado (+10%).

---

## 8. Cronograma Detalhado — Semana 1

| Dia | Atividade | Ferramenta | Entregavel | Gate |
|:---:|-----------|-----------|------------|:----:|
| D+1 | Mapear modulos para pipeline 7 fases | ReasoningOrchestrator v11 | `MODULO_MAP.md` | Revisao par |
| D+2 | Criar SPEC-MA (Configuracao Etica) | SDD Layer | `SPEC_MA_CONFIG.md` | Review R10+R22 |
| D+2 | Criar SPEC-MB (Rastreabilidade DOI) | SDD Layer | `SPEC_MB_DOI.md` | Review R28 |
| D+3 | Criar SPEC-MC (Auditoria Redacao) | SDD Layer | `SPEC_MC_AUDITORIA.md` | Review R24+R26 |
| D+3 | Criar SPEC-MD (Anonimizacao LGPD) | SDD Layer | `SPEC_MD_ANONIMIZACAO.md` | Review V3+V5-V7 |
| D+4 | Implementar testes TDD Mod A+B | TDD Layer | `test_modulo_a+b.py` (6 CTs) | 6/6 passando |
| D+5 | Implementar testes TDD Mod C+D | TDD Layer | `test_modulo_c+d.py` (6 CTs) | 6/6 passando |
| D+5 | Implementar testes pipeline+pesos | TDD Layer | `test_pipeline+pesos.py` (4 CTs) | 4/4 passando |
| D+6 | Executar laco AutoEvolve (1a iteracao) | `refinement_loop_modulos.py` | Log de diagnostico | PCI >= 85 |
| D+6 | Ciclo de refino (se PCI < 85) | R22+R24+R26 | Diagnostico F4 | Gate F4 |
| D+7 | Validacao CORA-Eval | `cora_benchmark_tracker.py` | `cora_scores_atualizado.json` | CORA >= 3.45 |
| D+7 | Registro de licoes e insights | AutoEvolve LEARN | `insight_week1.md` | Memory atualizado |

---

## 9. Metricas de Sucesso da Semana 1

| Indicador | Formula | Target | Alerta |
|-----------|---------|:-----:|:------:|
| Cobertura de CTs | `testes_passando / 16` | 1.0 | < 1.0 |
| PCI medio por modulo | `media(PCI_A, PCI_B, PCI_C, PCI_D)` | >= 85 | < 80 |
| CORA-Score | `media(D1..D10)` | >= 3.45 | < 3.20 |
| CORA-V-Score | `media_ponderada(V1..V7)` | >= 3.20 | < 2.80 |
| Agreement auditoria | `acu de 3 perguntas` | >= 0.80 | < 0.70 |
| Densidade de erros | `erros / modulo` | <= 2 | > 3 |
| Convergencia | `iteracoes_para_pci_85` | <= 3 | > 5 |

---

## 10. Riscos e Mitigacao

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|:-------------:|:-------:|-----------|
| Pesos recalibrados nao convergem para Mod C (Redacao) | Media | Alto | Ativar R24+R26 em loop; reduzir peso de R10 |
| Agreement C6 nao se replica para auditoria dos modulos | Baixa | Alto | Re-aplicar protocolo C6 para modulos (budget 10 docs) |
| CORA-Score nao atinge 3.45 na Semana 1 | Media | Medio | Estender para Semana 2 com foco em D4 e D8 (piores dimensoes) |
| Conflito entre requisitos LGPD e funcionalidades da plataforma | Baixa | Alto | Documentar como ADR; consultar especialista juridico |
| Esgotamento do budget de 5 iteracoes por ciclo | Baixa | Medio | Registrar como insight; ajustar pesos para proximo round |

---

## 11. Registro de Decisoes (ADRs)

| ADR | Decisao | Rationale | Data |
|:---:|---------|-----------|:----:|
| CAL-001 | Usar combo R10+R22+R26+V3+R28 como nucleo de cada modulo | CORRIGENDUM validou 5 raciocinios cobrem 100% dos casos | D+1 |
| CAL-002 | Gate F4 obrigatorio para todos os modulos | Licao C6: R22 com agreement 0.9425 e mais frequente | D+1 |
| CAL-003 | Auditoria 3 perguntas por modulo (herdado do C6) | C6 validou framework 3D com agreement 92.77% | D+2 |
| CAL-004 | PCI target 85 para avancar, 95 para consolidar | CORRIGENDUM Secao 5: 5 ciclos para PCI 95 | D+2 |
| CAL-005 | D4 e D8 tem prioridade de refino (scores mais baixos) | CORA-Eval: D4=2.23, D8=2.23 vs. media 3.04 | D+1 |

---

## 12. Proxima Etapa (Apos Semana 1)

### Passo 3: Benchmark CORA-Eval Pos-Calibracao

Apos aplicar a calibracao, executar benchmark completo:

```
1. Rodar 150 tarefas (10 dimensoes x 4 niveis x 3.75 tarefas/nivel)
2. Calcular delta real vs. projetado
3. Se delta >= 80% do projetado: CALIBRACAO VALIDADA
4. Se delta < 50%: recalibrar com insights adicionais
5. Atualizar cora_scores.json
6. Gerar relatorio de validacao
```

### Passo 4: Evolution Round 14

Registrar no EvolutionService:

```
Round 14:
  - best_score: CORA pos-calibracao
  - insights: C6 Matriz A, PCI target 95, combo calibrado
  - health: atualizar com metricas da Semana 1
  - evo-state: round 13 → round 14
```

---

## 13. Referencias

- `CORRIGENDUM_V2_RETRATACAO.md` — Erro IMO 2025 P1 (3 camadas)
- `RELATORIO_CALIBRACAO_CORRIGENDUM.md` — Calibracao completa (10 secoes)
- `RELATORIO_C6_ANOTACAO.md` — C6 protocolo (92.77% agreement, Matriz A)
- `FRAMEWORK.md` — SDD+TDD+AutoEvolve template
- `SPEC_008_ANTI_CIRCULARIDADE.md` — Anti-circularity framework
- `anteprojeto.tex` — Anteprojeto PPGTE formal
- `reasoning-orchestrator-v11/SKILL.md` — 68 raciocinios, 7 fases
- `cora-debate/SKILL.md` — V1-V7, Q-Score UCB1
- `cora_benchmark_tracker.py` — Runner do benchmark
- `cora_scores.json` — Scores atuais (CORA=3.04, CORA-V=2.56)
- `CROSS_CORRELATION_ALETHEIA_OPENCODE.md` — 12 dimensoes comparadas
- `evolution.py` — EvolutionService (pipeline 6 fases)

---

*Gerado por AutoEvolve — OpenCode Ecosystem v4.6.1*
*Metodo: SENSE->DISCOVER->ANALYZE->CALIBRATE->VERIFY->LEARN*
*Proposito: Aplicar calibracao CORRIGENDUM + C6 ao Anteprojeto PPGTE Semana 1*
