#!/usr/bin/env python3
"""
Pipeline Sci-Hub + arXiv + Docling para download, conversao e extracao de pesquisa
para evolucao do CORA-Eval Benchmark.
v2.0: Adiciona arXiv como fonte primaria, Sci-Hub .ru/.st como fontes secundarias.
"""
import sys, os, json, re, time, warnings
from pathlib import Path

warnings.filterwarnings('ignore', category=Warning)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.resolve()
DOWNLOADS_DIR = BASE_DIR / "downloads"
MD_DIR = BASE_DIR / "corpus_md"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(MD_DIR, exist_ok=True)

def buscar_arxiv(keyword, num_results=5):
    import feedparser
    query = keyword.replace(' ', '+')
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={num_results}"
    feed = feedparser.parse(url)
    papers = []
    for entry in feed.entries:
        doi = None
        for link in entry.links:
            if link.rel == 'alternate' and 'arxiv' in link.href:
                doi = link.href.split('abs/')[-1]
                break
        papers.append({
            'doi': doi or entry.id,
            'title': entry.title.replace('\n', ' ').strip(),
            'author': ', '.join([a.name for a in entry.authors[:3]]),
            'year': entry.published[:4] if hasattr(entry, 'published') else '',
            'source': 'arxiv',
            'url': entry.link if hasattr(entry, 'link') else f"https://arxiv.org/abs/{doi}",
            'summary': entry.summary[:500] if hasattr(entry, 'summary') else ''
        })
    return papers

def buscar_crossref(keyword, num_results=5):
    import requests
    url = f"https://api.crossref.org/works?query={keyword}&rows={num_results}"
    r = requests.get(url, timeout=30)
    papers = []
    if r.status_code == 200:
        for item in r.json()['message']['items']:
            doi = item.get('DOI', '')
            title = (item.get('title') or [''])[0]
            author = ', '.join([a.get('family','') for a in (item.get('author') or [])[:3]])
            year = ''
            for src in ['published-print', 'issued', 'published-online', 'created']:
                dp = item.get(src, {}).get('date-parts')
                if dp and dp[0]:
                    year = str(dp[0][0])
                    break
            papers.append({'doi': doi, 'title': title, 'author': author, 'year': year, 'source': 'crossref', 'url': f"https://doi.org/{doi}", 'summary': ''})
    return papers

def baixar_pdf_arxiv(arxiv_id, output_path):
    import requests
    if arxiv_id.startswith('http'):
        arxiv_id = arxiv_id.split('abs/')[-1]
    r = requests.get(f"https://arxiv.org/pdf/{arxiv_id}.pdf", timeout=60)
    if r.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(r.content)
        return True
    return False

def baixar_pdf_scihub(doi, output_path):
    from scihub import SciHub
    sh = SciHub()
    for d in ['sci-hub.ru', 'sci-hub.st', 'sci-hub.wf']:
        if d not in sh.available_base_url_list:
            sh.available_base_url_list.insert(0, d)
    try:
        result = sh.fetch(doi)
        pdf_url = result.get('url')
        if pdf_url:
            sh.download(pdf_url, str(output_path))
            return True
    except Exception as e:
        print(f"  Sci-Hub erro: {e}")
    return False

def baixar_pdf(paper, output_path):
    if paper['source'] == 'arxiv' and baixar_pdf_arxiv(paper['doi'], output_path):
        return True
    doi = paper.get('doi', '')
    if doi and not doi.startswith('http'):
        return baixar_pdf_scihub(doi, output_path)
    return False

def converter_pdf_para_md(pdf_path, output_path):
    from docling.document_converter import DocumentConverter
    md_text = DocumentConverter().convert(str(pdf_path)).document.export_to_markdown()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_text)
    return md_text

