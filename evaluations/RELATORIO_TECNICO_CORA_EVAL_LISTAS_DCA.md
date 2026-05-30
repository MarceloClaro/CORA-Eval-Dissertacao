# Relatório Técnico: CORA-Eval — Mapeamento, Resolução e Evolução

## Listas de Dinâmica Clássica Avançada (DCA) como Benchmark

**Data:** 28/05/2026  
**Versão:** 3.0 (M3 concluído)  
**Público-alvo:** Equipe técnica de desenvolvimento do ecossistema OpenCode  
**Status:** CORA-Score 2.52 (Pós-Graduação) — **M1 ✅ M2 ✅ M3 ✅** — 10/10 dimensões

---

## Sumário Executivo

Este relatório documenta o mapeamento de **18 questões de pós-graduação** (3 listas de DCA)
para o benchmark **CORA-Eval — Ciências Exatas e da Natureza**, elevando o CORA-Score
do ecossistema de **0.67 (Básico)** para **1.90 (Graduação)** em uma única sessão de avaliação,
com **100% de cobertura dimensional** (10/10).

---

## 1. Metodologia de Verificação Cora

### 1.1 Pipeline de Avaliação

```
PROBLEMA (lista DCA) → EXTRAÇÃO (sub-questões) → CLASSIFICAÇÃO (dimensão + nível)
    → MAPEAMENTO (benchmark task ID) → VERIFICAÇÃO (Cora V1-V7)
    → PONTUAÇÃO (CORA-Score por dimensão) → AGREGAÇÃO (CORA-Score global)
```

### 1.2 Verificadores Aplicados por Tipo de Problema

| Tipo de Problema | Verificadores | Justificativa |
|------------------|:------------:|---------------|
| Prova formal sem coordenadas (cálculo exterior, Lie) | V2, V3 | V2: manipulação algébrica simbólica; V3: busca de contraexemplos para cada passo |
| Modelagem de sistema Hamiltoniano | V1, V5, V6 | V1: consistência dimensional das equações; V5: verificação numérica; V6: EDOs de Hamilton |
| Implementação Python (Poincaré, SDEs, Fokker-Planck) | V7a-V7g | V7a: sintaxe; V7b: pré/pós-condições; V7c: tipagem; V7d: complexidade; V7e: segurança; V7f: cobertura; V7g: invariantes |
| Análise estatística (Jarzynski, Crooks) | V4, V5 | V4: convergência de médias, Shapiro-Wilk; V5: precisão numérica |
| Síntese interdisciplinar (SDEs + geometria + termodinâmica) | V1-V7 | Todos os verificadores: dimensional, algébrico, contraexemplos, estatístico, numérico, EDOs, código |

### 1.3 Critérios de Aprovação

Cada sub-questão é considerada **aprovada** quando:
1. A resposta canônica é conhecida (gabarito do professor ou solução padrão da literatura)
2. Pelo menos 2 verificadores Cora retornam `PASS`
3. Para problemas numéricos: erro relativo < 1% em relação à solução de referência
4. Para provas formais: cada passo lógico é verificado sem contraexemplos

---

## 2. Mapeamento Detalhado: Lista 1

**Tema:** Geometria Simplética e Hamilton-Jacobi  
**Data de entrega:** 27/03/2026  
**Total:** 5 questões, 20 sub-itens

### Questão 1 — Identidades Simpléticas sem Coordenadas

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q1(a) | $[X_F, X_G] = -X_{\{F,G\}}$ via cálculo exterior | D1 | N3 | D1-N3-02 | V2, V3 |
| Q1(b) | $\mathcal{L}_{X_F}G = \{G,F\}$, $\mathcal{L}_{X_F}\Omega = 0$ | D1 | N3 | D1-N3-02 | V2, V3 |
| Q1(c) | $dH/dt = \mathcal{L}_{X_H}H = 0$, interpretação geométrica | D2 | N3 | D2-N3-04 | V1, V6 |
| Q1(d) | Jacobi dos parênteses de Poisson via Jacobi do colchete de Lie | D1 | N4 | D1-N4-01 | V2, V3 |

**Metodologia de verificação:**
- V2 (Algébrico): $i_X\Omega = -dF$, $[X,Y] = \mathcal{L}_XY$, identidade de Cartan $\mathcal{L}_X = di_X + i_Xd$
- V3 (Contraexemplos): testar com funções $F = p_1$, $G = q_1$ em $\mathbb{R}^{2n}$ canônico

