# CORA-Eval: Benchmark Evolutivo para Ciências Exatas e da Natureza

## Níveis de Maturidade Científica

| Nível | Faixa | Classificação | Descrição |
|-------|-------|---------------|-----------|
| **N1** | 0.1 – 0.9 | **Básico** | Operações elementares, definições, raciocínio de passo único |
| **N2** | 1.0 – 1.9 | **Graduação** | Problemas multi-etapa, metodologias-padrão, nível livro-texto |
| **N3** | 2.0 – 2.9 | **Pós-Graduação** | Síntese de literatura, desenho experimental, modelagem avançada |
| **N4** | 3.0+ | **Pesquisa** | Contribuições originais, verificação formal de provas, problemas de fronteira |

---

## 1. Dimensões de Capacidade (11 dimensões × Cora V1-V7)

Cada dimensão é avaliada por benchmarks concretos nos 4 níveis. A pontuação da dimensão
é a média ponderada das tarefas resolvidas, com pesos proporcionais ao nível.

| # | Dimensão | Verificadores Cora | Peso |
|---|----------|-------------------|------|
| D1 | Raciocínio Matemático Formal | V2, V3, V6 | 14% |
| D2 | Modelagem de Sistemas Físicos | V1, V5, V6 | 11% |
| D3 | Análise Estatística e Inferência | V4, V5 | 11% |
| D4 | Química Computacional e Estrutural | V2, V5 | 9% |
| D5 | Biologia Molecular e Genômica | V4, V5 | 9% |
| D6 | Geociências e Modelagem Climática | V4, V5, V6 | 8% |
| D7 | Verificação de Código Científico | V7 (V7a-V7g) | 9% |
| D8 | Revisão Sistemática de Literatura | V3, V4 | 8% |
| D9 | Desenho Experimental e Metodologia | V1, V4 | 7% |
| D10 | Síntese Interdisciplinar | V1-V7 (todos) | 7% |
| D11 | Raciocínio de Longo Horizonte (DAG) | V1-V7 | 7% |

---

## 2. Benchmark Tarefas por Nível e Dimensão

### N1 — Básico (0.1 – 0.9)

#### D1: Raciocínio Matemático Formal
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D1-N1-01 | Resolver equação quadrática $ax^2+bx+c=0$ com coeficientes reais | Fórmula de Bhaskara correta, $\Delta$ calculado, raízes verificadas por substituição | V2 |
| D1-N1-02 | Verificar identidade trigonométrica $\sin^2\theta+\cos^2\theta=1$ | Expansão algébrica simbólica confirma igualdade | V2 |
| D1-N1-03 | Derivar polinômio $f(x)=x^3-2x^2+5x-1$ | $f'(x)=3x^2-4x+5$ verificado por SymPy | V2 |
| D1-N1-04 | Resolver sistema linear $2\times 2$ | Solução $(x,y)$ satisfaz ambas as equações | V2, V5 |

