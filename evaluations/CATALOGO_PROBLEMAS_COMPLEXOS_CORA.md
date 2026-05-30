# Catalogo de Problemas Complexos — Evolucao CORA-Eval

**Versao:** 1.0 | **Data:** 29/05/2026  
**Objetivo:** Fornecer problemas verificaveis para elevar CORA-Score de 2.62 → 4.00 (M4+M5)  
**Fontes:** Project Euler (988), Rosalind (284), DCA Listas (18), GAT (30+ refs), arXiv recent papers

---

## Indice de Fontes

| Fonte | Problemas | Area | Niveis | URL |
|-------|:---------:|------|--------|-----|
| Project Euler | 988 | Matematica/Computacao | N1-N4 | projecteuler.net/archives |
| Rosalind | 284 | Bioinformatica | N1-N4 | rosalind.info/problems/list-view/ |
| DCA Listas | 18 | Fisica-Matematica | N3-N4 | (local) |
| GAT Farinelli | 30+ refs | Geometria/Financas | N4 | arXiv:0910.1671v10 |
| arXiv comp-ph | 69 recentes | Fisica Computacional | N3-N4 | arxiv.org/list/physics.comp-ph/recent |

---

## D2 — Modelagem de Sistemas Fisicos (N3→N4, peso 12%)

### Problemas D2-N4 (Pesquisa, 3.0+)

| ID | Problema | Fonte | Cora V | Ground Truth |
|----|----------|-------|:------:|--------------|
| D2-N4-01 | Simulacao N-corpos com Barnes-Hut (N=10^5, erro < 10^-6) | arXiv:2605.29683 | V1,V5,V6,V7 | Conservacao de energia |
| D2-N4-02 | Equacao de Schrodinger dependente do tempo 2D (split-operator FFT) | arXiv comp-ph | V1,V6,V7 | Pacote Gaussiano analitico |
| D2-N4-03 | Dinamica Molecular NVE com potencial Lennard-Jones (N=10^4, 10^5 passos) | MD benchmarks | V1,V5,V7 | Temperatura, pressao, RDF |
| D2-N4-04 | CFD: Navier-Stokes 2D incompressivel (metodo de projecao, Re=1000) | OpenFOAM benchmarks | V1,V5,V6 | Lid-driven cavity (Ghia 1982) |
| D2-N4-05 | Simulacao de Monte Carlo Quantico (path integral, N=100 particulas) | arXiv:2605.30165 | V4,V5,V7 | Energia do estado fundamental |

### Problemas D2-N3 (Confirmacao TDD)

| ID | Problema | Fonte | Cora V | Tarefa CORA-Eval |
|----|----------|-------|:------:|------------------|
| D2-N3-01 | Secao de Poincare Henon-Heiles (E=1/6, E=1/8) | DCA Lista 2 Q3 | V5,V7 | D2-N3-04 |
| D2-N3-02 | Rede de Toda: integrais de movimento verificadas | DCA Lista 2 Q2 | V1,V2,V5 | D2-N3-04 |
| D2-N3-03 | Walker-Ford: ressonancias e superficies racionais | DCA Lista 2 Q4 | V1,V2 | D2-N3-04 |
| D2-N3-04 | Contato Hamiltoniano: toros instantaneos vs invariantes | DCA Lista 3 Q1-Q2 | V1,V6,V7 | D2-N3-04 |

---

## D3 — Analise Estatistica (N3→N4, peso 12%)

### Problemas D3-N4 (Pesquisa)

| ID | Problema | Fonte | Cora V | Ground Truth |
|----|----------|-------|:------:|--------------|
| D3-N4-01 | Inferencia Variacional para Mistura Gaussiana (K=3, ELBO converge) | PRML Bishop Cap.10 | V4,V5,V7 | Parametros verdadeiros conhecidos |
| D3-N4-02 | Causalidade: do-calculus + backdoor criterion (Pearl) | Pearl 2009 | V4 | DAG com efeito conhecido |
| D3-N4-03 | Modelo Hierarquico Bayesiano multi-nivel (WAIC, LOO, R-hat) | Gelman BDA3 | V4,V5,V7 | Dados simulados com parametros |
| D3-N4-04 | Processo Gaussiano com kernel Matern (otimizacao de hiperparametros) | Rasmussen & Williams | V4,V5,V7 | Funcao alvo conhecida |
| D3-N4-05 | Bootstrap para serie temporal (block bootstrap, stationary bootstrap) | Efron & Tibshirani | V4,V5 | Autocorrelacao conhecida |