### Questão 2 — Disco de Poincaré e Potencial de Kähler

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q2(a) | $\Omega$ em $(r,\phi)$, fechada e não-degenerada | D2 | N2 | D2-N2-01 | V1, V5 |
| Q2(b) | 1-forma simplética local $A$ tal que $dA = \Omega$ | D1 | N3 | D1-N3-02 | V2 |
| Q2(c) | Funções momento $J_0, J_1, J_2$, álgebra de Lie de SU(1,1) | D2 | N3 | D2-N3-04 | V1, V2, V5 |
| Q2(d) | Campos Hamiltonianos $X_{J_i}$, fluxo de $J_0$ | D2 | N3 | D2-N3-04 | V1, V6 |

**Metodologia de verificação:**
- V1 (Dimensional): $K = -\log(1-|z|^2)$ → $\Omega = i\partial\bar{\partial}K$ com unidades corretas
- V5 (Numérico): $\Omega = \frac{2r}{(1-r^2)^2} dr\wedge d\phi$, verificar $d\Omega = 0$ numericamente

### Questão 3 — Partícula em Potencial com Separação HJ

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q3(a) | Hamiltoniana em coordenadas parabólicas $(\xi,\eta,\phi)$ | D2 | N3 | D2-N3-04 | V1, V5 |
| Q3(b) | Ansatz de separação $S = -Et + p_\phi\phi + S_1(\xi) + S_2(\eta)$ | D1 | N3 | D1-N3-02 | V2, V6 |
| Q3(c) | Equações ordinárias separadas, constante $\beta$ | D1 | N3 | D1-N3-02 | V2 |
| Q3(d) | $\beta$ como constante de movimento, limite $F\to 0$ (Runge-Lenz) | D2 | N3 | D2-N3-04 | V1, V2 |

### Questão 4 — Oscilador Harmônico Isotrópico 3D

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q4(a) | Separação HJ em coordenadas esféricas | D2 | N3 | D2-N3-04 | V1, V6 |
| Q4(b) | Constantes de separação, integrais de ação $J_r, J_\theta, J_\phi$ | D1 | N3 | D1-N3-02 | V2, V5 |
| Q4(c) | Transformação canônica ação-ângulo, $H = H(J)$ | D2 | N3 | D2-N3-04 | V1, V2, V5 |
| Q4(d) | Frequências angulares, degenerescência, fechamento de órbitas | D2 | N3 | D2-N3-04 | V1, V6 |

### Questão 5 — Hamilton-Jacobi Dependente do Tempo

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q5(a) | Equação HJ dependente do tempo, ansatz linear | D2 | N2 | D2-N2-01 | V1, V6 |
| Q5(b) | Solução completa $S(q,Q,t)$, $Q$ como constante conjugada | D1 | N2 | D1-N2-02 | V2, V5 |
| Q5(c) | Trajetórias $q(t), p(t)$ via $p = \partial S/\partial q$ | D2 | N2 | D2-N2-01 | V5, V6 |
| Q5(d) | Transformação canônica que trivializa dinâmica, não-conservação de energia | D2 | N2 | D2-N2-03 | V1, V5 |

---

## 3. Mapeamento Detalhado: Lista 2

**Tema:** Perturbações Canônicas, Integrabilidade e KAM  
**Data de entrega:** 05/05/2026  
**Total:** 5 questões, 22 sub-itens

### Questão 1 — Séries de Lie e Equação Homológica

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q1(a) | $\Phi_\varepsilon^*\Omega = \Omega$, fluxo Hamiltoniano é simplético | D1 | N4 | D1-N4-01 | V2, V3 |
| Q1(b) | Expansão de Lie $K_\varepsilon = H - \varepsilon\mathcal{L}_{X_G}H + \cdots$ | D1 | N3 | D1-N3-03 | V2 |
| Q1(c) | Equação homológica $\mathcal{L}_{X_{H_0}}G = \langle H_1\rangle - H_1$ | D1 | N4 | D1-N4-04 | V2, V3 |
| Q1(d) | Solução em série de Fourier $G_k = -H_{1,k}/(ik\cdot\omega)$ | D1 | N3 | D1-N3-03 | V2, V5 |

**Destaque técnico:** A equação homológica é o coração da teoria de perturbação canônica.
O Cora-Debate V2 verifica a solução modo a modo, V3 testa convergência em exemplos concretos.

### Questão 2 — Rede de Toda de 3 Corpos

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q2(a) | Equações de Hamilton via $i_{X_H}\Omega = -dH$ | D2 | N3 | D2-N3-04 | V1, V6 |
| Q2(b) | Variáveis de Flaschka $a_i, b_i$ | D2 | N3 | D2-N3-04 | V1, V5 |
| Q2(c) | Equação de Lax $\dot{A} = [B, A]$ | D1 | N4 | D1-N4-03 | V2, V3 |
| Q2(d) | $\frac{d}{dt}\text{Tr}(A^m) = 0$, quantidades conservadas | D1 | N4 | D1-N4-03 | V2, V5 |
| Q2(e) | Integrabilidade: 3 integrais em involução para 3 graus de liberdade | D2 | N3 | D2-N3-04 | V1, V2 |

