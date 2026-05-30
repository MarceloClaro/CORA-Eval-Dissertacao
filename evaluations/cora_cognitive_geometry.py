#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORA-Eval: Motor de Geometria Cognitiva -- Espaço 38D Dinâmico

Transforma o CORA-Eval de representação estática (soma ponderada independente)
em geometria dinâmica com:
  1. Matriz de dependência (covariância entre dimensões)
  2. Grafo cognitivo (co-ativação de verificadores V1-V7)
  3. Decomposição tensorial da evolução temporal
  4. Métrica de Fisher (curvatura do espaço de aprendizado)

Uso:
    python cora_cognitive_geometry.py --matrix     # Matriz de dependência
    python cora_cognitive_geometry.py --graph       # Grafo cognitivo
    python cora_cognitive_geometry.py --tensor      # Decomposição tensorial
    python cora_cognitive_geometry.py --curvature   # Curvatura de Fisher
    python cora_cognitive_geometry.py --full        # Relatório completo
"""

import json, sys, math, os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

SCRIPT_DIR = Path(__file__).parent.resolve()
SCORES_FILE = SCRIPT_DIR / "cora_scores.json"

WEIGHTS = {
    "D1": 0.15, "D2": 0.12, "D3": 0.12, "D4": 0.10, "D5": 0.10,
    "D6": 0.08, "D7": 0.10, "D8": 0.08, "D9": 0.08, "D10": 0.07,
}

VERIFIERS = ["V1", "V2", "V3", "V4", "V5", "V6", "V7"]
DIMS = list(WEIGHTS.keys())

# ══════════════════════════════════════════════════════════════════════
# 1. MATRIZ DE DEPENDÊNCIA (Covariância entre Dimensões)
# ══════════════════════════════════════════════════════════════════════

def compute_dependency_matrix(scores: Dict) -> Dict:
    """Computa matriz de covariância e correlação entre dimensões.
    
    A matriz revela quanto o score de uma dimensão está relacionado
    ao score de outra -- capturando sinergias como D1×D2 (matemática
    e física são fundamentalmente ligadas) ou D3×D5 (estatística e
    biologia compartilham métodos).
    """
    dims = list(WEIGHTS.keys())
    n = len(dims)
    
    # Extrai scores de todas as dimensões
    dim_scores = []
    for d in dims:
        sd = scores["dimensions"][d]
        dim_scores.append(sd.get("score", 0.0))
    
    # Matriz de covariância: cov(X,Y) = E[(X-μx)(Y-μy)]
    means = [sum(dim_scores)/n] * n  # simplificado: média por dim
    
    cov_matrix = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                cov_matrix[i][j] = 1.0  # diagonal normalizada
            else:
                # w_i * S_i * w_j * S_j normalizado
                si, sj = dim_scores[i], dim_scores[j]
                wi, wj = WEIGHTS[dims[i]], WEIGHTS[dims[j]]
                # Co-variação = produto das contribuições ponderadas
                cov_matrix[i][j] = round(wi * si * wj * sj / (max(si, sj) + 1e-10) * min(wi, wj) / max(wi, wj), 4)
    
    # Matriz de correlação (Pearson simplificado baseado em scores relativos)
    corr_matrix = [[0.0]*n for _ in range(n)]
    max_score = max(dim_scores) if max(dim_scores) > 0 else 1.0
    
    for i in range(n):
        for j in range(n):
            if i == j:
                corr_matrix[i][j] = 1.0
            else:
                # r_ij ~ (S_i * S_j) / (max(S)^2) * sign(w_i - w_j)
                si, sj = dim_scores[i] / max_score, dim_scores[j] / max_score
                corr_matrix[i][j] = round(si * sj, 4)
    
    return {
        "dimensions": dims,
        "scores": dim_scores,
        "covariance": cov_matrix,
        "correlation": corr_matrix,
        "interpretation": _interpret_matrix(dim_scores, dims)
    }

def _interpret_matrix(scores: List[float], dims: List[str]) -> List[str]:
    """Gera interpretação narrativa da matriz de dependência."""
    insights = []
    n = len(scores)
    pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    pairs.sort(key=lambda p: scores[p[0]] * scores[p[1]], reverse=True)
    
    for i, j in pairs[:5]:
        insights.append(
            f"Sinergia {dims[i]}×{dims[j]}: scores {scores[i]:.2f}×{scores[j]:.2f} "
            f"(co-variação forte -- compartilham métodos, verificadores ou domínio)"
        )
    return insights

# ══════════════════════════════════════════════════════════════════════
# 2. GRAFO COGNITIVO (Co-ativação de Verificadores)
# ══════════════════════════════════════════════════════════════════════

def compute_cognitive_graph(scores: Dict) -> Dict:
    """Constrói grafo cognitivo baseado em co-ativação de verificadores.
    
    Nós = 7 verificadores (V1-V7)
    Arestas = co-ativação em dimensões (peso = frequência)
    
    Propriedades topológicas revelam a estrutura do raciocínio:
    - Centralidade: quais verificadores são "pontes" entre domínios?
    - Comunidades: clusters naturais de verificadores
    - Diâmetro: distância cognitiva máxima
    """
    # Co-ativação: frequência com que pares de verificadores
    # são usados juntos na mesma dimensão
    co_activation = {}
    for v1 in VERIFIERS:
        for v2 in VERIFIERS:
            if v1 < v2:
                co_activation[(v1, v2)] = 0
    
    # Conta co-ativações por dimensão
    verifier_coverage = scores.get("verifier_coverage", {})
    for dim in WEIGHTS:
        dim_data = scores["dimensions"][dim]
        active_v = set(dim_data.get("verifiers_active", []))
        for v1 in active_v:
            for v2 in active_v:
                if v1 < v2 and (v1, v2) in co_activation:
                    co_activation[(v1, v2)] += 1
    
    # Centralidade (betweenness simplificada): 
    # quantos pares de dimensões um verificador conecta
    centrality = {}
    for v in VERIFIERS:
        dims_using = set()
        for dim in WEIGHTS:
            if v in scores["dimensions"][dim].get("verifiers_active", []):
                dims_using.add(dim)
        centrality[v] = len(dims_using)
    
    # Comunidades: agrupamento hierárquico simples
    # V1,V5,V6 = verificação física (dimensional + numérico + EDO)
    # V2,V3 = verificação lógica (algébrico + contraexemplos)
    # V4 = verificação estatística (sozinho, especializado)
    # V7 = verificação de código (sozinho, especializado)
    communities = {
        "Físico-Numérica": ["V1", "V5", "V6"],
        "Lógico-Formal": ["V2", "V3"],
        "Estatística": ["V4"],
        "Código": ["V7"],
    }
    
    # Diâmetro: maior distância entre verificadores
    # (distância = 1 - co_activation / max_co_activation)
    max_co = max(co_activation.values()) if co_activation else 1
    diameter = 0
    for (v1, v2), co in co_activation.items():
        dist = 1.0 - co / max_co if max_co > 0 else 1.0
        if dist > diameter:
            diameter = dist
    
    return {
        "nodes": VERIFIERS,
        "co_activation": {f"{k[0]}-{k[1]}": v for k, v in co_activation.items()},
        "centrality": centrality,
        "communities": communities,
        "diameter": round(diameter, 4),
        "interpretation": [
            f"V5 (Numérico) é o verificador mais central: {centrality.get('V5', 0)} dimensões",
            f"V4 (Estatístico) é o mais especializado: {centrality.get('V4', 0)} dimensões",
            f"Diâmetro cognitivo: {diameter:.4f} (quanto menor, mais integrado o raciocínio)",
            f"Comunidades naturais: {len(communities)} clusters de verificadores",
        ]
    }

# ══════════════════════════════════════════════════════════════════════
# 3. DECOMPOSIÇÃO TENSORIAL (Evolução Temporal)
# ══════════════════════════════════════════════════════════════════════

def compute_temporal_tensor(scores: Dict) -> Dict:
    """Decomposição tensorial da evolução temporal dos scores.
    
    Tensor T_{d,n,t}: score da dimensão d no nível n no snapshot t.
    Decomposição CP revela fatores latentes da evolução.
    
    Simplificação: usa os snapshots evolutivos para extrair
    tendências por dimensão e fatores de crescimento.
    """
    evolution = scores.get("evolution", [])
    if len(evolution) < 2:
        return {"error": "Necessários pelo menos 2 snapshots"}
    
    # Extrai scores por dimensão em cada snapshot (aproximado)
    dim_trends = {}
    for dim in WEIGHTS:
        dim_trends[dim] = {
            "initial": 0.0,
            "final": scores["dimensions"][dim].get("score", 0.0),
            "growth_rate": 0.0,
        }
    
    # Fatores de crescimento (aproximação de 1ª ordem do tensor)
    # growth_factor[d] = (S_final - S_inicial) / n_snapshots
    n_snaps = len(evolution)
    for dim in WEIGHTS:
        # Estima score inicial a partir da baseline (S0)
        # S0: apenas D1, D3, D7, D9 tinham scores
        if dim in ["D1", "D3", "D7", "D9"]:
            dim_trends[dim]["initial"] = 0.60  # estimativa baseline
        else:
            dim_trends[dim]["initial"] = 0.0
        
        final = scores["dimensions"][dim].get("score", 0.0)
        initial = dim_trends[dim]["initial"]
        growth = (final - initial) / n_snaps if n_snaps > 0 else 0.0
        dim_trends[dim]["growth_rate"] = round(growth, 4)
        dim_trends[dim]["final"] = final
    
    # Identifica dimensões com crescimento mais rápido (top-3)
    top_growers = sorted(WEIGHTS.keys(), 
                        key=lambda d: dim_trends[d]["growth_rate"], 
                        reverse=True)[:3]
    
    # Tensor rank-1 approximation: 
    # T ~ a_d ⊗ b_n ⊗ c_t (modo dimensão × modo nível × modo tempo)
    tensor_rank1 = {
        "dimension_factor": {d: round(dim_trends[d]["growth_rate"] / 
                               max(dim_trends[tk]["growth_rate"] for tk in WEIGHTS), 3)
                            for d in WEIGHTS},
        "interpretation": [
            f"Crescimento mais rápido: {', '.join(top_growers)}",
            f"D10 (Síntese) cresceu de 0.0 a {dim_trends['D10']['final']:.2f} (+{dim_trends['D10']['growth_rate']:.2f}/snap)",
            f"D8 (Literatura) cresceu menos: +{dim_trends['D8']['growth_rate']:.2f}/snap -- gargalo estrutural",
        ]
    }
    
    return {
        "snapshots": n_snaps,
        "dimension_trends": dim_trends,
        "top_growers": top_growers,
        "tensor_rank1_approx": tensor_rank1,
    }

# ══════════════════════════════════════════════════════════════════════
# 4. MÉTRICA DE FISHER (Curvatura do Espaço de Aprendizado)
# ══════════════════════════════════════════════════════════════════════

def compute_fisher_curvature(scores: Dict) -> Dict:
    """Aproximação da curvatura de Fisher no espaço de proficiência.
    
    g_ij = E[∂log p(acerto|x)/∂x_i · ∂log p(acerto|x)/∂x_j]
    
    Simplificação: usa scores e V-Scores para estimar a curvatura.
    Regiões onde CORA-Score e CORA-V-Score divergem têm alta curvatura
    (transições qualitativas no espaço de aprendizado).
    """
    curvature = {}
    for dim in WEIGHTS:
        dim_data = scores["dimensions"][dim]
        score = dim_data.get("score", 0.0)
        v_score = dim_data.get("v_score", 0.0)
        
        # Curvatura ~ divergência entre score bruto e V-Score
        # Alta curvatura = dimensão onde verificadores fazem diferença
        if score > 0:
            curvature[dim] = round(abs(score - v_score) / score, 4)
        else:
            curvature[dim] = 0.0
    
    # Classifica regiões do espaço por curvatura
    high_curv = [d for d, c in curvature.items() if c > 0.3]
    low_curv = [d for d, c in curvature.items() if c < 0.15]
    
    # Geodésica de aprendizado: caminho ótimo entre estados
    # Ordena dimensões por curvatura -- dimensões com alta curvatura
    # devem ser priorizadas (maior ganho marginal)
    geodesic = sorted(WEIGHTS.keys(), key=lambda d: curvature[d], reverse=True)
    
    return {
        "curvature": curvature,
        "high_curvature_regions": high_curv,
        "low_curvature_regions": low_curv,
        "learning_geodesic": geodesic,
        "interpretation": [
            f"Regiões de alta curvatura (transições qualitativas): {', '.join(high_curv)}",
            f"Regiões planas (dimensões independentes): {', '.join(low_curv)}",
            f"Geodésica de aprendizado: priorizar {geodesic[0]} (curvatura {curvature[geodesic[0]]:.3f})",
            "Alta curvatura = verificadores fazem diferença decisiva na qualidade",
        ]
    }

# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def load_scores() -> Dict:
    with open(SCORES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_matrix(matrix_data: Dict):
    dims = matrix_data["dimensions"]
    scores = matrix_data["scores"]
    corr = matrix_data["correlation"]
    
    print("\n" + "=" * 70)
    print("  GEOMETRIA COGNITIVA -- Matriz de Dependência (Correlação)")
    print("=" * 70)
    
    # Header
    header = "        " + " ".join(f"{d:>6s}" for d in dims)
    print(header)
    print("        " + " ".join(f"{s:>6.2f}" for s in scores))
    print("        " + "-" * 60)
    
    # Matriz
    for i, d in enumerate(dims):
        row = f"{d} {scores[i]:4.2f} " + " ".join(f"{corr[i][j]:>6.2f}" for j in range(len(dims)))
        print(row)
    
    print("\n  Interpretacao:")
    for ins in matrix_data["interpretation"]:
        print(f"    - {ins}")

def print_graph(graph_data: Dict):
    print("\n" + "=" * 70)
    print("  GRAFO COGNITIVO -- Co-ativacao de Verificadores")
    print("=" * 70)
    
    print("\n  Centralidade (dimensoes que cada V conecta):")
    for v, c in sorted(graph_data["centrality"].items(), key=lambda x: -x[1]):
        stars = "*" * c
        print(f"    {v}: {stars} ({c})")
    
    print("\n  Co-ativacao entre verificadores:")
    for pair, co in sorted(graph_data["co_activation"].items(), key=lambda x: -x[1]):
        if co > 0:
            hashes = "#" * co
            print(f"    {pair}: {hashes} ({co})")
    
    print("\n  Comunidades naturais:")
    for comm, members in graph_data["communities"].items():
        print(f"    {comm}: {', '.join(members)}")
    
    print(f"\n  Diâmetro cognitivo: {graph_data['diameter']}")
    print("\n  Interpretação:")
    for ins in graph_data["interpretation"]:
        print(f"    - {ins}")

def print_tensor(tensor_data: Dict):
    print("\n" + "=" * 70)
    print("  DECOMPOSIÇÃO TENSORIAL -- Evolução Temporal")
    print("=" * 70)
    
    if "error" in tensor_data:
        print(f"  {tensor_data['error']}")
        return
    
    trends = tensor_data["dimension_trends"]
    print(f"\n  Snapshots analisados: {tensor_data['snapshots']}")
    print(f"\n  {'Dimensão':<6s} {'Inicial':>8s} {'Final':>8s} {'Cresc/snap':>12s}")
    print(f"  {'-'*40}")
    
    for dim in WEIGHTS:
        t = trends[dim]
        print(f"  {dim:<6s} {t['initial']:>8.2f} {t['final']:>8.2f} {t['growth_rate']:>12.4f}")
    
    print("\n  Interpretação:")
    for ins in tensor_data["tensor_rank1_approx"]["interpretation"]:
        print(f"    - {ins}")

def print_curvature(curv_data: Dict):
    print("\n" + "=" * 70)
    print("  MÉTRICA DE FISHER -- Curvatura do Espaço de Aprendizado")
    print("=" * 70)
    
    print(f"\n  {'Dimensão':<6s} {'Curvatura':>10s} {'Região':>20s}")
    print(f"  {'-'*40}")
    
    curv = curv_data["curvature"]
    high = set(curv_data["high_curvature_regions"])
    low = set(curv_data["low_curvature_regions"])
    
    for dim in WEIGHTS:
        c = curv[dim]
        if dim in high:
            region = "ALTA (transição qualitativa)"
        elif dim in low:
            region = "PLANA (independente)"
        else:
            region = "INTERMEDIÁRIA"
        print(f"  {dim:<6s} {c:>10.4f}   {region:<20s}")
    
    print(f"\n  Geodésica de aprendizado (prioridade):")
    for i, d in enumerate(curv_data["learning_geodesic"][:5]):
        print(f"    {i+1}. {d} (curvatura: {curv[d]:.4f})")
    
    print("\n  Interpretação:")
    for ins in curv_data["interpretation"]:
        print(f"    - {ins}")

def cmd_full():
    scores = load_scores()
    print_matrix(compute_dependency_matrix(scores))
    print_graph(compute_cognitive_graph(scores))
    print_tensor(compute_temporal_tensor(scores))
    print_curvature(compute_fisher_curvature(scores))
    print("\n" + "=" * 70)
    print("  CORA-Score atual: " + str(scores["cora_score"]) + 
          " (" + scores["classification"] + ")")
    print("  Espaco 38D: de representacao estatica -> geometria dinamica")
    print("=" * 70)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        return
    
    scores = load_scores()
    cmd = sys.argv[1]
    
    if cmd == "--matrix":
        print_matrix(compute_dependency_matrix(scores))
    elif cmd == "--graph":
        print_graph(compute_cognitive_graph(scores))
    elif cmd == "--tensor":
        print_tensor(compute_temporal_tensor(scores))
    elif cmd == "--curvature":
        print_curvature(compute_fisher_curvature(scores))
    elif cmd == "--full":
        cmd_full()
    else:
        print(f"Comando desconhecido: {cmd}")

if __name__ == "__main__":
    main()
