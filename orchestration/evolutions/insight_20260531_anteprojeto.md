# Evolução — Anteprojeto UFC: Compilação e Documentação

## Metadados
- **Timestamp**: 2026-05-31T22:00 (UTC-3)
- **Documento**: `manuscrito/main.tex` (anteprojeto PPGTE/UFC)
- **Tipo**: Compilação + documentação + fichamentos
- **Artefatos**: `main.pdf`, `anexo-fichamentos.tex`, `STATUS.md`

## O que foi feito

### Compilação completa do PDF
- Cadeia: pdflatex → bibtex → pdflatex × 2 (3 passagens)
- Resultado: 91 páginas, 499548 bytes, **0 erros de LaTeX**
- Warnings: 5 (referências + hyperref, todos resolvidos nas passagens seguintes)
- Underfull \hboxes: 3 (cosméticos, badness 7168/1755/1448)

### Fichamentos documentais
- Duas entradas adicionadas ao `anexo-fichamentos.tex`:
  - `docs/cotejo-citacoes-mh.md`: documentação formal do cotejo de citações
  - `STATUS.md`: relatório de status do projeto
- Estrutura: `\begin{fichamento}...\end{fichamento}` com campos Ref., Conceitos-chave, Descrição, Articulação

### Documentação de status
- `STATUS.md.zip` existia mas `STATUS.md` estava vazio
- Extraído e populado com 103 linhas de status completo do projeto
- Atualizado para refletir estado real (compilação concluída)

## Aprendizados

### Técnicos
1. **Pipeline pdflatex**: a cadeia pdflatex → bibtex → pdflatex × 2 é suficiente — não há necessidade de latex → dvips → ps2pdf
2. **"major issue" do MiKTeX**: não é erro de compilação, é notificação de atualizações pendentes do gerenciador de pacotes
3. **STATUS.md.zip**: documentação de estado pode estar compactada — verificar antes de assumir que está vazia
4. **Cotejo de citações**: 19 ocorrências de `\cite{LeaoXIV2026MH}`, 2 necessitaram edição com `[§XX]` — taxa de acerto de ~89% na citação direta

### Processo
5. **Fichamentos documentais** são análogos a bibliográficos mas referenciam artefatos do próprio projeto
6. **Manuscrito autônomo**: o projeto acadêmico não depende do ecossistema OpenCode para compilar — decisão arquitetural correta

## Recomendações
1. Executar revisão de redação dos capítulos antes da entrega
2. Verificar consistência dos fichamentos com o texto do manuscrito
3. Considerar executar `pdflatex` com `-synctex=1` para depuração mais rápida
4. Manter `STATUS.md` atualizado como documentação viva do projeto

## Assinatura
Gerado manualmente — Ciclo de compilação e documentação do anteprojeto UFC.