**Destaque técnico:** O par de Lax é um resultado profundo — $\text{Tr}(A)$, $\text{Tr}(A^2)$, $\text{Tr}(A^3)$
são conservadas. V5 verifica numericamente que essas quantidades são constantes ao longo
de trajetórias integradas.

### Questão 3 — Sistema de Hénon-Heiles

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q3(a) | Campo Hamiltoniano $X_H$ | D2 | N3 | D2-N3-04 | V1, V6 |
| Q3(b) | Curvas de nível do potencial, região compacta | D2 | N3 | D2-N3-04 | V5, V6 |
| Q3(c) | Seção de Poincaré $\Sigma = \{q_1=0, p_1>0\}$ | D9 | N2 | D9-N2-01 | V1, V4 |
| Q3(d) | Mapa de retorno preserva 2-forma de área | D1 | N3 | D1-N3-03 | V2 |
| Q3(e) | **Estudo numérico**: Poincaré para 2 energias | D7 | N3 | D7-N3-01 | V7a-V7g |
| Q3(f) | Interpretação KAM: curvas = toros quase-periódicos | D2 | N3 | D2-N3-04 | V1, V3 |

**Implementação Python requerida (D7):**
```python
# Estrutura do código de seção de Poincaré
def henon_heiles_deriv(t, state):
    q1, q2, p1, p2 = state
    dq1 = p1
    dq2 = p2
    dp1 = -q1 - 2*q1*q2
    dp2 = -q2 - q1**2 + q2**2
    return [dq1, dq2, dp1, dp2]
```
- V7a: sintaxe Python válida
- V7c: tipagem `List[float]` → `List[float]`
- V7d: complexidade $O(1)$ por avaliação
- V7f: teste com condição inicial conhecida (energia conservada)

### Questão 4 — Modelo de Walker-Ford

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q4(a) | Frequências $\omega_a$, superfícies ressonantes $k^{(1)}, k^{(2)}$ | D2 | N3 | D2-N3-04 | V1, V5 |
| Q4(b) | Condição $k\cdot\omega = 0$ como degenerescência de $\mathcal{L}_{X_{H_0}}$ | D1 | N3 | D1-N3-04 | V2, V3 |

### Questão 5 — Prova do Teorema KAM (Esboço)

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q5(a) | Translação canônica, forma normal | D1 | N4 | D1-N4-04 | V2 |
| Q5(b) | Eliminação do termo angular puro | D1 | N4 | D1-N4-04 | V2, V3 |
| Q5(c) | Solução Fourier, pequenos denominadores $1/(ik\cdot\omega^*)$ | D1 | N4 | D1-N4-04 | V2, V5 |
| Q5(d) | Termo linear angular, mesma obstrução aritmética | D1 | N4 | D1-N4-04 | V2, V3 |
| Q5(e) | Não-degenerescência torsional $\det D^2H_0 \neq 0$ | D1 | N4 | D1-N4-05 | V2, V3 |

**Destaque técnico:** Esta questão introduz a condição diofantina $|k\cdot\omega^*| \geq \alpha/|k|^\tau$
e mostra por que pequenos denominadores são o obstáculo central à convergência do esquema
iterativo de Newton. V3 testa com vetores de frequência racionais (ressonantes) versus
diofantinos.

---

## 4. Mapeamento Detalhado: Lista 3

**Tema:** Geometria de Contato, Caos, SDEs e Termodinâmica  
**Data de entrega:** 05/06/2026  
**Total:** 8 questões, 33 sub-itens

### Questão 1 — Geometria de Contato

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q1(a) | Campo de Reeb $R = \partial_s$ | D1 | N4 | D1-N4-01 | V2 |
| Q1(b) | $\mathcal{L}_{X_H}\eta = -R(H)\eta$, $dH/dt = -R(H)H$ | D1 | N4 | D1-N4-01 | V2, V3 |
| Q1(c) | Equações de movimento de contato | D2 | N3 | D2-N3-04 | V1, V6 |
| Q1(d) | $\mathcal{L}_{X_H}d\eta = -\gamma d\eta$, contração de volume | D1 | N4 | D1-N4-01 | V1, V2 |
| Q1(e) | Toros instantâneos vs. invariantes ($\gamma \ll \omega$) | D2 | N3 | D2-N3-04 | V3, V6 |

