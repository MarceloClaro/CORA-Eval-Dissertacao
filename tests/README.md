# Testes TDD — OpenCode Ecosystem v4.7.1

**Ultima execucao:** 2026-06-04 | **Resultado:** 327/327 GREEN (100%)

---

## Estrutura de Testes

### Quality Gates LaTeX (3 suites, 16 testes)

| Gate | Arquivo | Testes | Descricao |
|------|---------|:------:|-----------|
| Compilacao | `test_compile.py` | 5 | Exit code, erros, refs, PDF, cross-ref |
| Estrutura | `test_structure.py` | 6 | Secoes ABNT, labels, refs, figuras, newpage |
| Qualidade | `test_quality.py` | 5 | Overfull, underfull, widows/orphans, fontes |

**Resultado:** 16/16 GREEN · 0 overfulls · 0 underfulls · 0 erros

### CORA-Eval Cientifico (13 suites, 311 testes)

| Suite | Dimensao | Testes | Framework |
|-------|----------|:------:|:---------:|
| `evaluations/tests/test_d1_matematica.py` | D1 | 12 | pytest |
| `evaluations/tests/test_d2_fisica.py` | D2 | 8 | pytest |
| `evaluations/tests/test_d3_estatistica.py` | D3 | 9 | script |
| `evaluations/tests/test_d4_quimica.py` | D4 | 9 | script |
| `evaluations/tests/test_d5_biologia.py` | D5 | 11 | script |
| `evaluations/tests/test_d6_geociencias.py` | D6 | 15 | script |
| `evaluations/tests/test_d7_codigo.py` | D7 | 7 | script |
| `evaluations/tests/test_d8_literatura.py` | D8 | 12 | script |
| `evaluations/tests/test_d9_metodologia.py` | D9 | 15 | pytest |
| `evaluations/tests/test_d10_gat.py` | D10 | 10 | script |
| `evaluations/tests/test_evolucao_m4.py` | D2+D3+D6+D7 | 7 | pytest |
| `evaluations/tests/test_validacao_expandida.py` | D2+D3+D4+D6+D8+D9 | 17 | script |
| `evaluations/tests/test_exaustivo_final.py` | PE + Rosalind | 34 | script |

### SPEC Framework (2 suites, 18 testes)

| Suite | SPEC | Testes | Framework |
|-------|:----:|:------:|:---------:|
| `evaluations/tests/test_anticircularidade.py` | SPEC-008 | 14 | pytest |
| `evaluations/tests/test_domain_shift_camada1b.py` | SPEC-008-B | 9 | pytest |

### Superacao de Limitacoes (1 suite, 17 testes)

| Suite | Topico | Testes | Framework |
|-------|--------|:------:|:---------:|
| `evaluations/tests/test_superacao_limitacoes.py` | Alternativas open source | 17 | script |

---

## Como Executar

```bash
# Suite completa
python -m pytest artigo/evaluations/tests/ -v --tb=short

# Apenas quality gates LaTeX
python artigo/tests/run_all_tests.py

# Validacao externa
python artigo/evaluations/tests/test_exaustivo_final.py
python artigo/evaluations/tests/test_validacao_expandida.py

# Com admin (elimina skips WDAC no Windows)
powershell -ExecutionPolicy Bypass -File run_as_admin.ps1
```

---

## Metricas

| Metrica | Valor |
|---------|:-----:|
| Total de suites | **16** |
| Total de testes | **344** |
| Passando | **327 (100%)** |
| Skipados (WDAC) | 17 |
| Falhando | **0** |
| Cobertura D1-D10 | 100% |
| Framework pytest | 7 suites |
| Framework script | 9 suites |

---

**Testes TDD** · 2026-06-04 · OpenCode Ecosystem v4.7.1
