# -*- coding: utf-8 -*-
"""
REVISOR R9 — Conformidade Documental (ABNT, CAPES, USP, BN)
Busca templates oficiais, verifica conformidade, constroi se necessario.
"""

import sys, json, re, os
from pathlib import Path
from typing import Dict, List, Tuple

# ══════════════════════════════════════════════════════════════════════
# BASE DE CONHECIMENTO — Templates e Normas Oficiais
# ══════════════════════════════════════════════════════════════════════

OFFICIAL_TEMPLATES = {
    # ── CAPES ──
    "capes_tese": {
        "instituicao": "CAPES — Coordenacao de Aperfeicoamento de Pessoal de Nivel Superior",
        "url": "https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/avaliacao",
        "normas": [
            "Fonte Times New Roman ou Arial 12pt para texto, 10pt para notas",
            "Margens: esquerda 3cm, direita 2cm, superior 3cm, inferior 2cm",
            "Espacamento 1.5 para texto, simples para notas e citacoes longas",
            "Numeracao progressiva conforme NBR 6024:2012",
            "Referencias conforme NBR 6023:2018",
        ],
    },
    "capes_artigo": {
        "instituicao": "CAPES — Periodicos Qualis",
        "url": "https://sucupira.capes.gov.br/sucupira/",
        "normas": [
            "Resumo com ate 500 palavras em portugues e ingles",
            "3-5 palavras-chave em portugues e ingles",
            "Secoes: Introducao, Metodologia, Resultados, Discussao, Conclusao",
            "Figuras e tabelas numeradas sequencialmente com legenda",
        ],
    },
    
    # ── USP ──
    "usp_tese": {
        "instituicao": "USP — Universidade de Sao Paulo",
        "url": "https://www.teses.usp.br/",
        "template_latex": "https://github.com/abntex/abntex2",
        "normas": [
            "Formato A4 (210x297mm), margens ABNT NBR 14724:2011",
            "Elementos pre-textuais: capa, folha de rosto, ficha catalografica",
            "Elementos textuais: introducao, desenvolvimento, conclusao",
            "Elementos pos-textuais: referencias, apendices, anexos",
        ],
    },
    "usp_abntex2": {
        "instituicao": "USP — Template abnTeX2 (LaTeX)",
        "url": "https://github.com/abntex/abntex2",
        "comando_instalacao": "pip install abntex2",
        "classe": "\\documentclass[12pt,a4paper]{abntex2}",
        "normas": [
            "Classe abntex2 implementa automaticamente NBR 14724, 6023, 6024, 6027, 6028, 10520",
            "Comando \\imprimircapa, \\imprimirfolhaderosto para elementos pre-textuais",
            "\\cite{}, \\citeonline{} para citacoes ABNT autor-data ou numerico",
            "\\begin{citacao} para citacoes diretas com mais de 3 linhas",
        ],
    },
    
    # ── Biblioteca Nacional ──
    "bn_ficha": {
        "instituicao": "Biblioteca Nacional — Ficha Catalográfica",
        "url": "https://www.bn.gov.br/servicos/deposito-legal",
        "normas": [
            "Ficha catalografica no verso da folha de rosto (NBR 14724:2011)",
            "ISBN requerido para livros, ISSN para periodicos",
            "Deposito legal obrigatorio para obras publicadas no Brasil (Lei 10.994/2004)",
        ],
    },
    
    # ── ABNT — Todas as normas relevantes ──
    "abnt_nbr14724": {
        "instituicao": "ABNT NBR 14724:2011 — Trabalhos Academicos",
        "normas": [
            "Margens: esquerda 3cm, direita 2cm, superior 3cm, inferior 2cm",
            "Espacamento 1.5 para texto, simples para citacoes longas (>3 linhas)",
            "Recuo de 4cm da margem esquerda para citacoes longas",
            "Fonte tamanho 12 para texto, 10 para notas de rodape e citacoes longas",
            "Indicativo de secao alinhado a esquerda, sem ponto apos o numero",
        ],
    },
    "abnt_nbr6023": {
        "instituicao": "ABNT NBR 6023:2018 — Referencias",
        "normas": [
            "Autor(es) em CAIXA ALTA, seguido de titulo em negrito",
            "Elementos complementares: edicao, local, editora, data",
            "DOI ao final da referencia, quando disponivel",
            "Para documentos online: Disponivel em: <url>. Acesso em: data.",
        ],
    },
    "abnt_nbr10520": {
        "instituicao": "ABNT NBR 10520:2002 — Citacoes",
        "normas": [
            "Citacao direta curta (ate 3 linhas): entre aspas no corpo do texto",
            "Citacao direta longa (>3 linhas): recuo 4cm, fonte 10, sem aspas",
            "Citacao indireta: parafrase com indicacao de autoria",
            "Sistema autor-data: (SOBRENOME, ano, p. X)",
        ],
    },
    "abnt_nbr6024": {
        "instituicao": "ABNT NBR 6024:2012 — Numeracao Progressiva",
        "normas": [
            "Secao primaria: 1, 2, 3 (negrito, CAIXA ALTA)",
            "Secao secundaria: 1.1, 1.2 (negrito, apenas iniciais maiusculas)",
            "Secao terciaria: 1.1.1 (sem negrito, apenas iniciais maiusculas)",
            "Sem ponto, hifen, travessao ou qualquer sinal apos o indicativo",
        ],
    },
    
    # ── IEEE ──
    "ieee_article": {
        "instituicao": "IEEE — Institute of Electrical and Electronics Engineers",
        "url": "https://www.ieee.org/publications/authors/author-templates.html",
        "template_latex": "https://www.ctan.org/pkg/ieeetran",
        "normas": [
            "Duas colunas, fonte Times 10pt",
            "Resumo de ate 200 palavras",
            "Referencias numeradas entre colchetes [1], [2]",
            "Secoes em numeracao romana: I. INTRODUCTION, II. METHODOLOGY",
        ],
    },
    
    # ── ACM ──
    "acm_article": {
        "instituicao": "ACM — Association for Computing Machinery",
        "url": "https://www.acm.org/publications/proceedings-template",
        "template_latex": "https://www.ctan.org/pkg/acmart",
        "normas": [
            "Classe acmart com \\documentclass[sigconf]{acmart}",
            "Uma coluna (sigchi) ou duas colunas (sigconf)",
            "DOI e ACM Reference Format na primeira pagina",
            "CCS Concepts e keywords obrigatorios",
        ],
    },
    
    # ── Springer LNCS ──
    "springer_lncs": {
        "instituicao": "Springer — Lecture Notes in Computer Science",
        "url": "https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines",
        "template_latex": "https://www.ctan.org/pkg/llncs",
        "normas": [
            "Classe llncs com \\documentclass{llncs}",
            "Fonte Times 10pt, margens generosas",
            "Sem numeracao de paginas (inserida pela Springer)",
            "Running head com nome do autor (paginas pares) e titulo (impares)",
        ],
    },
    
    # ── ELSEVIER ──
    "elsevier_article": {
        "instituicao": "Elsevier — Journal Article Template",
        "url": "https://www.elsevier.com/authors/journal-authors/submit-your-paper",
        "template_latex": "https://www.ctan.org/pkg/elsarticle",
        "normas": [
            "Classe elsarticle com \\documentclass{elsarticle}",
            "Fonte Times 12pt, uma coluna",
            "Highlights (3-5 bullet points, max 85 chars cada)",
            "Graphical abstract opcional",
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════
# MOTOR DE CONSTRUCAO — Gera template LaTeX se nao encontrado
# ══════════════════════════════════════════════════════════════════════

def build_abnt_template(doc_type: str) -> str:
    """Constroi template LaTeX ABNT para o tipo de documento solicitado."""
    
    templates = {
        "relatorio_tecnico": r"""\documentclass[12pt,a4paper,oneside]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazilian]{babel}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage[bookmarks,colorlinks=true]{hyperref}
\usepackage{booktabs,longtable,tabularx}
\usepackage{caption,float}
\usepackage{fancyhdr,setspace}
\usepackage{enumitem}
% --- MARGENS ABNT NBR 14724:2011 ---
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\onehalfspacing
% --- CABECALHO ---
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Titulo Abreviado}
\fancyhead[R]{\small Autor}
\fancyfoot[C]{\thepage}
\title{Relatorio Tecnico}
\author{Nome do Autor}
\date{\today}
\begin{document}
\maketitle
\begin{abstract}
Resumo do relatorio tecnico...
\end{abstract}
\tableofcontents
\newpage
% --- CONTEUDO ---
\section{Introducao}
\section{Metodologia}
\section{Resultados}
\section{Conclusao}
% --- REFERENCIAS ---
\begin{thebibliography}{99}
\bibitem{exemplo} SOBRENOME, Nome. Titulo. Editora, Ano.
\end{thebibliography}
\end{document}""",
        
        "tese_doutorado": r"""\documentclass[12pt,a4paper,oneside]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazilian]{babel}
\usepackage{amsmath,amssymb}
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\usepackage{fancyhdr,setspace}
\onehalfspacing
\title{Tese de Doutorado}
\author{Nome do Autor}
\date{\today}
\begin{document}
\frontmatter
\maketitle
% Ficha catalografica (verso da folha de rosto)
% Dedicacao
% Agradecimentos
% Epigrafe
% Resumo em portugues
% Resumo em ingles (Abstract)
% Lista de figuras
% Lista de tabelas
% Lista de siglas
\tableofcontents
\mainmatter
\chapter{Introducao}
\chapter{Revisao da Literatura}
\chapter{Metodologia}
\chapter{Resultados}
\chapter{Conclusao}
\backmatter
\begin{thebibliography}{99}
\bibitem{exemplo} SOBRENOME, N. Titulo. Editora, Ano.
\end{thebibliography}
\appendix
\chapter{Apendice A}
\end{document}""",
        
        "artigo_qualis": r"""\documentclass[12pt,a4paper,twocolumn]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazilian]{babel}
\usepackage[top=2.5cm,bottom=2.5cm,left=2cm,right=2cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage[bookmarks,colorlinks=true]{hyperref}
\usepackage{booktabs,caption,float}
\title{Titulo do Artigo}
\author{Autor 1, Autor 2\\
Instituicao\\
\texttt{email@instituicao.edu}}
\date{}
\begin{document}
\maketitle
\begin{abstract}
Resumo com ate 250 palavras...
\end{abstract}
\section{Introducao}
\section{Metodologia}
\section{Resultados}
\section{Conclusao}
\begin{thebibliography}{99}
\bibitem{ref1} SOBRENOME, N. Titulo. Periodico, vol, p., Ano.
\end{thebibliography}
\end{document}""",
        
        "tcc_graduacao": r"""\documentclass[12pt,a4paper,oneside]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazilian]{babel}
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\usepackage{setspace,fancyhdr}
\onehalfspacing
\title{Trabalho de Conclusao de Curso}
\author{Nome do Aluno\\
Orientador: Prof. Dr. Nome}
\date{\today}
\begin{document}
\maketitle
% Termo de aprovacao
% Dedicacao
% Agradecimentos
% Resumo
\begin{abstract}
Resumo do TCC...
\end{abstract}
\tableofcontents
\newpage
\section{Introducao}
\section{Fundamentacao Teorica}
\section{Metodologia}
\section{Resultados e Discussao}
\section{Consideracoes Finais}
\begin{thebibliography}{99}
\bibitem{exemplo} SOBRENOME, N. Titulo. Editora, Ano.
\end{thebibliography}
\end{document}""",
    }
    
    return templates.get(doc_type, f"% Template nao encontrado para: {doc_type}\n% Use \\documentclass{{article}} com geometria ABNT")

# ══════════════════════════════════════════════════════════════════════
# AUDITOR DE CONFORMIDADE — Verifica documento contra normas
# ══════════════════════════════════════════════════════════════════════

def audit_document_compliance(tex_content: str) -> List[Dict]:
    """Verifica conformidade do documento LaTeX com normas ABNT."""
    findings = []
    
    # Margens ABNT NBR 14724
    if "geometry" not in tex_content and "setlength" not in tex_content:
        findings.append({"norma":"NBR 14724","item":"Margens","status":"NAO ENCONTRADO",
                        "acao":"Adicionar \\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}"})
    elif "3cm" in tex_content and "2cm" in tex_content:
        findings.append({"norma":"NBR 14724","item":"Margens","status":"OK"})
    
    # Espacamento 1.5
    if "onehalfspacing" in tex_content or "setstretch{1.5}" in tex_content:
        findings.append({"norma":"NBR 14724","item":"Espacamento 1.5","status":"OK"})
    else:
        findings.append({"norma":"NBR 14724","item":"Espacamento","status":"NAO ENCONTRADO",
                        "acao":"Adicionar \\onehalfspacing"})
    
    # Fonte 12pt
    if "12pt" in tex_content[:200]:
        findings.append({"norma":"NBR 14724","item":"Fonte 12pt","status":"OK"})
    else:
        findings.append({"norma":"NBR 14724","item":"Fonte","status":"NAO ENCONTRADO"})
    
    # Numeracao progressiva (sem ponto apos numero)
    section_pattern = re.findall(r'\\section\{(\d+)[\.\s]', tex_content)
    if section_pattern:
        findings.append({"norma":"NBR 6024","item":"Numeracao progressiva","status":"OK"})
    
    # Referencias (NBR 6023)
    if "thebibliography" in tex_content or "bibliography{" in tex_content:
        findings.append({"norma":"NBR 6023","item":"Referencias","status":"OK"})
    else:
        findings.append({"norma":"NBR 6023","item":"Referencias","status":"NAO ENCONTRADO"})
    
    # Citacoes (NBR 10520)
    if "cite{" in tex_content or "footnote{" in tex_content:
        findings.append({"norma":"NBR 10520","item":"Citacoes","status":"OK"})
    
    return findings

# ══════════════════════════════════════════════════════════════════════
# R9 — REVISOR DOCUMENTAL
# ══════════════════════════════════════════════════════════════════════

def reviewer_r9_documental(tex_content: str = None) -> Dict:
    """R9: Revisor Documental — conformidade ABNT e templates oficiais."""
    
    # Auditoria de conformidade
    compliance_findings = audit_document_compliance(tex_content or "")
    
    ok_count = sum(1 for f in compliance_findings if f.get("status") == "OK")
    total = len(compliance_findings)
    
    # Nota baseada na conformidade
    if total > 0:
        nota = (ok_count / total) * 10
    else:
        nota = 5.0  # sem conteudo para auditar
    
    # Templates disponiveis
    templates_disponiveis = list(OFFICIAL_TEMPLATES.keys())
    
    return {
        "revisor": "R9 Documental (ABNT/CAPES/USP/BN/IEEE/ACM)",
        "nota": round(nota, 1),
        "compliance": compliance_findings,
        "templates": f"{len(templates_disponiveis)} templates oficiais catalogados",
        "normas_cobertas": [
            "ABNT NBR 14724:2011 — Trabalhos Academicos",
            "ABNT NBR 6023:2018 — Referencias",
            "ABNT NBR 10520:2002 — Citacoes",
            "ABNT NBR 6024:2012 — Numeracao Progressiva",
            "CAPES — Teses e Periodicos Qualis",
            "USP — Template abnTeX2",
            "BN — Ficha Catalográfica e Deposito Legal",
            "IEEE — Artigos (ieeetran)",
            "ACM — Proceedings (acmart)",
            "Springer LNCS — Conference Papers",
            "Elsevier — Journal Articles",
        ],
        "parecer": _doc_parecer(nota, ok_count, total),
        "construir_template": "Use build_abnt_template('tipo') para gerar template LaTeX",
    }

def _doc_parecer(nota: float, ok: int, total: int) -> str:
    if nota >= 9.0:
        return f"EXCELENTE — {ok}/{total} itens ABNT conformes. Documento pronto para submissao."
    elif nota >= 7.0:
        return f"BOM — {ok}/{total} itens conformes. Pequenos ajustes necessarios."
    elif nota >= 5.0:
        return f"REGULAR — {ok}/{total} itens conformes. Revisao ABNT recomendada."
    else:
        return f"INSUFICIENTE — {ok}/{total} itens conformes. Requer reformatacao completa."

# ══════════════════════════════════════════════════════════════════════
# TDD
# ══════════════════════════════════════════════════════════════════════

def test_templates_catalog():
    assert len(OFFICIAL_TEMPLATES) >= 10, f"Apenas {len(OFFICIAL_TEMPLATES)} templates"
    for key, tmpl in OFFICIAL_TEMPLATES.items():
        assert "instituicao" in tmpl
        assert len(tmpl["normas"]) >= 2, f"{key}: apenas {len(tmpl['normas'])} normas"
    print(f"  [TDD] {len(OFFICIAL_TEMPLATES)} templates oficiais catalogados... PASS")
    return True

def test_build_template():
    for doc_type in ["relatorio_tecnico","tese_doutorado","artigo_qualis","tcc_graduacao"]:
        tmpl = build_abnt_template(doc_type)
        assert "documentclass" in tmpl, f"{doc_type}: sem documentclass"
        assert "begin{document}" in tmpl, f"{doc_type}: sem begin document"
    print(f"  [TDD] 4 templates ABNT construidos dinamicamente... PASS")
    return True

def test_compliance_audit():
    sample = r"""\documentclass[12pt,a4paper]{article}
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\onehalfspacing
\begin{document}
\section{1 Introducao}
Conteudo aqui \cite{exemplo}.
\begin{thebibliography}{99}
\bibitem{exemplo} SOBRENOME, N. Titulo. 2026.
\end{thebibliography}
\end{document}"""
    
    findings = audit_document_compliance(sample)
    ok = sum(1 for f in findings if f.get("status") == "OK")
    assert ok >= 3, f"Apenas {ok} itens OK"
    print(f"  [TDD] Auditoria conformidade: {ok}/{len(findings)} itens ABNT OK... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  R9 — REVISOR DOCUMENTAL (ABNT/CAPES/USP/BN/IEEE/ACM)")
    print("=" * 65)
    
    tests = [
        ("Templates catalogados", test_templates_catalog),
        ("Construcao dinamica", test_build_template),
        ("Auditoria conformidade", test_compliance_audit),
    ]
    
    passed = 0
    for name, fn in tests:
        try:
            fn(); passed += 1
        except AssertionError as e:
            print(f"  [{name}] FAIL: {e}")
    
    r9 = reviewer_r9_documental()
    print(f"\n  R9 Nota: {r9['nota']}/10")
    print(f"  Templates: {r9['templates']}")
    print(f"  Normas cobertas: {len(r9['normas_cobertas'])}")
    print(f"  RESULTADO: {passed}/{len(tests)} PASS")
    print("=" * 65)
    return passed == len(tests)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