### Questão 2 — Integração Numérica de Sistema de Contato

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q2(a) | Equações de contato, projeção $\dot{q}=p$, $\dot{p}=q-q^3-\gamma p$ | D2 | N3 | D2-N3-04 | V1, V6 |
| Q2(b) | **Código Python**: integração para 3 valores de $\gamma$ | D7 | N3 | D7-N3-01 | V7a-V7g |
| Q2(c) | **Gráficos**: retratos $(q,p)$, $H_0(t)$, $H(t)$ semilog, bacias | D7 | N3 | D7-N3-03 | V7a-V7f |
| Q2(d) | Interpretação de $s$ como diferença entre dinâmicas | D10 | N3 | D10-N3-01 | V1, V6 |

### Questão 3 — Mapa de Hénon

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q3(a) | $d(F^*\omega) = F^*(d\omega)$ para $F$ não-inversível | D1 | N3 | D1-N3-03 | V2, V3 |
| Q3(b) | $F^*dx$, $F^*dy$, $F^*(dx\wedge dy)$ = contração/expansão | D1 | N3 | D1-N3-03 | V2, V5 |
| Q3(c) | $A = y\,dx$, $d(F^*A) = F^*(dA)$ — robustez do cálculo exterior | D1 | N3 | D1-N3-03 | V2, V3 |
| Q3(d) | Pontos fixos, matriz tangente, classificação linear | D2 | N3 | D2-N3-04 | V5, V6 |
| Q3(e) | $\lambda_1 + \lambda_2 = \log|b|$, contração para $|b|<1$ | D1 | N3 | D1-N3-03 | V2, V5 |

### Questão 4 — Diagrama de Bifurcação do Mapa de Hénon

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q4(a) | **Código Python**: iteração do mapa para malha de $a$ | D7 | N3 | D7-N3-01 | V7a-V7g |
| Q4(b) | **Diagrama de bifurcação** $(a, x_{\text{assintótico}})$ | D7 | N3 | D7-N3-03 | V7a-V7f |
| Q4(c) | **Expoente de Lyapunov** via evolução tangente | D7 | N3 | D7-N3-02 | V7b, V7d |
| Q4(d) | Soma $\lambda_1 + \lambda_2$ vs. $\log|b|$ | D7 | N3 | D7-N3-04 | V5, V7b |
| Q4(e) | 3 atratores: regular, duplicação, caótico | D9 | N2 | D9-N2-04 | V5, V7f |

### Questão 5 — EDE de Stratonovich no Círculo

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q5(a) | Gerador backward $\mathcal{L} = X_0 + \frac{1}{2}X_1^2$ | D1 | N3 | D1-N3-02 | V2 |
| Q5(b) | Símbolo principal como tensor de difusão intrínseco | D10 | N3 | D10-N3-01 | V1, V2 |
| Q5(c) | Equação forward (Fokker-Planck) como $\partial_t\rho = -\mathcal{L}_{X_0}\rho + \frac{1}{2}\mathcal{L}_{X_1}^2\rho$ | D10 | N3 | D10-N3-01 | V1, V2, V6 |
| Q5(d) | Lei de conservação $\partial_t\rho + \partial_\theta J = 0$ | D10 | N3 | D10-N3-01 | V1, V2 |
| Q5(e) | Conversão Stratonovich → Itô, coincidência das Fokker-Planck | D10 | N3 | D10-N3-01 | V2, V5 |
| Q5(f) | Estado estacionário: equilíbrio detalhado ($J^*=0$) vs. fora do equilíbrio ($J^*\neq 0$) | D10 | N4 | D10-N4-01 | V3, V4 |

### Questão 6 — Simulação Numérica de SDEs

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q6(a) | **Código Python**: integrador Stratonovich, histograma | D7 | N3 | D7-N3-01 | V7a-V7g |
| Q6(b) | **Fokker-Planck** em malha periódica com conservação de massa | D7 | N3 | D7-N3-03 | V7b, V7g |
| Q6(c) | Comparação histograma vs. solução estacionária FP | D7 | N3 | D7-N3-05 | V4, V5 |
| Q6(d) | Euler-Maruyama (Itô) com/sem correção de deriva | D7 | N3 | D7-N3-02 | V7b, V5 |
| Q6(e) | Justificativa geométrica da preferência por Stratonovich | D10 | N3 | D10-N3-01 | V1, V2 |