### Problemas D3-N3 (Completar 3/5→5/5)

| ID | Problema | Fonte | Tarefa CORA-Eval |
|----|----------|-------|------------------|
| D3-N3-05 | Kaplan-Meier + Cox PH (dados de leucemia, n=23) | survival package R | D3-N3-05 |

---

## D4 — Quimica Computacional (N2→N4, peso 10%)

### Problemas D4-N3 (Pos-Graduacao)

| ID | Problema | Fonte | Cora V | Ground Truth |
|----|----------|-------|:------:|--------------|
| D4-N3-01 | Otimizacao geometria H2O com DFT (B3LYP/6-31G*) | Gaussian/ORCA | V5 | Angulo 104.5°, r=0.96A |
| D4-N3-02 | Espectro UV-Vis benzeno via TD-DFT | TD-DFT benchmarks | V5 | lambda_max ~255 nm |
| D4-N3-03 | Dinamica molecular NVT de alanina dipeptide (AMBER ff) | MD benchmarks | V5,V7 | Ramachandran plot |
| D4-N3-04 | Reacao SN2: Cl- + CH3Cl → ClCH3 + Cl- (IRC) | Gaussian/ORCA | V2,V5 | Barreira ~3 kcal/mol |

### Problemas D4-N4 (Pesquisa)

| ID | Problema | Fonte | Cora V |
|----|----------|-------|:------:|
| D4-N4-01 | Predicao de estrutura cristalina (CSP blind test) | Cambridge CCDC | V5 |
| D4-N4-02 | Design de catalisador enantioseletivo (DFT+microkinetics) | Organometallics | V5,V7 |
| D4-N4-03 | Mecanismo enzimatico QM/MM (ONIOM, cytochrome P450) | Chem. Rev. | V5,V7 |

---

## D5 — Biologia Molecular (N2→N4, peso 10%)

### Problemas D5-N3 (Pos-Graduacao) — Rosalind

| ID | Problema | Rosalind ID | Cora V | Tarefa CORA-Eval |
|----|----------|:----------:|:------:|------------------|
| D5-N3-01 | Montagem de genoma (de Bruijn graph, N50) | LONG, BA3* | V5,V7 | D5-N3-02 |
| D5-N3-02 | Alinhamento multiplo (ClustalW, perfil HMM) | CLUS, MSA | V4,V5 | — |
| D5-N3-03 | Predicao de estrutura secundaria RNA (Nussinov, ViennaRNA) | PMCH, RNAS | V5,V7 | — |
| D5-N3-04 | Arvore filogenetica (Neighbor-Joining, 100+ taxons) | NWCK, NKEW | V5 | D5-N3-03 |

### Problemas D5-N4 (Pesquisa)

| ID | Problema | Cora V |
|----|----------|:------:|
| D5-N4-01 | Predicao estrutura 3D proteina (AlphaFold/ESMFold) com RMSD | V5,V7 |
| D5-N4-02 | Filogenomica: 1000 genomas, max. likelihood, bootstrap 1000 | V4,V5 |
| D5-N4-03 | Docking molecular proteina-ligante com energia de ligacao | V5,V7 |

---

## D6 — Geociencias (N2→N4, peso 8%)

### Problemas D6-N3 (Pos-Graduacao)

| ID | Problema | Fonte | Cora V |
|----|----------|-------|:------:|
| D6-N3-01 | Modelo climatico EBM 1D com feedback de albedo | North 1975 | V5,V6 |
| D6-N3-02 | Reconstrucao paleoclimatica delta-O18 de testemunho Vostok | NOAA NCEI | V4 |
| D6-N3-03 | Dispersao gaussiana de poluentes (modelo de pluma) | Turner 1994 | V5,V6 |

### D6-N4

