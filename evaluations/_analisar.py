import sys, os, json, re, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = Path(__file__).parent if '__file__' in dir() else Path('.')
BASE = BASE.resolve()

def extrair_insights(text, doi):
    ins = {'doi': doi, 'problemas': [], 'metodologias': [], 'metricas': [], 'dominios': [], 'tarefas': []}
    ins['problemas'] = list(set(re.findall(r'(?i)(?:limitation|challenge|problem|gap|difficult|shortcoming|issue|however|but|yet|although|despite)[^.]*\.', text)))[:5]
    ins['metodologias'] = list(set(re.findall(r'(?i)(?:method|approach|framework|pipeline|algorithm|technique|model|system|benchmark|evaluation)[^.]*\.[^.]*', text)))[:5]
    metrics = re.findall(r'(?i)(?:accuracy|precision|recall|f1[-\s]?score|auc|rmse|mae|mse|correlation|p[-\s]?value|score|agreement|reliability|validity|cohen|kappa)[^.]*\.', text)
    ins['metricas'] = list(set([m.strip().lower() for m in metrics]))[:5]
    dom = re.findall(r'(?i)(?:mathematics|physics|chemistry|biology|statistics|computer|engineering|geoscience|astronomy|neuroscience|linguistics|economics)[^.]*\.', text)
    ins['dominios'] = list(set([d.strip().lower() for d in dom]))[:5]
    tasks = re.findall(r'(?i)(?:classification|regression|clustering|ranking|prediction|generation|translation|summarization|qa|question.answering)[^.]*\.', text)
    ins['tarefas'] = list(set([t.strip().lower() for t in tasks]))[:5]
    return ins

# Ler o paper baixado
txt_path = Path("artigo/evaluations/corpus_md/1801.05075v2.txt")
text = txt_path.read_text(encoding='utf-8')
doi = "1801.05075v2"
title = "Quantitative Evaluation of Machine Learning Explanations: A Human-Grounded Benchmark"

print(f"\n=== ANALISE: {title} ===\n")
insights = extrair_insights(text, doi)

print(f"PROBLEMAS mencionados ({len(insights['problemas'])}):")
for p in insights['problemas']:
    print(f"  - {p[:150]}")

print(f"\nMETODOLOGIAS ({len(insights['metodologias'])}):")
for m in insights['metodologias']:
    print(f"  - {m[:150]}")

print(f"\nMETRICAS ({len(insights['metricas'])}):")
for m in insights['metricas']:
    print(f"  - {m[:150]}")

print(f"\nDOMINIOS ({len(insights['dominios'])}):")
for d in insights['dominios']:
    print(f"  - {d[:150]}")

print(f"\nTAREFAS ({len(insights['tarefas'])}):")
for t in insights['tarefas']:
    print(f"  - {t[:150]}")

# Salvar
Path("artigo/evaluations/insights_1801.05075.json").write_text(
    json.dumps(insights, indent=2, ensure_ascii=False), encoding='utf-8')
print("\nInsights salvos em insights_1801.05075.json")