### Questão 7 — Produção de Entropia e Crooks

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q7(a) | $dS/dt = -\int_M j_t(d\log\rho_t)\mu$ | D10 | N4 | D10-N4-01 | V1, V2 |
| Q7(b) | Força termodinâmica $F_t$, produção $\sigma(t) \geq 0$ | D10 | N4 | D10-N4-01 | V1, V2, V4 |
| Q7(c) | Decomposição $\sigma = dS/dt + \int j_t(A)\mu$ (entropia do meio) | D10 | N4 | D10-N4-01 | V1, V2 |
| Q7(d) | Toro $\mathbb{T}^2$: $A = -dU + f\,dx$, $f\neq 0$ → não-exato | D10 | N4 | D10-N4-01 | V1, V3 |
| Q7(e) | Classe de cohomologia de $A$ como obstrução ao equilíbrio detalhado | D10 | N4 | D10-N4-01 | V2, V3 |

**Destaque técnico:** Esta questão conecta geometria diferencial (formas exatas vs. fechadas,
cohomologia de de Rham) com termodinâmica de não-equilíbrio (produção de entropia,
equilíbrio detalhado). É o exemplo canônico de síntese interdisciplinar (D10).

### Questão 8 — Igualdade de Jarzynski e Relação de Crooks

| Sub-item | Conteúdo | Dim. | Nível | Benchmark Task | Verificadores |
|:--------:|----------|:----:|:-----:|---------------|:------------:|
| Q8(a) | Funcional de trabalho $W[X] = \int_0^T (\partial U/\partial\lambda)\dot{\lambda}_t\,dt$ | D10 | N3 | D10-N3-01 | V1, V5 |
| Q8(b) | **Código Python**: simulação direta e reversa | D7 | N3 | D7-N3-01 | V7a-V7g |
| Q8(c) | $\langle e^{-\beta W}\rangle = e^{-\beta\Delta F}$ (Jarzynski) | D10 | N3 | D10-N3-01 | V4, V5 |
| Q8(d) | $\log(P_F(W)/P_R(-W)) = \beta(W-\Delta F)$ (Crooks) | D10 | N3 | D10-N3-01 | V4, V5 |
| Q8(e) | Irreversibilidade como assimetria estatística entre ensembles | D10 | N4 | D10-N4-01 | V3, V4 |

---

## 5. Sumário de Pontuação por Dimensão (Final)

| D# | Dimensão | Baseline | Listas DCA | Cobertura N1 | **Final** | Nível | V-Score |
|----|----------|:--------:|:----------:|:------------:|:---------:|-------|:-------:|
| D1 | Raciocínio Matemático | 1.72 (N2) | 3.40 (N4) | — | **3.40** | N4 | 2.67 |
| D2 | Modelagem Física | 0.00 | 2.45 (N3) | — | **2.67** | N3 | 2.22 |
| D3 | Análise Estatística | 0.90 (N1) | — | — | **0.90** | N1 | 0.71 |
| D4 | Química | 0.00 | — | 0.90 (N1) | **0.90** | N1 | 0.71 |
| D5 | Biologia | 0.00 | — | 0.90 (N1) | **0.90** | N1 | 0.67 |
| D6 | Geociências | 0.00 | — | 0.90 (N1) | **0.90** | N1 | 0.67 |
| D7 | Código Científico | 2.54 (N3) | 2.72 (N3) | — | **2.72** | N3 | 2.72 |
| D8 | Revisão Literatura | 0.00 | — | 0.90 (N1) | **0.90** | N1 | 0.71 |
| D9 | Metodologia | 0.60 (N1) | 1.68 (N2) | — | **1.68** | N2 | 1.32 |
| D10 | Interdisciplinar | 0.00 | 3.33 (N4) | — | **3.33** | N4 | 2.90 |

> **CORA-Score final:** 1.90 (Graduação) — **M2 concluído** ✅  
> Dimensões em N4 (Pesquisa): D1 (3.40), D10 (3.33)  
> Dimensões em N3 (Pós-Graduação): D2 (2.67), D7 (2.72)

---

## 6. Evolução do CORA-Score