def extrair_insights(md_text, doi):
    insights = {'doi': doi, 'problemas': [], 'metodologias': [], 'metricas': [], 'dominios': []}
    insights['problemas'] = list(set(re.findall(r'(?i)(limitation|challenge|problem|gap|difficult|shortcoming|issue|however|but)[^.]*\.', md_text)))[:5]
    insights['metodologias'] = list(set(re.findall(r'(?i)(method|approach|framework|pipeline|algorithm|technique|model|system)[^.]*\.[^.]*', md_text)))[:5]
    metrics = re.findall(r'(?i)(accuracy|precision|recall|f1[-\s]score|auc|rmse|mae|mse|correlation|p[-\s]value|score)[^.]*\.', md_text)
    insights['metricas'] = list(set([m.lower().strip() for m in metrics]))[:5]
    dom = re.findall(r'(?i)(mathematics|physics|chemistry|biology|statistics|computer\s*science|engineering|geoscience|astronomy|neuroscience|linguistics|economics)[^.]*\.', md_text)
    insights['dominios'] = list(set([d.lower().strip() for d in dom]))[:5]
    return insights

def pipeline_completo(keyword=None, doi=None):
    papers = []
    print("=" * 60)
    print("FASE 1: BUSCA MULTI-FONTE")
    print("=" * 60)
    
    if doi:
        import requests
        r = requests.get(f"https://api.crossref.org/works/{doi}", timeout=30)
        if r.status_code == 200:
            item = r.json()['message']
            papers.append({'doi': doi, 'title': (item.get('title') or [''])[0], 'author': '', 'year': '', 'source': 'crossref', 'url': f"https://doi.org/{doi}", 'summary': ''})
    elif keyword:
        print(f"  Buscando: '{keyword}'")
        for nome, func in [('arXiv', buscar_arxiv), ('CrossRef', buscar_crossref)]:
            try:
                ps = func(keyword)
                print(f"  {nome}: {len(ps)} resultados")
                papers.extend(ps)
            except Exception as e:
                print(f"  {nome}: erro - {e}")
    
    if not papers:
        print("Nenhum artigo encontrado.")
        return []
    
    seen = set()
    papers_uniq = []
    for p in papers:
        if p['doi'] not in seen:
            seen.add(p['doi'])
            papers_uniq.append(p)
    papers = papers_uniq[:10]
    print(f"  Total unicos: {len(papers)} artigos")
    
    resultados = []
    for i, paper in enumerate(papers):
        print(f"\n--- [{i+1}/{len(papers)}] {paper['title'][:80]}...")
        print(f"    Fonte: {paper['source']} | DOI: {paper['doi'][:60]}")
        
        doi_clean = paper['doi'].replace('/', '_').replace(':', '_')
        pdf_path = DOWNLOADS_DIR / f"{doi_clean}.pdf"
        
        if not pdf_path.exists():
            print(f"  Download...")
            ok = baixar_pdf(paper, pdf_path)
            if not ok:
                print(f"  [SKIP] PDF indisponivel.")
                continue
            time.sleep(1)
        else:
            print(f"  [CACHE] PDF existe.")
        
        md_path = MD_DIR / f"{doi_clean}.md"
        if not md_path.exists():
            print(f"  Convertendo -> Markdown (docling)...")
            try:
                md_text = converter_pdf_para_md(pdf_path, md_path)
                print(f"  [OK] {len(md_text)} caracteres")
            except Exception as e:
                print(f"  [ERRO] Conversao: {e}")
                continue
        else:
            with open(md_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
            print(f"  [CACHE] MD ({len(md_text)} chars)")
        
        insights = extrair_insights(md_text, paper['doi'])
        paper['insights'] = insights
        paper['pdf_path'] = str(pdf_path)
        paper['md_path'] = str(md_path)
        resultados.append(paper)
        print(f"  Insights: {len(insights['problemas'])} problemas | {len(insights['metricas'])} metricas | {len(insights['dominios'])} dominios")
    
    relatorio = BASE_DIR / "relatorio_scihub.json"
    with open(relatorio, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"\nRelatorio salvo: {relatorio}")
    print(f"Processados: {len(resultados)}/{len(papers)}")
    return resultados

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default="benchmark evaluation benchmark suite scientific computing")
    parser.add_argument("--doi")
    args = parser.parse_args()
    pipeline_completo(keyword=args.keyword, doi=args.doi)