| ID | Problema | Fonte | Cora V |
|----|----------|-------|:------:|
| D6-N4-01 | Ensemble CMIP6: projecao 2100 com IC, atribuicao de forcantes | IPCC AR6 | V4,V5 |
| D6-N4-02 | Ciclo carbono acoplado oceano-atmosfera com feedback | GEOS-Chem | V6,V7 |
| D6-N4-03 | Full Waveform Inversion (FWI) sismica 2D | SEG benchmarks | V5,V7 |

---

## D7 — Codigo Cientifico (N3→N4, peso 10%)

### Problemas D7-N4

| ID | Problema | Cora V | Ground Truth |
|----|----------|:------:|--------------|
| D7-N4-01 | Biblioteca algebra linear (1000+ LOC) com triplas Hoare | V7b | numpy.linalg |
| D7-N4-02 | Codigo HPC MPI/OpenMP: race conditions, deadlocks | V7e,V7g | Valgrind/Helgrind |
| D7-N4-03 | Gradient Boosting: monotonicidade da loss, convergencia | V7g | XGBoost |
| D7-N4-04 | 100% branch coverage + boundary value analysis | V7f | gcov/lcov |

---

## D9 — Metodologia Experimental (N3→N4, peso 8%)

### Problemas D9-N4

| ID | Problema | Cora V |
|----|----------|:------:|
| D9-N4-01 | Bayesian Optimization para hiperparametros (GP-UCB) | V4,V7 |
| D9-N4-02 | Analise de sensibilidade global Sobol (N=20 parametros) | V5 |
| D9-N4-03 | Validacao Bland-Altman com padrao-ouro (bias < 5%) | V4 |

---

## Plano de Execucao para M4 (3.00)

| Dimensao | Acao | Nivel Alvo | Tarefas | Score | Ganho |
|----------|------|:----------:|:--------:|:-----:|:-----:|
| D2 | TDD Poincare + N-corpos | N3→N4 | 2/4 N4 | 3.50 | +0.10 |
| D3 | TDD inferencia variacional + causalidade | N3→N4 | 2/5 N4 | 3.40 | +0.14 |
| D4 | TDD DFT + MD (dados reais) | N2→N3 | 3/4 N3 | 2.67 | +0.08 |
| D5 | TDD alinhamento + filogenia Rosalind | N2→N3 | 3/4 N3 | 2.67 | +0.08 |
| D6 | TDD EBM climatico | N2→N3 | 2/3 N3 | 2.60 | +0.06 |
| D7 | TDD Hoare + HPC | N3→N4 | 2/5 N4 | 3.40 | +0.07 |
| D9 | TDD Sobol + Bland-Altman | N3→N4 | 2/4 N4 | 3.50 | +0.07 |
| | | | | **Total** | **+0.60** |

**CORA-Score projetado:** 2.62 + 0.60 = **3.22 (M4 Pesquisa)** ✅

---

## Plano para M5 (4.00)

| Dimensao | Acao | Alvo | Ganho |
|----------|------|:----:|:-----:|
| D2 | Completar 5/5 N4 | 4.00 | +0.06 |
| D3 | Completar 5/5 N4 | 4.00 | +0.07 |
| D4 | CSP + QM/MM (N4) | 4.00 | +0.13 |
| D5 | AlphaFold + filogenomica (N4) | 4.00 | +0.13 |
| D6 | CMIP6 + FWI (N4) | 4.00 | +0.10 |
| D7 | Completar 5/5 N4 | 4.00 | +0.05 |
| D8 | Meta-analise em rede PRISMA (N3→N4) | 3.33 | +0.11 |
| D9 | Completar 4/4 N4 | 4.00 | +0.05 |
| D10 | Gemeo digital sistema complexo (N4 completo) | 4.00 | +0.02 |
| | | **Total** | **+0.78** |

---

## Referencias

- Project Euler: https://projecteuler.net/archives (988 problemas)
- Rosalind: https://rosalind.info/problems/list-view/ (284 problemas)
- GAT: Farinelli, arXiv:0910.1671v10 (2021)
- DCA Listas: 3 listas de pos-graduacao (18 questoes)
- arXiv comp-ph: arxiv.org/list/physics.comp-ph/recent (69 recentes)
- WF-Bench: arXiv:2605.29683 (neural network wavefunction benchmark)
- Tunneling phase diagram: arXiv:2605.30165 (machine learning kinetic isotope effects)
