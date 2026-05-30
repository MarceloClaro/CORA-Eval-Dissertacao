# PROMPT PARA NOTEBOOKLM — PODCAST CIENTIFICO CORA-Eval

## Instrucao Geral
Gere um podcast estilo "apresentacao de defesa academica" com dois hosts (um especialista em IA e um metodologista cientifico). Tom: rigoroso, transparente, sem exageros. Duracao alvo: 15-20 minutos. Idioma: Portugues Brasileiro formal. Publico-alvo: desenvolvedores e pesquisadores de IA.

---

## ROTEIRO SUGERIDO

### BLOCO 1 — Abertura e Contexto (3 min)
- Apresentar o problema central: como medir objetivamente a capacidade de raciocinio cientifico de sistemas multiagente de IA?
- Mencionar que benchmarks como MATH (12.500 problemas) e GSM8K (8.500) existem, mas medem apenas matematica/aritmetica isolada — nao capturam maturidade cientifica integrada.
- Introduzir o OpenCode Ecosystem: 79 agentes, 104 skills, 38 servidores MCP, 212 tipos de raciocinio, 7 verificadores simbolicos Cora-Debate (V1-V7).
- FRASE DE IMPACTO: "Como voce avalia se uma inteligencia artificial pensa como um cientista — e nao apenas como uma calculadora?"

### BLOCO 2 — O Metodo CORA-Eval (4 min)
- Explicar a triangulacao metodologica: verificacao simbolica + TDD + validacao externa.
- Descrever os 7 verificadores: V1 (dimensional), V2 (algebrico/SymPy), V3 (contraexemplos/Popper), V4 (estatistico), V5 (numerico), V6 (EDO/PDE), V7 (codigo-fonte).
- Explicar a estrutura: 10 dimensoes (Matematica, Fisica, Estatistica, Quimica, Biologia, Geociencias, Codigo Cientifico, Literatura, Metodologia, Sintese Interdisciplinar) × 4 niveis (Basico, Graduacao, Pos-Graduacao, Pesquisa) = 150 tarefas.
- Mencionar os 466 testes de calibracao com erros conhecidos injetados.
- Enfatizar a TRANSPARENCIA: todos os scores sao auto-reportados. O sistema documenta suas proprias limitacoes. Principio de Integridade: 8 raciocinios, 25 regras.

### BLOCO 3 — Resultados (4 min)
- CORA-Score bruto: 3,04 (nivel Pesquisa).
- CORA-Score ajustado: 2,59 (penalizando 8/10 dimensoes que so tem validacao interna).
- Validacao cega externa: 42/42 problemas (30 Project Euler + 12 Rosalind) — 100%. Verificacao automatica pelas plataformas, correto/erro binario, nao por revisores humanos.
- Bootstrap IC 95%: [2,65; 3,39], t = 198,6 contra H0: score = 2,50 (p < 0,001).
- Cross-validation K=10: CV = 2,2% (excelente).
- Calibracao dos 7 verificadores: F1 medio = 95,5% (466 testes).
- Vies de selecao documentado: r(ground truth disponivel, score) = 0,78.
- Nota estimada pelo perfil do revisor senior auto-simulado: 94/100.

### BLOCO 4 — 5 Ciclos de Critica Senior (3 min)
- Explicar que o relatorio passou por 5 ciclos de critica antes da publicacao.
- Ciclo 1: Numeros inflados — "125 agentes" corrigido para 79 verificaveis.
- Ciclo 2: Citacoes — 50 referencias com DOI CrossRef auditavel.
- Ciclo 3: Transparencia — todo score rotulado como [auto-reportado].
- Ciclo 4: Rastreabilidade — comandos exatos + seeds para reproducao.
- Ciclo 5: Separacao validacao externa vs interna — coluna [Ext/Int] em toda tabela.
- FRASE CHAVE: "O documento nao tenta convencer voce de que o sistema e perfeito. Ele tenta te dar todas as ferramentas para verificar cada afirmacao."

### BLOCO 5 — Limitacoes Declaradas (2 min)
- Este e um documento auto-publicado, sem revisao por pares externa.
- 8 das 10 dimensoes tem apenas validacao interna (Cora-Debate auto-verificando Cora-Debate).
- Reproducao por terceiros: pendente.
- Generalizacao para outros LLMs: nao testada.
- Vies de selecao de tarefas: documentado e quantificado.

### BLOCO 6 — Conclusao e Implicacoes (2 min)
- O ecossistema demonstrou capacidade de raciocinio avancado em benchmark proprio.
- A transparencia sobre limitacoes e parte integrante da contribuicao.
- Implicacoes para desenvolvedores: TDD + verificacao simbolica + transparencia como principios de engenharia para IA confiavel.
- Convite a comunidade: reproduzir, refutar, estender.
- Encerramento com os repositorios: github.com/MarceloClaro/OpenCode_Ecosystem e github.com/MarceloClaro/CORA-Eval-Dissertacao.

---

## FATOS E NUMEROS PARA O PODCAST

### Ecossistema
- 79 agentes (125 com definicoes distribuidas)
- 104 skills, 38 MCPs, 212 tipos de raciocinio
- 7 verificadores Cora-Debate (V1-V7)
- 17 iteracoes de desenvolvimento, score medio 93/100
- Autor: Marcelo Claro Laranjeira, Professor/Pedagogo, Prefeitura Municipal de Crateus, Ceara
- ORCID: 0000-0001-8996-2887

### CORA-Eval
- 150 tarefas, 10 dimensoes, 4 niveis
- CORA-Score: 3,04 bruto / 2,59 ajustado
- 42/42 validacao externa (100%)
- F1 medio: 95,5% (466 testes)
- 18 suites TDD, 113/114 testes GREEN
- 5 ciclos de critica, 15/15 CTs GREEN
- 50 referencias com DOI CrossRef

### Principio de Integridade
- 8 raciocinios: R-I1 a R-I8
- 25 regras em 5 faces: Analise, Producao, Documentacao, Comunicacao, Evolucao
- Regra fundamental: "Toda afirmacao deve ser verificavel."

---

## TOM E ESTILO

- Rigoroso mas acessivel — explique termos tecnicos na primeira mencao.
- Transparente — nunca omita limitacoes. Se algo e auto-reportado, DIGA que e auto-reportado.
- Sem hype — evite superlativos ("revolucionario", "incrivel", "estado da arte"). Prefira "demonstrou capacidade em", "os resultados sugerem que", "dentro das limitacoes documentadas".
- Dialogo natural entre os dois hosts — eles discordam respeitosamente em pontos de tensao (ex: "Mas isso nao e validacao externa de verdade, e so Project Euler...").
- Humanize com contexto brasileiro: mencione que o autor e professor da rede publica em Crateus, Ceara, desenvolvendo IA cientifica com recursos limitados.
- Termine com um call-to-action: links para os repositorios, convite para reproducao independente.