**Pontuação N1-D1** = (# tarefas aprovadas / 4) × 0.9

#### D2: Modelagem de Sistemas Físicos
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D2-N1-01 | Calcular velocidade final em queda livre: $v_f = \sqrt{2gh}$ | Análise dimensional: $[v] = LT^{-1}$, $[2gh] = L^2T^{-2} \rightarrow \surd$ consistente | V1 |
| D2-N1-02 | Verificar conservação de energia mecânica: $E_i = E_f$ | $mgh_1 + \frac{1}{2}mv_1^2 = mgh_2 + \frac{1}{2}mv_2^2$ numericamente | V5 |
| D2-N1-03 | Calcular força resultante $\vec{F}=m\vec{a}$ em 1D | Análise dimensional: $[F]=MLT^{-2}$ confere com $[ma]$ | V1 |

**Pontuação N1-D2** = (# tarefas aprovadas / 3) × 0.9

#### D3: Análise Estatística e Inferência
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D3-N1-01 | Calcular média e desvio-padrão de conjunto de dados (n ≤ 30) | $\bar{x}$ e $s$ corretos com 4 casas decimais | V5 |
| D3-N1-02 | Construir intervalo de confiança 95% para média | IC contém $\mu$ verdadeiro, margem de erro correta | V4, V5 |
| D3-N1-03 | Testar normalidade com histograma e QQ-plot | Shapiro-Wilk $p > 0.05$ onde apropriado | V4 |

**Pontuação N1-D3** = (# tarefas aprovadas / 3) × 0.9

#### D4: Química Computacional e Estrutural
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D4-N1-01 | Balancear equação química: $a\text{H}_2 + b\text{O}_2 \rightarrow c\text{H}_2\text{O}$ | Coeficientes estequiométricos: $(2,1,2)$ | V2 |
| D4-N1-02 | Calcular massa molar de $\text{C}_6\text{H}_{12}\text{O}_6$ | 180.156 g/mol (tolerância ±0.01) | V5 |
| D4-N1-03 | Converter concentração: %(m/v) $\leftrightarrow$ mol/L | Cálculo numérico com análise dimensional | V1, V5 |

**Pontuação N1-D4** = (# tarefas aprovadas / 3) × 0.9

#### D5: Biologia Molecular e Genômica
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D5-N1-01 | Transcrever DNA → RNA: `ATGCGT` → `AUGCGU` | Regras de pareamento corretas | V5 |
| D5-N1-02 | Traduzir códon → aminoácido: `AUG` → Metionina | Tabela de código genético padrão | V5 |
| D5-N1-03 | Calcular %GC de sequência: `ATGCGCAT` = ? | 50% (4/8 = G ou C) | V5 |

**Pontuação N1-D5** = (# tarefas aprovadas / 3) × 0.9

#### D6: Geociências e Modelagem Climática
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D6-N1-01 | Classificar rocha por composição: granito = ígnea intrusiva | Classificação correta do ciclo das rochas | V5 |
| D6-N1-02 | Converter escala de temperatura: °C $\leftrightarrow$ K $\leftrightarrow$ °F | $K = °C + 273.15$, $°F = 1.8°C + 32$ | V1, V5 |
| D6-N1-03 | Identificar camadas atmosféricas por altitude | Troposfera (0-12km), Estratosfera (12-50km) | V5 |

**Pontuação N1-D6** = (# tarefas aprovadas / 3) × 0.9

#### D7: Verificação de Código Científico
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D7-N1-01 | Validar sintaxe de função Python simples (`def quadrado(x): return x*x`) | V7a: AST válido, zero erros de sintaxe | V7a |
| D7-N1-02 | Verificar anotação de tipo: `def soma(a: int, b: int) -> int:` | V7c: consistência de tipos verificada | V7c |
| D7-N1-03 | Rodar suíte de teste unitário (≥3 casos) | V7f: cobertura ≥ 80% para função simples | V7f |

**Pontuação N1-D7** = (# tarefas aprovadas / 3) × 0.9

#### D8: Revisão Sistemática de Literatura
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D8-N1-01 | Extrair afirmação principal de artigo (resumo) | Afirmação extraída == afirmação do abstract | V3 |
| D8-N1-02 | Contar citações de autor em base (≥5 papers) | Contagem com precisão ≥ 90% | V5 |
| D8-N1-03 | Classificar artigo por área (Física/Química/Bio/Geo) | Classificação correta em ≥ 80% dos casos | V5 |

**Pontuação N1-D8** = (# tarefas aprovadas / 3) × 0.9

#### D9: Desenho Experimental e Metodologia
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D9-N1-01 | Identificar variável independente vs. dependente | Classificação correta em experimento descrito | V1 |
| D9-N1-02 | Calcular tamanho amostral mínimo: $n = (Z_{\alpha/2}\sigma/E)^2$ | Cálculo numérico correto | V5 |
| D9-N1-03 | Identificar grupo controle vs. experimental | Classificação correta | V1 |

**Pontuação N1-D9** = (# tarefas aprovadas / 3) × 0.9

#### D10: Síntese Interdisciplinar
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D10-N1-01 | Identificar intersecção: física + química = termodinâmica | Conexão correta entre disciplinas | V1-V5 |
| D10-N1-02 | Explicar fenômeno com 2+ disciplinas (ex: fotossíntese = bio+química+física) | Explicação correta multi-domínio | V1-V5 |

**Pontuação N1-D10** = (# tarefas aprovadas / 2) × 0.9

#### D11: Raciocínio de Longo Horizonte (DAG)
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D11-N1-01 | Propagar expressão booleana em DAG de 2 nós: NOT(AND(A,B)) | Resultado correto para todas as combinações de A,B | V2, V3 |
| D11-N1-02 | Avaliar árvore aritmética: ((3+5)×2)−4 | Resultado = 12, cada nó verificado | V2, V5 |
| D11-N1-03 | Executar cadeia de dependência linear: A→B→C | Tarefas executadas na ordem topológica correta | V3 |
| D11-N1-04 | Avaliar expressão em árvore sintática: (x>0)∧(y<10) | Resultado booleano correto para entradas de teste | V7 |
| D11-N1-05 | Converter unidades em cadeia: 5 km → m → cm | 500000 cm, cada conversão verificada | V1, V5 |

**Pontuação N1-D11** = (# tarefas aprovadas / 5) × 0.9

---

### N2 — Graduação (1.0 – 1.9)

#### D1: Raciocínio Matemático Formal
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D1-N2-01 | Provar convergência de série: $\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}$ | Prova por comparação com integral, verificação simbólica | V2, V3 |
| D1-N2-02 | Diagonalizar matriz $3\times 3$ simétrica | Autovalores e autovetores calculados, $PDP^{-1}=A$ | V2, V5 |
| D1-N2-03 | Resolver EDO de 2ª ordem: $y''+3y'+2y=0$ | Solução geral: $y=c_1e^{-x}+c_2e^{-2x}$, verificada | V6 |
| D1-N2-04 | Encontrar contraexemplo: "Todo número primo é ímpar" | $x=2$ é primo e par → contraexemplo | V3 |
| D1-N2-05 | Calcular integral definida: $\int_0^\pi \sin^2x\,dx = \pi/2$ | Verificação simbólica + numérica | V2, V5 |

**Pontuação N2-D1** = (# tarefas aprovadas / 5) × 0.9 + 1.0

#### D2: Modelagem de Sistemas Físicos
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D2-N2-01 | Resolver equação de Schrödinger para poço infinito 1D | $\psi_n(x)=\sqrt{2/L}\sin(n\pi x/L)$, $E_n=n^2\pi^2\hbar^2/(2mL^2)$ | V1, V6 |
| D2-N2-02 | Calcular campo elétrico de distribuição de cargas (Lei de Gauss) | $\oint\vec{E}\cdot d\vec{A}=Q_{enc}/\epsilon_0$, dimensionalmente OK | V1, V5 |
| D2-N2-03 | Modelar decaimento radioativo: $N(t)=N_0e^{-\lambda t}$ | Meia-vida $t_{1/2}=\ln 2/\lambda$, verificação numérica | V5, V6 |
| D2-N2-04 | Calcular momento de inércia de cilindro sólido | $I=\frac{1}{2}MR^2$, verificação dimensional | V1, V5 |

**Pontuação N2-D2** = (# tarefas aprovadas / 4) × 0.9 + 1.0

#### D3: Análise Estatística e Inferência
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D3-N2-01 | Executar teste t de duas amostras (independentes) | $t$-statistic, $p$-value, Cohen's $d$ calculados | V4 |
| D3-N2-02 | Realizar ANOVA one-way com 3 grupos | $F$-statistic, $\eta^2$, post-hoc Tukey | V4 |
| D3-N2-03 | Ajustar regressão linear: $y=\beta_0+\beta_1x+\epsilon$ | $R^2$, $\beta$ com IC 95%, resíduos normais (Shapiro-Wilk) | V4, V5 |
| D3-N2-04 | Calcular correlação de Pearson com bootstrap | $r$ com IC 95% via 10000 reamostragens | V4 |
| D3-N2-05 | Testar homocedasticidade (Breusch-Pagan ou Levene) | Diagnóstico correto de heterocedasticidade | V4 |

**Pontuação N2-D3** = (# tarefas aprovadas / 5) × 0.9 + 1.0

#### D4: Química Computacional e Estrutural
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D4-N2-01 | Calcular entalpia de reação: $\Delta H = \sum\Delta H_f^{\text{prod}} - \sum\Delta H_f^{\text{reag}}$ | Valor com sinal e magnitude corretos | V5 |
| D4-N2-02 | Prever geometria molecular (VSEPR): $\text{NH}_3$ = piramidal trigonal | Ângulos ~107°, hibridização $sp^3$ | V2, V5 |
| D4-N2-03 | Balancear reação redox em meio ácido | Semi-reações de oxidação e redução corretas | V2 |
| D4-N2-04 | Calcular pH de solução tampão (Henderson-Hasselbalch) | $\text{pH} = \text{p}K_a + \log([A^-]/[HA])$ | V5 |

**Pontuação N2-D4** = (# tarefas aprovadas / 4) × 0.9 + 1.0

#### D5: Biologia Molecular e Genômica
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D5-N2-01 | Analisar heredograma para padrão de herança | Autossômico dominante/recessivo, ligado ao X identificado | V3 |
| D5-N2-02 | Calcular frequências alélicas (Hardy-Weinberg) | $p^2+2pq+q^2=1$, equilíbrio testado com $\chi^2$ | V4, V5 |
| D5-N2-03 | Alinhar 2 sequências de DNA (Needleman-Wunsch) | Score de alinhamento e identidade calculados | V5 |
| D5-N2-04 | Construir árvore filogenética (UPGMA) com 5 taxa | Distância calculada, topologia correta | V5 |

**Pontuação N2-D5** = (# tarefas aprovadas / 4) × 0.9 + 1.0

#### D6: Geociências e Modelagem Climática
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D6-N2-01 | Interpretar diagrama de fases mineral (PT) | Fase estável identificada para $(P,T)$ dado | V5 |
| D6-N2-02 | Calcular balanço radiativo simples: $(1-\alpha)S/4 = \sigma T_e^4$ | $T_e$ calculado (~255K), efeito estufa quantificado | V1, V5 |
| D6-N2-03 | Analisar perfil de sondagem atmosférica | Inversão térmica, CAPE, nível de convecção livre | V5 |

**Pontuação N2-D6** = (# tarefas aprovadas / 3) × 0.9 + 1.0

#### D7: Verificação de Código Científico
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D7-N2-01 | Verificar implementação de Runge-Kutta 4ª ordem | Solução numérica de EDO com erro $O(h^4)$ | V7b, V7d |
| D7-N2-02 | Auditar segurança de script de análise de dados | V7e: zero vulnerabilidades OWASP (SQLi, XSS, path traversal) | V7e |
| D7-N2-03 | Verificar invariante de loop em algoritmo de ordenação | V7g: invariante mantido em todas as iterações | V7g |
| D7-N2-04 | Analisar complexidade de algoritmo recursivo: $T(n)=2T(n/2)+O(n)$ | V7d: $O(n\log n)$ confirmado | V7d |

**Pontuação N2-D7** = (# tarefas aprovadas / 4) × 0.9 + 1.0

#### D8: Revisão Sistemática de Literatura
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D8-N2-01 | Extrair metodologia de 5 artigos relacionados | Métodos extraídos corretamente (≥80% acurácia) | V3 |
| D8-N2-02 | Construir tabela de comparação: autor × método × resultado | Tabela com 5+ linhas, todas as células preenchidas corretamente | V3, V5 |
| D8-N2-03 | Identificar lacuna de pesquisa em corpo de 10 artigos | Lacuna identificada corresponde à apontada por revisores humanos | V3 |
| D8-N2-04 | Verificar consistência de citações: toda ref no texto está na bibliografia | Zero citações órfãs | V3 |

**Pontuação N2-D8** = (# tarefas aprovadas / 4) × 0.9 + 1.0

#### D9: Desenho Experimental e Metodologia
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D9-N2-01 | Projetar experimento fatorial $2^2$ com 3 réplicas | Blocagem, randomização, fatores e níveis corretos | V1, V4 |
| D9-N2-02 | Calcular poder estatístico: $1-\beta$ para teste t com $n$ e $d$ dados | Cálculo com G*Power ou scipy.stats | V4 |
| D9-N2-03 | Identificar vieses em desenho experimental | Viés de seleção, confundimento, efeito placebo detectados | V3 |
| D9-N2-04 | Validar instrumento de medição: incerteza e precisão | Propagação de erros calculada corretamente | V1, V5 |

**Pontuação N2-D9** = (# tarefas aprovadas / 4) × 0.9 + 1.0

#### D10: Síntese Interdisciplinar
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D10-N2-01 | Modelar sistema biofísico (ex: potencial de ação neuronal, Hodgkin-Huxley) | Equações diferenciais com parâmetros biológicos, verificação dimensional | V1, V6 |
| D10-N2-02 | Analisar problema com 3+ disciplinas (ex: mudança climática = física+química+geo+bio) | Cadeia causal multi-domínio correta | V1-V7 |
| D10-N2-03 | Resolver problema de físico-química (ex: equação de Arrhenius) | $k=Ae^{-E_a/(RT)}$, cálculo correto com unidades | V1, V5 |

**Pontuação N2-D10** = (# tarefas aprovadas / 3) × 0.9 + 1.0

#### D11: Raciocínio de Longo Horizonte (DAG)
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D11-N2-01 | Propagar implicação multi-nível: A→B→C→D | A=True ⇒ D=True, nós intermediários consistentes | V2, V3 |
| D11-N2-02 | Calcular expressão algébrica encadeada: x=3 → y=2x+1 → z=y²−x | z=46, propagação numérica correta | V2, V5 |
| D11-N2-03 | Alocar 3 tarefas com 2 recursos e precedências em DAG | Alocação factível respeitando todas as dependências | V3, V5 |
| D11-N2-04 | Simular fluxo condicional: if(A>0) then B=C else B=D | B correto para ambos os caminhos | V7 |
| D11-N2-05 | Propagar dados por pipeline de 4 estágios: input→process→validate→output | Saída do pipeline igual ao esperado | V5, V7 |
| D11-N2-06 | Avaliar função majoritária em DAG de 5 entradas | Resultado True se ≥3 entradas True | V2, V3 |
| D11-N2-07 | Executar operação matricial encadeada: A×B→C→det(C) | Determinante calculado corretamente | V2, V5 |

**Pontuação N2-D11** = (# tarefas aprovadas / 7) × 0.9 + 1.0

---

### N3 — Pós-Graduação (2.0 – 2.9)

#### D1: Raciocínio Matemático Formal
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D1-N3-01 | Provar teorema usando indução matemática | Passo base + passo indutivo verificados simbolicamente | V2, V3 |
| D1-N3-02 | Resolver sistema de equações diferenciais acopladas não-lineares | Solução analítica ou numérica com verificação de estabilidade | V6 |
| D1-N3-03 | Provar convergência de método numérico (ex: Newton-Raphson) | Critério de convergência $\|x_{n+1}-x_n\|<\epsilon$ demonstrado | V2, V5 |
| D1-N3-04 | Encontrar contraexemplo para conjectura de teoria dos grafos | Grafo com propriedade desejada construído e verificado | V3 |
| D1-N3-05 | Derivar solução de equação de onda 2D com condições de contorno | Separação de variáveis, harmônicos esféricos | V6 |

**Pontuação N3-D1** = (# tarefas aprovadas / 5) × 0.9 + 2.0

#### D2: Modelagem de Sistemas Físicos
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D2-N3-01 | Simular sistema de $N$ corpos com interação gravitacional | Conservação de energia com erro < $10^{-6}$ | V5, V7 |
| D2-N3-02 | Resolver equações de Navier-Stokes para fluxo laminar 2D | Perfil de velocidade parabólico, número de Reynolds | V6, V5 |
| D2-N3-03 | Calcular seção de choque de espalhamento quântico (Born) | $d\sigma/d\Omega = |f(\theta)|^2$, verificação dimensional | V1, V5 |
| D2-N3-04 | Modelar equação de difusão com fonte dependente do tempo | Solução analítica via função de Green | V6 |

**Pontuação N3-D2** = (# tarefas aprovadas / 4) × 0.9 + 2.0

#### D3: Análise Estatística e Inferência
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D3-N3-01 | Implementar MCMC (Metropolis-Hastings) para inferência Bayesiana | Cadeia converge, $\hat{R} < 1.1$, traço estacionário | V4, V5 |
| D3-N3-02 | Realizar análise de componentes principais (PCA) com validação cruzada | Variância explicada por componente, scree plot, loadings | V4 |
| D3-N3-03 | Ajustar modelo de efeitos mistos (random effects) | Estrutura de covariância, REML, AIC/BIC | V4 |
| D3-N3-04 | Corrigir múltiplas comparações (Bonferroni, FDR, Holm) | Taxa de descoberta falsa controlada em $\alpha=0.05$ | V4 |
| D3-N3-05 | Realizar análise de sobrevivência (Kaplan-Meier, Cox PH) | Curvas de sobrevivência, hazard ratio, log-rank test | V4 |

**Pontuação N3-D3** = (# tarefas aprovadas / 5) × 0.9 + 2.0

#### D4: Química Computacional e Estrutural
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D4-N3-01 | Otimizar geometria molecular com DFT (B3LYP/6-31G*) | Energia converge, gradiente < $10^{-4}$, frequências > 0 | V5 |
| D4-N3-02 | Calcular espectro UV-Vis via TD-DFT | $\lambda_{\max}$ com erro < 20nm do experimental | V5 |
| D4-N3-03 | Simular dinâmica molecular (NVT) de proteína pequena | RMSD estabiliza < 2Å, energia conservada | V5, V7 |
| D4-N3-04 | Prever mecanismo de reação orgânica (estado de transição) | Barreira de ativação calculada, intermediários identificados | V2, V5 |

**Pontuação N3-D4** = (# tarefas aprovadas / 4) × 0.9 + 2.0

#### D5: Biologia Molecular e Genômica
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D5-N3-01 | Realizar análise de expressão diferencial (RNA-seq, DESeq2/edgeR) | Genes diferencialmente expressos com FDR < 0.05 | V4 |
| D5-N3-02 | Montar genoma bacteriano a partir de reads Illumina (SPAdes) | N50 > 50kbp, cobertura > 30× | V5 |
| D5-N3-03 | Construir rede de interação proteína-proteína (STRING, Cytoscape) | Módulos funcionais identificados, enriquecimento GO | V4, V5 |
| D5-N3-04 | Realizar docking molecular (proteína-ligante) | Energia de ligação, pose com menor RMSD do cristalográfico | V5 |

**Pontuação N3-D5** = (# tarefas aprovadas / 4) × 0.9 + 2.0

#### D6: Geociências e Modelagem Climática
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D6-N3-01 | Rodar modelo climático simplificado (EBM 1D) | Perfil de temperatura latitudinal, albedo feedback | V6, V5 |
| D6-N3-02 | Analisar dados de testemunho de gelo ($\delta^{18}\text{O}$) | Reconstrução paleoclimática de temperatura | V4 |
| D6-N3-03 | Modelar dispersão de poluentes atmosféricos (Gaussiana) | Concentração em função da distância, direção do vento | V6 |

**Pontuação N3-D6** = (# tarefas aprovadas / 3) × 0.9 + 2.0

#### D7: Verificação de Código Científico
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D7-N3-01 | Verificar corretude de implementação de integrador simplético | V7b: tripla Hoare verificada, energia conservada | V7b, V7g |
| D7-N3-02 | Auditar segurança de pipeline de bioinformática | V7e: zero vulnerabilidades críticas (CWE-78, CWE-89, CWE-22) | V7e |
| D7-N3-03 | Verificar tipagem de biblioteca científica (TypeScript strict) | V7c: zero erros de tipo, genéricos corretos | V7c |
| D7-N3-04 | Provar complexidade assintótica de algoritmo paralelo | V7d: $O(n/p + \log p)$ confirmado para reduce | V7d |
| D7-N3-05 | Cobertura de testes para módulo de computação científica (≥95%) | V7f: cobertura de branches ≥ 95%, edge cases cobertos | V7f |

**Pontuação N3-D7** = (# tarefas aprovadas / 5) × 0.9 + 2.0

#### D8: Revisão Sistemática de Literatura
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D8-N3-01 | Conduzir revisão sistemática (PRISMA) com ≥50 artigos | Fluxograma PRISMA, viés de publicação (funnel plot) | V3, V4 |
| D8-N3-02 | Realizar meta-análise: efeito combinado com random effects | Forest plot, $I^2$ heterogeneidade, $p$-value combinado | V4 |
| D8-N3-03 | Extrair e sintetizar evidência quantitativa de 10+ artigos | Effect sizes extraídos, direção consistente | V3, V4 |
| D8-N3-04 | Identificar vieses de publicação com teste de Egger | Intercepto do funnel plot com IC | V4 |

**Pontuação N3-D8** = (# tarefas aprovadas / 4) × 0.9 + 2.0

#### D9: Desenho Experimental e Metodologia
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D9-N3-01 | Projetar experimento com delineamento em blocos casualizados (RCBD) | ANOVA com blocagem, $F$-test para tratamentos | V4 |
| D9-N3-02 | Calcular tamanho amostral para modelo multivariado | Poder ≥ 0.80, $\alpha=0.05$, número de preditores considerado | V4 |
| D9-N3-03 | Validar questionário: $\alpha$ de Cronbach, análise fatorial confirmatória | $\alpha > 0.70$, CFI > 0.90, RMSEA < 0.08 | V4 |
| D9-N3-04 | Simular dados para validação de método estatístico | Dados sintéticos com propriedades conhecidas, viés < 5% | V5, V7 |

**Pontuação N3-D9** = (# tarefas aprovadas / 4) × 0.9 + 2.0

#### D10: Síntese Interdisciplinar
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D10-N3-01 | Integrar modelo climático com modelo ecológico (feedback vegetação-clima) | Acoplamento bidirecional, variáveis de estado consistentes | V1, V6 |
| D10-N3-02 | Resolver problema de fronteira (ex: origem da vida = química+geo+física+bio) | Hipótese com suporte multi-domínio, previsões testáveis | V1-V7 |
| D10-N3-03 | Projetar material com propriedades específicas (ex: band gap ajustável) | DFT + termodinâmica, propriedade alvo dentro de 10% | V5, V7 |

**Pontuação N3-D10** = (# tarefas aprovadas / 3) × 0.9 + 2.0

#### D11: Raciocínio de Longo Horizonte (DAG)
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D11-N3-01 | Verificar SAT de DAG booleano de 8 nós com 3 entradas | Listar atribuições que satisfazem a expressão | V2, V3 |
| D11-N3-02 | Propagar composição aninhada: f(g(h(x))) com h(x)=x², g(y)=y+1, f(z)=√z | Valor final correto para múltiplas entradas | V2, V5 |
| D11-N3-03 | Resolver C-SP com 5 tarefas, 3 recursos, 4 precedências | Ordenação topológica respeitando restrições | V3, V5 |
| D11-N3-04 | Propagar parâmetros por 3 funções: normalizar→transformar→mapear | Saída correta em cada estágio do pipeline | V5, V7 |
| D11-N3-05 | Executar propagação de erro: nó folha → raiz via derivadas parciais | Erro propagado corretamente pela cadeia | V1, V5 |
| D11-N3-06 | Avaliar lógica com quantificadores: ∀x(P(x)→Q(x)) ∧ ∃xP(x) ⇒ ∃xQ(x) | Inferência válida, cadeia de propagação correta | V2, V3 |
| D11-N3-07 | Propagar parâmetros em modelo de 3 equações acopladas | Parâmetros consistentes em todos os nós | V1, V5, V6 |
| D11-N3-08 | Expandir DAG com feedback em sequência temporal de 4 passos | Expansão temporal correta, consistência mantida | V2, V3 |

**Pontuação N3-D11** = (# tarefas aprovadas / 8) × 0.9 + 2.0

---

### N4 — Pesquisa (3.0+)

#### D1: Raciocínio Matemático Formal
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D1-N4-01 | Verificar demonstração de teorema original (≥50 passos) | Cada passo logicamente válido, sem saltos ou erros | V2, V3 |
| D1-N4-02 | Gerar prova alternativa para teorema conhecido | Prova correta e estruturalmente diferente da original | V2, V3 |
| D1-N4-03 | Refutar conjectura com contraexemplo explícito | Contraexemplo verificado por todos os V ativos | V3 |
| D1-N4-04 | Provar limite assintótico de sequência definida recursivamente | Prova por indução ou squeeze theorem, $\epsilon$-$N$ formal | V2 |
| D1-N4-05 | Resolver problema de otimização não-convexa com garantia de otimalidade | Condições KKT, dualidade forte verificada | V2, V5 |

**Pontuação N4-D1** = (# tarefas aprovadas / 5) × 1.0 + 3.0

#### D2: Modelagem de Sistemas Físicos
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D2-N4-01 | Derivar nova solução analítica para EDP não-linear | Solução verifica equação + condições de contorno | V6 |
| D2-N4-02 | Simular sistema quântico de muitos corpos (≥10 partículas) | Entanglement entropy, ground state energy convergida | V5, V7 |
| D2-N4-03 | Modelar formação de estruturas cósmicas (dark matter halo) | Perfil NFW, função de massa de halos | V5, V6 |
| D2-N4-04 | Propor e validar modelo para fenômeno sem teoria estabelecida | Preditivo, falsificável, dimensionalmente consistente | V1, V3 |

**Pontuação N4-D2** = (# tarefas aprovadas / 4) × 1.0 + 3.0

#### D3: Análise Estatística e Inferência
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D3-N4-01 | Desenvolver novo estimador com propriedades demonstradas (consistência, eficiência) | Demonstração formal + simulação Monte Carlo | V4, V7 |
| D3-N4-02 | Implementar inferência variacional para modelo complexo (≥100 parâmetros) | ELBO converge, posterior aproximada vs MCMC benchmark | V4, V5 |
| D3-N4-03 | Realizar análise causal com DAGs e do-calculus (Pearl) | Efeito causal identificado, backdoor criterion satisfeito | V4 |
| D3-N4-04 | Desenvolver teste de hipótese para estrutura de dependência não-trivial | Poder e tamanho do teste validados via simulação | V4 |
| D3-N4-05 | Construir modelo hierárquico Bayesiano com dados reais multi-nível | Posterior preditiva, WAIC/LOO, convergência $\hat{R}$ | V4, V5 |

**Pontuação N4-D3** = (# tarefas aprovadas / 5) × 1.0 + 3.0

#### D4: Química Computacional e Estrutural
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D4-N4-01 | Prever estrutura cristalina de novo composto (CSP) | Estrutura ranqueada #1 entre preditas corresponde à experimental | V5 |
| D4-N4-02 | Projetar catalisador com propriedade-alvo (seletividade > 90%) | DFT + microkinetic modeling, TOF calculado | V5 |
| D4-N4-03 | Simular mecanismo enzimático completo (QM/MM) | Barreira de ativação, coordenada de reação, estado de transição | V5, V7 |

**Pontuação N4-D4** = (# tarefas aprovadas / 3) × 1.0 + 3.0

#### D5: Biologia Molecular e Genômica
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D5-N4-01 | Predizer estrutura 3D de proteína (homologia ou ab initio) | RMSD < 2Å do cristalográfico para ≥70% dos resíduos | V5 |
| D5-N4-02 | Realizar análise filogenômica com ≥100 genomas | Árvore de máxima verossimilhança, bootstrap ≥ 1000 | V4, V5 |
| D5-N4-03 | Identificar novo elemento regulatório em genoma | ChIP-seq + RNA-seq integrados, validação com repórter | V4 |

**Pontuação N4-D5** = (# tarefas aprovadas / 3) × 1.0 + 3.0

#### D6: Geociências e Modelagem Climática
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D6-N4-01 | Rodar ensemble de modelos climáticos (CMIP6-like) com cenários RCP | Projeção 2100 com intervalo de confiança, atribuição de forçantes | V4, V5 |
| D6-N4-02 | Modelar ciclo do carbono acoplado oceano-atmosfera | Fluxos de CO₂, acidificação oceânica, feedback loops | V6 |
| D6-N4-03 | Inverter dados sísmicos para imageamento de subsuperfície (FWI) | Modelo de velocidade com misfit < 5% dos dados observados | V5, V7 |

**Pontuação N4-D6** = (# tarefas aprovadas / 3) × 1.0 + 3.0

#### D7: Verificação de Código Científico
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D7-N4-01 | Provar corretude de biblioteca de álgebra linear (≥1000 LOC) | V7b: triplas Hoare para todas as funções públicas | V7b |
| D7-N4-02 | Verificar ausência de vulnerabilidades em código HPC (MPI/OpenMP) | V7e: race conditions, deadlocks, buffer overflows detectados | V7e, V7g |
| D7-N4-03 | Verificar implementação de Gradient Boosted Trees com invariantes | V7g: monotonicidade da loss, convergência do gradiente | V7g |
| D7-N4-04 | Cobertura de testes + boundary value analysis para código numérico | V7f: 100% branches, tolerância numérica documentada | V7f |
| D7-N4-05 | Verificar pipeline CI/CD de experimento científico (DVC + Git) | Reprodutibilidade: hash dos artefatos idêntico entre runs | V7a-V7f |

**Pontuação N4-D7** = (# tarefas aprovadas / 5) × 1.0 + 3.0

#### D8: Revisão Sistemática de Literatura
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D8-N4-01 | Conduzir meta-análise em rede (network meta-analysis) com ≥20 estudos | Ranking de tratamentos, inconsistência < 5%, SUCRA | V4 |
| D8-N4-02 | Realizar revisão de escopo (scoping review) cobrindo ≥200 artigos | Mapa de evidência com categorização taxonômica | V3 |
| D8-N4-03 | Sintetizar evidência contraditória de corpo literário (≥30 artigos) | Resolução de contradições, explicação de heterogeneidade | V3, V4 |
| D8-N4-04 | Identificar viés de publicação com métodos avançados (p-curve, selection models) | Diagnóstico de p-hacking, excesso de significância | V4 |

**Pontuação N4-D8** = (# tarefas aprovadas / 4) × 1.0 + 3.0

#### D9: Desenho Experimental e Metodologia
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D9-N4-01 | Projetar experimento adaptativo (adaptive design, Bayesian optimization) | Alocação sequencial ótima, critério de parada | V4, V7 |
| D9-N4-02 | Desenvolver protocolo experimental completo (replicável por terceiros) | Protocolo passo a passo, reagentes, equipamentos, análise | V1, V7 |
| D9-N4-03 | Realizar análise de sensibilidade global (Sobol, Morris, FAST) para modelo com ≥20 parâmetros | Índices de Sobol de 1ª ordem e totais | V5 |
| D9-N4-04 | Validar método de medição com padrão ouro (Bland-Altman) | Viés < 5%, limites de concordância dentro de ±1.96 SD | V4 |

**Pontuação N4-D9** = (# tarefas aprovadas / 4) × 1.0 + 3.0

#### D10: Síntese Interdisciplinar
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D10-N4-01 | Propor teoria unificadora conectando 3+ disciplinas | Hipótese testável com predições quantitativas | V1-V7 |
| D10-N4-02 | Resolver problema de fronteira interdisciplinar (ex: matéria escura ↔ biologia) | Framework teórico com suporte observacional/experimental | V1-V7 |
| D10-N4-03 | Construir gêmeo digital de sistema complexo (ex: célula, ecossistema, planeta) | Modelo multifísico acoplado, validação contra dados reais | V1, V5, V6, V7 |

**Pontuação N4-D10** = (# tarefas aprovadas / 3) × 1.0 + 3.0

#### D11: Raciocínio de Longo Horizonte (DAG)
| ID | Tarefa | Critério de Sucesso | V |
|----|--------|---------------------|---|
| D11-N4-01 | Verificar prova de 12 passos em DAG de regras de inferência | Todos os nós verificados, cadeia de implicação válida | V2, V3 |
| D11-N4-02 | Propagar predicados com quantificadores aninhados em DAG de 10 nós | Propagação ∀∃∀ corresponde ao esperado | V2, V3 |
| D11-N4-03 | Planejar 8 tarefas interdependentes com 4 deadlines | Cronograma factível, precedências e prazos cumpridos | V3, V5 |
| D11-N4-04 | Rastrear execução simbólica multi-módulo: A→B→C, 3 variáveis simbólicas | Saída simbólica correta, cada nó rastreável | V7 |
| D11-N4-05 | Propagar estado de sistema acoplado: EDO1→EDO2→EDO3 | Estado final correto, verificar propagação temporal | V1, V5, V6 |
| D11-N4-06 | Verificar DAG de 15 nós com 3 caminhos alternativos e 2 fusões | Todos os caminhos convergentes produzem mesmo resultado | V2, V3 |
| D11-N4-07 | Analisar sensibilidade em DAG: perturbar nó fonte, propagar a 5 dependentes | ∂saída/∂entrada correta em cada nó | V1, V5 |
| D11-N4-08 | Resolver DAG com 6 entidades e 10 restrições de integridade referencial | Todas as restrições satisfeitas, sem violações | V3, V5 |
| D11-N4-09 | Propagar distribuição de probabilidade por DAG de 8 nós (bayesiana) | Distribuição final correta, cada nó condicionado aos pais | V4, V5 |
| D11-N4-10 | Verificar DAG de otimização multi-objetivo: 4 objetivos, 6 variáveis, 3 restrições | Pareto-otimalidade verificada, trade-offs propagados | V2, V3, V5 |

**Pontuação N4-D11** = (# tarefas aprovadas / 10) × 1.0 + 3.0

---

## 3. Metodologia de Pontuação

### 3.1 Pontuação por Dimensão

Para cada dimensão $d$ e nível $n$, a pontuação bruta é:

$$S_{d,n} = \frac{\text{tarefas aprovadas em } n}{\text{total de tarefas em } n} \times 0.9 + \text{offset}(n)$$

onde $\text{offset}(n)$ é: N1=0, N2=1.0, N3=2.0, N4=3.0.

### 3.2 Pontuação Máxima por Dimensão

| Dimensão | N1 máx | N2 máx | N3 máx | N4 máx |
|----------|--------|--------|--------|--------|
| D1 | 0.9 | 1.9 | 2.9 | 4.0 |
| D2 | 0.9 | 1.9 | 2.9 | 4.0 |
| D3 | 0.9 | 1.9 | 2.9 | 4.0 |
| D4 | 0.9 | 1.9 | 2.9 | 4.0 |
| D5 | 0.9 | 1.9 | 2.9 | 4.0 |
| D6 | 0.9 | 1.9 | 2.9 | 4.0 |
| D7 | 0.9 | 1.9 | 2.9 | 4.0 |
| D8 | 0.9 | 1.9 | 2.9 | 4.0 |
| D9 | 0.9 | 1.9 | 2.9 | 4.0 |
| D10 | 0.9 | 1.9 | 2.9 | 4.0 |
| D11 | 0.9 | 1.9 | 2.9 | 4.0 |

### 3.3 Pontuação Global (CORA-Score)

A pontuação global é a soma ponderada do nível mais alto alcançado em cada dimensão:

$$\text{CORA-Score} = \sum_{d=1}^{11} w_d \times \max_{n \in \{N1,N2,N3,N4\}} S_{d,n}$$

onde $w_d$ são os pesos da tabela de dimensões (§1).

**Interpretação**:

| CORA-Score | Classificação | Significado |
|-----------|---------------|-------------|
| 0.1 – 0.9 | **Básico** | Resolve problemas de passo único, definições, cálculos elementares |
| 1.0 – 1.9 | **Graduação** | Metodologias-padrão, problemas multi-etapa, nível livro-texto |
| 2.0 – 2.9 | **Pós-Graduação** | Síntese de literatura, modelagem avançada, desenho experimental |
| 3.0 – 4.0 | **Pesquisa** | Contribuições originais, provas formais, problemas de fronteira |

### 3.4 Score com Cora Verificadores (CORA-V-Score)

Para cada tarefa, registra-se quais verificadores V1-V7 foram ativados e aprovaram:

$$\text{CORA-V-Score}_d = S_d \times \left(0.7 + 0.3 \times \frac{\sum \text{verificadores aprovados}}{7}\right)$$

Isso recompensa tarefas que passam por mais verificadores (maior rigor).

---

## 4. Estrutura de Rastreamento Evolutivo

### 4.1 JSON Schema

```json
{
  "ecosystem": "OpenCode",
  "version": "1.0.0",
  "last_evaluation": "2026-05-28",
  "cora_score": 2.45,
  "classification": "Pós-Graduação",
  "dimensions": {
    "D1": {"score": 2.9, "level": "N3", "tasks_passed": 5, "total_tasks": 5, "verifiers_active": ["V2","V3","V6"]},
    "D2": {"score": 1.9, "level": "N2", "tasks_passed": 4, "total_tasks": 4, "verifiers_active": ["V1","V5","V6"]},
    ...
  },
  "evolution": [
    {"date": "2026-05-28", "cora_score": 0.85, "classification": "Básico"},
    {"date": "2026-06-15", "cora_score": 1.72, "classification": "Graduação"},
    ...
  ],
  "verifier_coverage": {
    "V1": {"dimensions": ["D2","D4","D9","D10"], "approval_rate": 0.85},
    "V2": {"dimensions": ["D1","D4"], "approval_rate": 0.92},
    ...
  }
}
```

### 4.2 Periodicidade Recomendada

| Evento | Ação |
|--------|------|
| **A cada evolução do ecossistema** | Registrar CORA-Score corrente |
| **Após novo Cora V-verifier** | Reavaliar dimensões impactadas pelo verificador |
| **Mensalmente** | Rodar benchmark completo, registrar tendências |
| **Antes de publicação** | Auditar trilha evolutiva completa |

---

## 5. Integração com Cora-Debate

### 5.1 Mapeamento Verificador → Dimensão Científica

| Verificador | Dimensões primárias | Tipo de raciocínio científico |
|-------------|-------------------|-------------------------------|
| **V1** (Dimensional) | D2, D4, D9, D10 | Consistência de unidades em equações físicas/químicas |
| **V2** (Algébrico) | D1, D4 | Manipulação simbólica, provas algébricas |
| **V3** (Contraexemplos) | D1, D8, D9 | Falseabilidade, teste de hipóteses |
| **V4** (Estatístico) | D3, D5, D6, D8, D9 | Significância, tamanho de efeito, inferência |
| **V5** (Numérico) | D1-D10 (todos) | Precisão computacional, tolerância |
| **V6** (PDE/EDO) | D1, D2, D6, D10 | Modelagem de sistemas dinâmicos |
| **V7** (Código) | D7, D3, D5, D8 | Reprodutibilidade, corretude de software científico |

### 5.2 Q-Score UCB1 para Seleção de Tarefas

O algoritmo Q-Score UCB1 seleciona quais tarefas de benchmark priorizar em cada evolução:

$$Q_{\text{tarefa}} = \bar{r}_{\text{tarefa}} + \sqrt{\frac{2\ln N_{\text{total}}}{n_{\text{tarefa}}}}$$

- $\bar{r}_{\text{tarefa}}$ = taxa histórica de aprovação (balanceia exploração)
- $N_{\text{total}}$ = total de avaliações realizadas
- $n_{\text{tarefa}}$ = vezes que a tarefa foi avaliada
- Tarefas com $n=0$ têm prioridade máxima (exploração pura)

### 5.3 Self-Consistency para Benchmark (K=7)

Tarefas ambíguas (ex: D10, síntese interdisciplinar) são avaliadas K=7 vezes com
diferentes sementes de debatedores Cora. A resposta final é a moda ponderada pelo Q-Score.

---

## 6. Calibração e Validação do Benchmark

### 6.1 Ground Truth

Cada tarefa de benchmark possui:
- **Resposta canônica**: solução aceita pela comunidade científica
- **Fontes**: referência a livro-texto ou artigo onde a resposta é estabelecida
- **Métrica de tolerância**: margem de erro aceitável (ex: ±1% para cálculos numéricos)

### 6.2 Calibração Platt da Confiança do Cora

Para cada nível, calibra-se a confiança reportada pelo Cora contra a taxa real de acerto:

$$\hat{p}_{\text{calibrada}} = \sigma(a \cdot \logit(p_{\text{raw}}) + b)$$

com ECE (Expected Calibration Error) ≤ 0.10.

### 6.3 Validação com Especialistas Humanos

| Nível | Amostra de validação | Concordância esperada |
|-------|---------------------|----------------------|
| N1 | 10 avaliadores (graduandos) | ≥ 95% |
| N2 | 5 avaliadores (mestrandos) | ≥ 90% |
| N3 | 3 avaliadores (doutorandos) | ≥ 85% |
| N4 | 2 avaliadores (PhD, pós-doutores) | ≥ 80% |

---

## 7. Tabela Resumo: Total de Tarefas

| Dimensão | N1 | N2 | N3 | N4 | Total |
|----------|----|----|----|----|-------|
| D1 — Matemática | 4 | 5 | 5 | 5 | 19 |
| D2 — Física | 3 | 4 | 4 | 4 | 15 |
| D3 — Estatística | 3 | 5 | 5 | 5 | 18 |
| D4 — Química | 3 | 4 | 4 | 3 | 14 |
| D5 — Biologia | 3 | 4 | 4 | 3 | 14 |
| D6 — Geociências | 3 | 3 | 3 | 3 | 12 |
| D7 — Código Científico | 3 | 4 | 5 | 5 | 17 |
| D8 — Literatura | 3 | 4 | 4 | 4 | 15 |
| D9 — Metodologia | 3 | 4 | 4 | 4 | 15 |
| D10 — Interdisciplinar | 2 | 3 | 3 | 3 | 11 |
| D11 — Longo Horizonte (DAG) | 5 | 7 | 8 | 10 | 30 |
| **Total** | **35** | **47** | **49** | **49** | **180** |

---

## 8. Roadmap Evolutivo

| Marco | CORA-Score alvo | Prazo estimado | Entregáveis |
|-------|----------------|----------------|-------------|
| **M1: Fundação** | 0.9 (Básico) | Sprints 1-2 | 30/30 N1 aprovado |
| **M2: Graduação** | 1.9 (Graduação) | Sprints 3-6 | 40/40 N2 aprovado |
| **M3: Especialização** | 2.5 (Pós-Grad) | Sprints 7-12 | 30/41 N3 aprovado |
| **M4: Pesquisa** | 3.0 (Pesquisa) | Sprints 13-24 | 20/39 N4 aprovado |
| **M5: Fronteira** | 4.0 (Excelência) | Sprints 25-36 | 39/39 N4 aprovado |

---

## 9. Referências

- `BENCHMARK_CORA_CIENCIAS_EXATAS.md` — este documento
- `cora_benchmark_tracker.py` — rastreador de pontuação evolutiva
- `cora_scores.json` — registro histórico de pontuações
- `skills/cora-debate/SKILL.md` — especificação completa do Cora-Debate
- `skills/cora-debate/references/verifier_specs.md` — especificação dos V1-V7
- `skills/cora-debate/references/qscore_algorithm.md` — algoritmo Q-Score UCB1
