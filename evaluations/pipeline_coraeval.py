#!/usr/bin/env python3
"""Pipeline CORA-Eval: multi-fonte + PyMuPDF + extracao de insights. v3.0"""

import sys, os, json, re, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = Path("artigo/evaluations").resolve()
DOWNLOADS = BASE / "downloads"
CORPUS = BASE / "corpus_md"
DOWNLOADS.mkdir(exist_ok=True); CORPUS.mkdir(exist_ok=True)

def fetch_text(path):
    return Path(path).read_text(encoding='utf-8') if Path(path).exists() else ''

def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def extrair_insights(text, doi):
    ins = {'doi': doi, 'problemas': [], 'metodologias': [], 'metricas': [], 'dominios': [], 'tarefas': []}
    ins['problemas'] = list(set(re.findall(r'(?i)(?:limitation|challenge|problem|gap|difficult|shortcoming|issue|however|but|yet|although|despite)[^.]*\.', text)))[:5]
    ins['metodologias'] = list(set(re.findall(r'(?i)(?:method|approach|framework|pipeline|algorithm|technique|model|system|benchmark|evaluation)[^.]*\.[^.]*', text)))[:5]
    metrics = re.findall(r'(?i)(?:accuracy|precision|recall|f1[-\s]?score|auc|rmse|mae|mse|correlation|p[-\s]?value|score|agreement|reliability|validity|cohen|kappa)[^.]*\.', text)
    ins['metricas'] = list(set([m.strip().lower() for m in metrics]))[:5]
    dom = re.findall(r'(?i)(?:mathematics|physics|chemistry|biology|statistics|computer|engineering|geoscience|astronomy|neuroscience|linguistics|economics)[^.]*\.', text)
    ins['dominios'] = list(set([d.strip().lower() for d in dom]))[:5]
    tasks = re.findall(r'(?i)(?:classification|regression|clustering|ranking|prediction|generation|translation|summarization|qa|question.answering|reasoning)[^.]*\.', text)
    ins['tarefas'] = list(set([t.strip().lower() for t in tasks]))[:5]
    return ins

def buscar_arxiv(keyword, n=5):
    import feedparser
    papers = []
    try:
        feed = feedparser.parse(f"http://export.arxiv.org/api/query?search_query=all:{keyword.replace(' ','+')}&start=0&max_results={n}")
        for e in feed.entries:
            doi = ''
            for link in e.links:
                if link.rel == 'alternate' and 'arxiv' in link.href:
                    doi = link.href.split('abs/')[-1]
            papers.append({'doi': doi or e.id, 'title': e.title.replace('\n',' ').strip(),'source':'arxiv','url':f'https://arxiv.org/abs/{doi}'})
    except Exception as ex:
        print(f'  arXiv erro: {ex}')
    return papers

def buscar_crossref(keyword, n=5):
    import requests
    papers = []
    try:
        r = requests.get(f"https://api.crossref.org/works?query={keyword}&rows={n}", timeout=20)
        if r.status_code == 200:
            for item in r.json()['message']['items']:
                doi = item.get('DOI','')
                title = (item.get('title') or [''])[0]
                papers.append({'doi':doi,'title':title,'source':'crossref','url':f'https://doi.org/{doi}'})
    except Exception as ex:
        print(f'  CrossRef erro: {ex}')
    return papers

def baixar_arxiv(arxiv_id, out):
    import requests
    aid = arxiv_id.split('abs/')[-1] if arxiv_id.startswith('http') else arxiv_id
    r = requests.get(f"https://arxiv.org/pdf/{aid}.pdf", timeout=60)
    if r.status_code == 200:
        with open(out, 'wb') as f: f.write(r.content)
        return True
    return False

def baixar_scihub(doi, out):
    try:
        from scihub import SciHub
        sh = SciHub()
        for d in ['sci-hub.ru','sci-hub.st','sci-hub.wf']:
            if d not in sh.available_base_url_list: sh.available_base_url_list.insert(0,d)
        r = sh.fetch(doi)
        url = r.get('url')
        if url: sh.download(url, str(out)); return True
    except Exception as e:
        print(f'  Sci-Hub erro: {e}')
    return False

def extrair_texto_pdf(pdf_path):
    import fitz
    doc = fitz.open(str(pdf_path))
    text = ''.join(page.get_text() for page in doc)
    doc.close()
    return text

def processar_paper(paper):
    doi = paper['doi']
    d_clean = doi.replace('/','_').replace(':','_')
    pdf_path = DOWNLOADS / f'{d_clean}.pdf'
    txt_path = CORPUS / f'{d_clean}.txt'
    
    if not pdf_path.exists():
        print(f'  Baixando...', end=' ')
        if paper['source'] == 'arxiv':
            ok = baixar_arxiv(doi, pdf_path)
        else:
            ok = baixar_scihub(doi, pdf_path) if doi and not doi.startswith('http') else False
        if not ok:
            print('[FALHOU]')
            return None
        print('[OK]')
        time.sleep(1)
    else:
        print(f'  [CACHE]')
    
    if not txt_path.exists():
        print(f'  Extraindo texto...', end=' ')
        text = extrair_texto_pdf(pdf_path)
        txt_path.write_text(text, encoding='utf-8')
        print(f'{len(text)} chars')
    else:
        text = txt_path.read_text(encoding='utf-8')
        print(f'  [CACHE] {len(text)} chars')
    
    ins = extrair_insights(text, doi)
    paper['insights'] = ins
    paper['pdf'] = str(pdf_path)
    paper['txt'] = str(txt_path)
    return paper

def pipeline(keyword):
    print(f'\n=== BUSCA: {keyword} ===')
    papers = []
    papers.extend(buscar_arxiv(keyword, 5))
    papers.extend(buscar_crossref(keyword, 5))
    
    seen = set()
    papers_u = []
    for p in papers:
        if p['doi'] not in seen:
            seen.add(p['doi']); papers_u.append(p)
    print(f'Total: {len(papers_u)} artigos unicos')
    
    results = []
    for i, p in enumerate(papers_u):
        print(f'\n[{i+1}/{len(papers_u)}] {p["title"][:80]}...')
        r = processar_paper(p)
        if r:
            results.append(r)
            ins = r['insights']
            print(f'  -> {len(ins["problemas"])} prob | {len(ins["metricas"])} metr | {len(ins["dominios"])} dom | {len(ins["tarefas"])} tarefas')
    
    rel = BASE / 'relatorio_coraeval.json'
    save_json(rel, results)
    print(f'\n=== RESUMO: {len(results)}/{len(papers_u)} processados ===')
    print(f'Relatorio: {rel}')
    return results

if __name__ == '__main__':
    kw = sys.argv[1] if len(sys.argv) > 1 else 'benchmark evaluation framework reasoning'
    pipeline(kw)