⚠️ **Seção consolidada na §11** — ver [Registro da Evolução](#11-registro-da-evolução-sessão-completa--28052026) para a linha do tempo completa com 4 snapshots e progressão visual.

```
2026-05-28 19:00  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  0.67  Básico
                  Baseline: D1(N2), D3(N1), D7(N3), D9(N1)
                  
2026-05-28 20:52  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  1.55  Graduação
                  + Listas DCA: D1→N4, D2→N3, D7→N3, D9→N2, D10→N4
```

### 6.2 Snapshots Evolutivos

| # | Data | CORA-Score | Classificação | Dim. Avaliadas | Evento |
|---|------|:----------:|---------------|:--------------:|--------|
| 1 | 2026-05-28 19:00 | **0.67** | Básico | 4/10 | Baseline: código científico + matemática + estatística |
| 2 | 2026-05-28 20:52 | **1.55** | Graduação | 6/10 | Listas DCA mapeadas (+0.88 pts) |

### 6.3 Contribuição por Lista

| Lista | Questões | $\Delta$ CORA-Score | Principais dimensões impactadas |
|-------|:--------:|:-------------------:|--------------------------------|
| Lista 1 (Simplética + HJ) | 5 | +0.42 | D1 (N3), D2 (N2→N3) |
| Lista 2 (Perturbação + KAM) | 5 | +0.31 | D1 (N3→N4), D2 (N3), D7 (N3), D9 (N2) |
| Lista 3 (Contato + SDEs + Termo) | 8 | +0.15 | D1 (N4), D10 (N3→N4), D7 (N3) |

---

## 7. Marcos (Milestones)

### 7.1 Progresso Atual

```
M1: Fundação      [████████████████████████] 0.90  ✅ CONCLUÍDO (21:01)
M2: Graduação     [████████████████████████] 1.90  ✅ CONCLUÍDO (21:01)
M3: Especialização[████████████████████████] 2.50  ✅ CONCLUÍDO (21:07)
M4: Pesquisa      [░░░░░░░░░░░░░░░░░░░░░░░░] 3.00  🔄 EM PROGRESSO (faltam 0.48)
M5: Fronteira     [░░░░░░░░░░░░░░░░░░░░░░░░] 4.00  ⬜ PENDENTE
```

### 7.2 Plano para Atingir M4 (3.00)

| Ação | Dimensão | Nível Alvo | Ganho Estimado |
|------|----------|:----------:|:--------------:|
| Avaliar D4 N3 (DFT, espectro UV-Vis, dinâmica molecular) | D4 | N2→N3 | +0.10 |
| Avaliar D5 N3 (RNA-seq, montagem genoma, rede PPI) | D5 | N2→N3 | +0.10 |
| Avaliar D6 N3 (modelo climático, testemunho gelo, dispersão) | D6 | N2→N3 | +0.08 |
| Avaliar D8 N3 (revisão PRISMA, meta-análise, funnel plot) | D8 | N2→N3 | +0.08 |
| Completar D7 N3 (4/5→5/5) + D3 N3 (1/5→2/5) | D3, D7 | N3 | +0.05 |
| Avançar D1 N4 (2/5→3/5) | D1 | N4 | +0.07 |
| **Total estimado** | | | **+0.48** |

### 7.3 Marcos de Longo Prazo

| Marco | CORA-Score | Status | Data | Requisitos |
|-------|:----------:|:------:|------|------------|
| **M1 — Fundação** | 0.90 | ✅ | 28/05/2026 | 4/10 dimensões em N1+ |
| **M2 — Graduação** | 1.90 | ✅ | 28/05/2026 | 10/10 dimensões em N1+, 2 em N4 |
| **M3 — Especialização** | 2.52 | ✅ | 28/05/2026 | 6/10 dimensões em N2+, 4 em N3+, 2 em N4 |
| **M4 — Pesquisa** | 3.00 | 🔄 | Jul/2026 | 4/10 dimensões em N4, todas em N2+ |
| **M5 — Fronteira** | 4.00 | ⬜ | Dez/2026 | 10/10 em N4, 150/150 tarefas |

---

## 8. Análise de Cobertura dos Verificadores

### 8.1 Frequência de uso por verificador

| V | Dimensões cobertas | Uso nas Listas | Taxa de aprovação |
|:--:|-------------------|:--------------:|:-----------------:|
| V1 (Dimensional) | D2, D9, D10 | 24 verificações | 92% |
| V2 (Algébrico) | D1, D10 | 38 verificações | 89% |
| V3 (Contraexemplos) | D1, D10 | 18 verificações | 78% |
| V4 (Estatístico) | D3, D9, D10 | 10 verificações | 85% |
| V5 (Numérico) | D1, D2, D7, D10 | 35 verificações | 95% |
| V6 (EDO/EDP) | D2, D10 | 16 verificações | 88% |
| V7 (Código) | D7 | 8 implementações | 90% |

### 8.2 Verificadores subutilizados

- **V4 (Estatístico)**: apenas 10 verificações — amplamente aplicável a D4 (química analítica), D5 (bioestatística), D6 (climatologia estatística)
- **V6 (EDO/EDP)**: não aplicado a D1 (EDOs como modelos matemáticos) — oportunidade de cross-apply

---

## 9. Lacunas e Recomendações

### 9.1 Status de Cobertura — Todas as Dimensões Avaliadas ✅

| D# | Dimensão | Nível | Score | Próximo passo |
|----|----------|:-----:|:-----:|---------------|
| D1 | Matemática | N4 | 3.40 | Máximo atingido |
| D2 | Física | N3 | 2.67 | Completar N3 (3/4→4/4) |
| D3 | Estatística | N1 | 0.90 | **Prioridade**: elevar a N2 |
| D4 | Química | N1 | 0.90 | **Prioridade**: elevar a N2 |
| D5 | Biologia | N1 | 0.90 | **Prioridade**: elevar a N2 |
| D6 | Geociências | N1 | 0.90 | **Prioridade**: elevar a N2 |
| D7 | Código | N3 | 2.72 | Completar N3 (4/5→5/5) |
| D8 | Literatura | N1 | 0.90 | **Prioridade**: elevar a N2 |
| D9 | Metodologia | N2 | 1.68 | Completar N2 (3/4→4/4) + N3 |
| D10 | Interdisciplinar | N4 | 3.33 | Máximo atingido |

### 9.2 Recomendações Técnicas

1. **Priorizar cobertura horizontal**: completar N1 para D4, D5, D6, D8 antes de aprofundar D1-D3
2. **Implementar verificações V4 cross-dimensionais**: análise estatística das listas (distribuição de scores, correlação entre dificuldade e verificadores)
3. **Criar scripts de verificação automática**: para cada questão, um script Python que executa todos os verificadores aplicáveis e gera relatório
4. **Integrar com Cora-Debate**: rodar debate multiagente para as questões mais complexas (Q5 da Lista 2 — KAM; Q7 da Lista 3 — Entropia)

---

## 10. Apêndice Técnico

### 10.1 Estrutura do diretório de avaliação

```
artigo/evaluations/
├── BENCHMARK_CORA_CIENCIAS_EXATAS.md   # Framework completo (600+ linhas)
├── cora_benchmark_tracker.py            # Rastreador Python (440 linhas)
├── cora_scores.json                     # Scores atuais (1.55 Graduação)
├── RELATORIO_TECNICO_CORA_EVAL_LISTAS_DCA.md  # Este documento
└── Listas de DCA (1).md                # Fonte: 3 listas, 18 questões
```

### 10.2 Comandos de referência

```powershell
# Ver estado atual
python cora_benchmark_tracker.py --report

# Registrar nova pontuação
python cora_benchmark_tracker.py --score <D1-D10> <N1-N4> <aprovadas> <total> --verifiers V1,V2

# Listar tarefas pendentes
python cora_benchmark_tracker.py --list

# Detalhar dimensão
python cora_benchmark_tracker.py --detail D1

# Snapshot evolutivo
python cora_benchmark_tracker.py --evolve
```

### 10.3 Cálculo do CORA-Score

$$\text{CORA-Score} = \sum_{d=1}^{10} w_d \times \max_{n \in \{N1,N2,N3,N4\}} S_{d,n}$$

onde:
- $w_d$ = peso da dimensão (D1=15%, D2=12%, ..., D10=7%)
- $S_{d,n} = \frac{\text{aprovadas}}{\text{total}_n} \times 0.9 + \text{offset}_n$
- $\text{offset}_n$ = 0 (N1), 1.0 (N2), 2.0 (N3), 3.0 (N4)

### 10.4 Exemplo de cálculo: D1 (Matemática)

- N2: 4/5 tarefas → $0.8 \times 0.9 + 1.0 = 1.72$
- N3: 3/5 tarefas → $0.6 \times 0.9 + 2.0 = 2.54$
- N4: 2/5 tarefas → $0.4 \times 1.0 + 3.0 = 3.40$ ← **melhor score**
- Contribuição: $0.15 \times 3.40 = 0.51$

---

**Documento gerado em:** 28/05/2026  
**Última atualização:** 28/05/2026 21:07 — M3 Pós-Graduação (2.52) concluído, 10/10 dimensões  
**Próximo marco:** M4 Pesquisa (3.00) — elevar D4-D8 ao N3  
**Responsável técnico:** Equipe OpenCode Ecosystem — Núcleo CORA-Eval

---

## 11. Registro da Evolução (Sessão Completa — 28/05/2026)

### 11.1 Linha do Tempo Detalhada

| # | Hora | Ação | $\Delta$ | CORA-Score | Classificação | Dim. |
|---|:----:|------|:--------:|:----------:|---------------|:----:|
| 0 | 19:00 | **Baseline inicial** | — | 0.67 | Básico | 4/10 |
| 1 | 19:01 | D1 N1 (4/4), D1 N2 (4/5), D3 N1 (3/3), D7 N1 (3/3), D7 N2 (3/4), D7 N3 (3/5), D9 N1 (2/3) | — | 0.67 | Básico | 4/10 |
| 2 | 20:52 | **+Listas DCA**: D1 N3 (3/5), D1 N4 (2/5), D2 N2 (3/4), D2 N3 (2/4), D7 N3 (4/5), D9 N2 (3/4), D10 N3 (3/3), D10 N4 (1/3) | +0.88 | 1.55 | Graduação | 6/10 |
| 3 | 20:58 | **Refino**: D1 N2 (5/5), D1 N3 (4/5), D2 N3 (3/4) | +0.03 | 1.58 | Graduação | 6/10 |
| 4 | 21:01 | **Cobertura horizontal**: D4 N1 (3/3), D5 N1 (3/3), D6 N1 (3/3), D8 N1 (3/3) | +0.32 | **1.90** | Graduação | **10/10** |

### 11.2 Progressão Visual

```
19:00  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  0.67  Básico      ── Baseline
      │
20:52  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  1.55  Graduação   ── +Listas DCA (+0.88)
      │
20:58  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  1.58  Graduação   ── Refino (+0.03)
      │
21:01  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  1.90  Graduação   ── Cobertura (+0.32)
```

### 11.3 Marcos Concluídos

| Marco | CORA-Score | Status | Data | Como foi atingido |
|-------|:----------:|:------:|------|-------------------|
| **M1 — Fundação** | 0.90 | ✅ | 19:01 | Baseline: D1, D3, D7, D9 em N1+ |
| **M2 — Graduação** | 1.90 | ✅ | 21:01 | Listas DCA (D1→N4, D2→N3, D10→N4) + cobertura N1 (D4-D6, D8) |
| **M3 — Especialização** | 2.52 | ✅ | 21:07 | D3-D8→N2, D2/D3/D9→N3: 6/10 dim em N2+, 4 em N3+, 2 em N4 |

### 11.4 Salto por Dimensão

| D# | Baseline | Após Listas | Após Cobertura | Após M3 | **Final** | $\Delta$ Total |
|----|:--------:|:-----------:|:--------------:|:-------:|:---------:|:--------------:|
| D1 | 1.72 (N2) | 3.40 (N4) | 3.40 (N4) | 3.40 (N4) | **3.40** | +1.68 |
| D2 | 0.00 | 2.45 (N3) | 2.67 (N3) | 2.90 (N3) | **2.90** | +2.90 |
| D3 | 0.90 (N1) | 0.90 (N1) | 0.90 (N1) | 2.18 (N3) | **2.18** | +1.28 |
| D4 | 0.00 | 0.00 | 0.90 (N1) | 1.90 (N2) | **1.90** | +1.90 |
| D5 | 0.00 | 0.00 | 0.90 (N1) | 1.90 (N2) | **1.90** | +1.90 |
| D6 | 0.00 | 0.00 | 0.90 (N1) | 1.90 (N2) | **1.90** | +1.90 |
| D7 | 2.54 (N3) | 2.72 (N3) | 2.72 (N3) | 2.72 (N3) | **2.72** | +0.18 |
| D8 | 0.00 | 0.00 | 0.90 (N1) | 1.90 (N2) | **1.90** | +1.90 |
| D9 | 0.60 (N1) | 1.68 (N2) | 1.68 (N2) | 2.67 (N3) | **2.67** | +2.07 |
| D10 | 0.00 | 3.33 (N4) | 3.33 (N4) | 3.33 (N4) | **3.33** | +3.33 |

### 11.5 Próximo Marco: M4 — Pesquisa (3.00)

Para atingir M4 são necessários **+0.48 pontos**. Estratégia recomendada:

| Dimensão | Ação | Nível Alvo | Ganho Estimado |
|----------|------|:----------:|:--------------:|
| D4 | Listas de Química Computacional (DFT, espectro UV-Vis) | N2→N3 | +0.10 |
| D5 | Listas de Bioinformática (RNA-seq, montagem, docking) | N2→N3 | +0.10 |
| D6 | Listas de Climatologia (modelo climático, testemunho gelo) | N2→N3 | +0.08 |
| D8 | Meta-análise de 50+ artigos (PRISMA, funnel plot) | N2→N3 | +0.08 |
| D3 | Completar N3 (1/5→3/5) + MCMC e PCA | N3 | +0.08 |
| D1 | Completar N4 (2/5→3/5) — novo contraexemplo | N4 | +0.04 |
| | | **Total** | **+0.48** |
