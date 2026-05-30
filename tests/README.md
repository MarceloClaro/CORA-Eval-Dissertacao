# TDD Test Suites — AutoEvolve LaTeX

## Visão Geral

Este diretório contém as 3 suites de teste TDD que compõem os **Quality Gates**
do pipeline SDD+TDD+AutoEvolve. Cada suite verifica uma dimensão diferente da
qualidade do documento LaTeX.

## Menu Adaptativo (recomendado)

O **painel central** para operar o ecossistema é o `menu.py`, que auto-descobre
todos os artefatos do projeto e constrói um menu dinâmico com 6 categorias.

```powershell
python menu.py
```

Modos disponíveis:

| Comando | Função |
|---------|--------|
| `python menu.py` | Menu interativo colorido com navegação numérica |
| `python menu.py <n>` | Executa diretamente a opção N (ex: `menu.py 3`) |
| `python menu.py --list` | Lista todos os artefatos descobertos |
| `python menu.py --quick` | Diagnóstico rápido (TDD + métricas) |

O menu se adapta automaticamente ao projeto: descobre arquivos `.tex`,
suites de teste, pipelines, backups, insights e comandos registrados
via `.menu_registry.json` (plugin system).

## Execução Direta (alternativa)

### Executar todas as suites
```powershell
python tests\run_all_tests.py
```
Compila o documento (2 passes), executa as 3 suites e gera relatório JSON.

### Executar uma suite individual
```powershell
python tests\test_compile.py
python tests\test_structure.py
python tests\test_quality.py
```
Cada suite retorna exit code 0 (PASS) ou 1 (FAIL) e exibe detalhes no stdout.

### Executar o pipeline completo com auto-fix
```powershell
python orchestration\refinement_loop.py
```
Executa SENSE→DIAGNOSE→FIX→VERIFY→EVOLVE→LEARN, com até 5 iterações.

## As 3 Suites

### 1. Compilation Gate (`test_compile.py`) — 5 testes
O documento **compila** e gera PDF válido.

| # | Teste | O que verifica |
|---|-------|----------------|
| 1.1 | `test_compilation_succeeds` | `pdflatex` retorna exit code 0 |
| 1.2 | `test_no_latex_errors` | Nenhuma linha `!` no log |
| 1.3 | `test_no_undefined_refs` | Nenhum `LaTeX Warning: ... undefined` |
| 1.4 | `test_pdf_generated` | PDF existe e > 100 KB |
| 1.5 | `test_no_rerun_warnings` | Cross-references finalizadas |

### 2. Structure Gate (`test_structure.py`) — 6 testes
O documento segue a **estrutura ABNT**.

| # | Teste | O que verifica |
|---|-------|----------------|
| 2.1 | `test_section_count` | 7 seções ABNT obrigatórias presentes |
| 2.2 | `test_fig_tab_labels` | 10 labels obrigatórios (fig+tabela) |
| 2.3 | `test_label_ref_balance` | Todo `\ref` tem `\label` correspondente |
| 2.4 | `test_no_manual_section_numbering` | Sem numeração manual (`\section{1. }`) |
| 2.5 | `test_figures_in_figuras_dir` | Arquivos de figura existem |
| 2.6 | `test_newpage_before_major_sections` | `\newpage` antes de seções principais |

### 3. Quality Gate (`test_quality.py`) — 5 testes
O documento tem **qualidade tipográfica**.

| # | Teste | Limite |
|---|-------|--------|
| 3.1 | `test_overfull_threshold` | Overfull < 12.0pt |
| 3.2 | `test_overfull_count` | ≤ 8 overfull boxes |
| 3.3 | `test_underfull_threshold` | Underfull badness < 10000 |
| 3.4 | `test_widow_orphan` | Sem widows/orphans |
| 3.5 | `test_font_warnings` | Sem font substitution warnings |

## Interpretação de Resultados

### Exit codes
- **0**: suite passou (todos os testes GREEN)
- **1**: suite falhou (um ou mais testes RED)

### Relatórios
O `run_all_tests.py` gera relatórios JSON em `tests/reports/`:
```json
{
  "timestamp": "20260528_101146",
  "document": "artigo_150_questoes.tex",
  "all_passed": true,
  "suites": {
    "test_compile": {"passed": true},
    "test_structure": {"passed": true},
    "test_quality": {"passed": true}
  }
}
```

## Adicionar Novos Testes

### 1. Dentro de uma suite existente
1. Escreva a função de teste (sem parâmetros, retorna `True`/`False`)
2. Adicione à lista `tests` no `main()` da suite
3. Atualize a docstring do arquivo com o novo critério

### 2. Nova suite de teste
1. Crie `tests/test_<nome>.py` seguindo o padrão das suites existentes
2. Adicione à lista `TEST_SUITES` em `tests/run_all_tests.py`
3. Atualize `SPEC_ORCHESTRATION.md` §4 com a nova gate
4. Atualize `FRAMEWORK.md` §4 com o novo critério formal

### Convenções
- Nome da função: `test_<descricao_curta>()`
- Print do resultado: `[TEST X.Y] Nome... PASS/FAIL`
- Exit code: `PASS = 0`, `FAIL = 1`
- Docstring: descrever condição RED (o que faz falhar)

## Dependências

### Runtime
- `pdflatex` (TeX Live 2023+) no PATH
- Python 3.10+

### LaTeX Packages (documento)
- `natbib`, `graphicx`, `hyperref`, `longtable`, `booktabs`, `float`

## Referências

| Documento | Localização |
|-----------|-------------|
| SPEC do pipeline | `orchestration/SPEC_ORCHESTRATION.md` |
| Framework conceitual | `orchestration/FRAMEWORK.md` |
| Orquestrador AutoEvolve | `orchestration/refinement_loop.py` |
| Runner TDD | `tests/run_all_tests.py` |
| Histórico de correções | `orchestration/fix_history.json` |
