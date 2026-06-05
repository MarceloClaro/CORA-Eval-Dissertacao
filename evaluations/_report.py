#!/usr/bin/env python3
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open('artigo/evaluations/relatorio_coraeval.json', encoding='utf-8'))
for i, p in enumerate(d):
    ins = p['insights']
    print(f"[{i+1}] {p['title'][:75]}")
    print(f"    Fonte: {p['source']} | DOI: {p['doi']}")
    print(f"    Problemas: {len(ins['problemas'])} | Metodologias: {len(ins['metodologias'])} | Metricas: {len(ins['metricas'])}")
    for k in ['problemas','metodologias','metricas']:
        if ins[k]:
            print(f"    {k}: {ins[k][0][:100]}")
    print()

# Sumario
print("="*60)
print("SUMARIO CRUZADO")
print("="*60)
todas_met = []
todas_metr = []
for p in d:
    for m in p['insights']['metodologias']: todas_met.append(m[:80])
    for m in p['insights']['metricas']: todas_metr.append(m[:80])
print(f"Metodologias: {len(todas_met)} ocorrencias")
print(f"Metricas: {len(todas_metr)} ocorrencias")
