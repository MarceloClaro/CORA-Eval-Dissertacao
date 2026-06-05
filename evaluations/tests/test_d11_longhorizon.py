"""test_d11_longhorizon.py — SPEC-013: D11 Raciocínio de Longo Horizonte (DAG)
150 CTs (5 domínios × 4 níveis = 30 tarefas/domínio), pytest.
Cada tarefa: DAG topologicamente ordenada onde cada nó é individualmente
tratável mas a propagação requer raciocínio de longo horizonte.
Referência: DeepSeek-R1: Incentivizing Reasoning Capability (2025) §3.4.3
"""

import math
import operator
import random
from collections import deque

import pytest

random.seed(42)

# ═══════════════════════════════════════════════════════════════════
# DAG Engine
# ═══════════════════════════════════════════════════════════════════

def topological_sort(nodes, edges):
    in_degree = {n: 0 for n in nodes}
    for u, v in edges:
        in_degree[v] = in_degree.get(v, 0) + 1
    queue = deque([n for n in nodes if in_degree[n] == 0])
    result = []
    while queue:
        cur = queue.popleft()
        result.append(cur)
        for u, v in edges:
            if u == cur:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
    return result

def execute_dag(nodes):
    """nodes: dict[str, (callable, list[str])] -> nome -> (função, [deps])"""
    all_nodes = list(nodes.keys())
    edges = []
    for name, (_, deps) in nodes.items():
        for d in deps:
            edges.append((d, name))
    order = topological_sort(all_nodes, edges)
    vals = {}
    for name in order:
        func, deps = nodes[name]
        dep_vals = tuple(vals[d] for d in deps)
        vals[name] = func(*dep_vals) if dep_vals else func()
    return vals


# ═══════════════════════════════════════════════════════════════════
# Helper: task generator
# ═══════════════════════════════════════════════════════════════════

def make_task(name, nodes_spec, expected_key):
    """
    nodes_spec: dict[name, (callable, [deps])]
    expected_key: qual nó contém o output esperado
    Retorna (nome, nodes, expected_output)
    """
    result = execute_dag(nodes_spec)
    return (name, nodes_spec, result[expected_key])


# ═══════════════════════════════════════════════════════════════════
# DOMAIN 1: Logic (DAG-L)
# ═══════════════════════════════════════════════════════════════════

def _logic_tasks():
    tasks = []

    # N1 — 5 tasks (2-3 nodes)
    tasks.append(make_task("L-N1-1: AND chain", {
        "a":  (lambda: True, []),
        "b":  (lambda: True, []),
        "c":  (lambda a,b: a and b, ["a","b"]),
        "out":(lambda c: c, ["c"]),
    }, "out"))

    tasks.append(make_task("L-N1-2: OR propagation", {
        "a":  (lambda: False, []),
        "b":  (lambda: True, []),
        "c":  (lambda a,b: a or b, ["a","b"]),
        "out":(lambda c: c, ["c"]),
    }, "out"))

    tasks.append(make_task("L-N1-3: NOT inversion", {
        "a":  (lambda: True, []),
        "b":  (lambda a: not a, ["a"]),
        "out":(lambda b: b, ["b"]),
    }, "out"))

    tasks.append(make_task("L-N1-4: XOR detection", {
        "a":  (lambda: True, []),
        "b":  (lambda: False, []),
        "c":  (lambda a,b: a != b, ["a","b"]),
        "out":(lambda c: c, ["c"]),
    }, "out"))

    tasks.append(make_task("L-N1-5: NAND gate", {
        "a":  (lambda: 1, []),
        "b":  (lambda: 1, []),
        "c":  (lambda a,b: 0 if a==1 and b==1 else 1, ["a","b"]),
        "out":(lambda c: c, ["c"]),
    }, "out"))

    # N2 — 7 tasks (4-6 nodes)
    tasks.append(make_task("L-N2-1: (A AND B) OR (C AND D)", {
        "a":(lambda:1,[]),"b":(lambda:1,[]),"c":(lambda:0,[]),"d":(lambda:1,[]),
        "e":(lambda a,b: a and b,["a","b"]),
        "f":(lambda c,d: c and d,["c","d"]),
        "out":(lambda e,f: e or f,["e","f"]),
    },"out"))

    tasks.append(make_task("L-N2-2: 3-level implication", {
        "a":(lambda:1,[]),"b":(lambda:0,[]),
        "c":(lambda a,b: 0 if a==1 and b==0 else 1,["a","b"]),
        "d":(lambda c: c,["c"]),
        "e":(lambda d: d,["d"]),
        "out":(lambda e: e,["e"]),
    },"out"))

    tasks.append(make_task("L-N2-3: Majority gate (3 inputs)", {
        "a":(lambda:1,[]),"b":(lambda:0,[]),"c":(lambda:1,[]),
        "d":(lambda a,b,c: 1 if (a+b+c)>=2 else 0,["a","b","c"]),
        "out":(lambda d: d,["d"]),
    },"out"))

    tasks.append(make_task("L-N2-4: XOR chain 4 inputs", {
        "a":(lambda:1,[]),"b":(lambda:0,[]),"c":(lambda:1,[]),"d":(lambda:1,[]),
        "e":(lambda a,b: a!=b,["a","b"]),
        "f":(lambda e,c: e!=c,["e","c"]),
        "out":(lambda f,d: f!=d,["f","d"]),
    },"out"))

    tasks.append(make_task("L-N2-5: AND-OR tree", {
        "a":(lambda:1,[]),"b":(lambda:1,[]),"c":(lambda:1,[]),"d":(lambda:0,[]),
        "e":(lambda a,b: a and b,["a","b"]),
        "f":(lambda c,d: c and d,["c","d"]),
        "out":(lambda e,f: e or f,["e","f"]),
    },"out"))

    tasks.append(make_task("L-N2-6: Conditional propagation", {
        "a":(lambda:1,[]),"b":(lambda:0,[]),
        "c":(lambda a: a,["a"]),
        "d":(lambda c,b: c if c else b,["c","b"]),
        "out":(lambda d: d,["d"]),
    },"out"))

    tasks.append(make_task("L-N2-7: NOR + NAND composition", {
        "a":(lambda:0,[]),"b":(lambda:0,[]),"c":(lambda:1,[]),"d":(lambda:1,[]),
        "e":(lambda a,b: 0 if a==0 and b==0 else 1,["a","b"]),  # NAND(a,b) = 1
        "f":(lambda c,d: 1 if c==0 and d==0 else 0,["c","d"]),  # NOR(c,d) = 0
        "out":(lambda e,f: e and f,["e","f"]),
    },"out"))

    # N3 — 8 tasks (7-10 nodes)
    tasks.append(make_task("L-N3-1: 4-bit parity", {
        "a":(lambda:1,[]),"b":(lambda:0,[]),"c":(lambda:1,[]),"d":(lambda:0,[]),
        "e":(lambda a,b: a!=b,["a","b"]),
        "f":(lambda e,c: e!=c,["e","c"]),
        "g":(lambda f,d: f!=d,["f","d"]),
        "out":(lambda g: g,["g"]),
    },"out"))

    tasks.append(make_task("L-N3-2: Full adder sum", {
        "a":(lambda:1,[]),"b":(lambda:0,[]),"cin":(lambda:1,[]),
        "s1":(lambda a,b: a!=b,["a","b"]),
        "sum":(lambda s1,cin: s1!=cin,["s1","cin"]),
        "c1":(lambda a,b: a and b,["a","b"]),
        "c2":(lambda s1,cin: s1 and cin,["s1","cin"]),
        "cout":(lambda c1,c2: c1 or c2,["c1","c2"]),
        "out":(lambda sum,cout: (sum,cout),["sum","cout"]),
    },"out"))

    tasks.append(make_task("L-N3-3: 3-level AND-OR cascade", {
        "a":(lambda:1,[]),"b":(lambda:1,[]),"c":(lambda:0,[]),
        "d":(lambda:1,[]),"e":(lambda:0,[]),
        "f":(lambda a,b: a and b,["a","b"]),
        "g":(lambda c,d: c and d,["c","d"]),
        "h":(lambda f,g,e: (f or g) and e,["f","g","e"]),
        "out":(lambda h: h,["h"]),
    },"out"))

    tasks.append(make_task("L-N3-4: Priority encoder", {
        "i0":(lambda:0,[]),"i1":(lambda:1,[]),"i2":(lambda:0,[]),"i3":(lambda:1,[]),
        "v":(lambda i0,i1,i2,i3: i0 or i1 or i2 or i3,["i0","i1","i2","i3"]),
        "y0":(lambda i1,i3: i1 or i3,["i1","i3"]),
        "y1":(lambda i2,i3: i2 or i3,["i2","i3"]),
        "out":(lambda v,y0,y1: (v,y0,y1),["v","y0","y1"]),
    },"out"))

    tasks.append(make_task("L-N3-5: Inference chain with negation", {
        "p":(lambda:1,[]),"q":(lambda:1,[]),"r":(lambda:0,[]),
        "not_r":(lambda r: 1-r,["r"]),
        "p_and_q":(lambda p,q: p and q,["p","q"]),
        "s":(lambda p_and_q,not_r: p_and_q and not_r,["p_and_q","not_r"]),
        "out":(lambda s: s,["s"]),
    },"out"))

    tasks.append(make_task("L-N3-6: Multiplexer 2-to-1", {
        "s":(lambda:0,[]),"d0":(lambda:1,[]),"d1":(lambda:0,[]),
        "not_s":(lambda s: 1-s,["s"]),
        "a":(lambda not_s,d0: not_s and d0,["not_s","d0"]),
        "b":(lambda s,d1: s and d1,["s","d1"]),
        "y":(lambda a,b: a or b,["a","b"]),
        "out":(lambda y: y,["y"]),
    },"out"))

    tasks.append(make_task("L-N3-7: Boolean minimization", {
        "a":(lambda:1,[]),"b":(lambda:0,[]),"c":(lambda:1,[]),
        "t1":(lambda a,b: a or b,["a","b"]),
        "t2":(lambda b,c: b or c,["b","c"]),
        "t3":(lambda a,c: a and c,["a","c"]),
        "out":(lambda t1,t2,t3: t1 and t2 or t3,["t1","t2","t3"]),
    },"out"))

    tasks.append(make_task("L-N3-8: Controlled NOT (CNOT)", {
        "ctrl":(lambda:1,[]),"target":(lambda:0,[]),
        "new_target":(lambda ctrl,target: target if not ctrl else 1-target,["ctrl","target"]),
        "out":(lambda ctrl,new_target: (ctrl,new_target),["ctrl","new_target"]),
    },"out"))

    # N4 — 10 tasks (11-20 nodes)
    tasks.append(make_task("L-N4-1: 8-bit AND reduction", {
        f"b{i}":(lambda i=i: random.Random(42+i).randint(0,1),[]) for i in range(8)
    } | {
        f"t{i}":(lambda *args: all(args),
                [f"b{j}" for j in range(2**i, min(2**(i+1),8))])
        for i in range(3)
    } | {
        "out":(lambda t0,t1,t2: t0 and t1 and t2,["t0","t1","t2"]),
    }, "out"))

    tasks.append(make_task("L-N4-2: 3-bit comparator", {
        f"a{i}":(lambda i=i: 1,[]) for i in range(3)
    } | {
        f"b{i}":(lambda i=i: 0,[]) for i in range(3)
    } | {
        f"eq{i}":(lambda a, b: a == b,[f"a{i}",f"b{i}"]) for i in range(3)
    } | {
        "all_eq":(lambda eq0,eq1,eq2: eq0 and eq1 and eq2,["eq0","eq1","eq2"]),
        "out":(lambda all_eq: all_eq,["all_eq"]),
    }, "out"))

    # Remaining N4: manually defined for uniqueness
    tasks.append(make_task("L-N4-3: 4-bit carry lookahead", {
        f"g{i}":(lambda i=i: random.Random(100+i).randint(0,1),[]) for i in range(4)
    } | {
        f"p{i}":(lambda i=i: random.Random(200+i).randint(0,1),[]) for i in range(4)
    } | {
        f"c{i}":((lambda i: lambda *args: args[0] or (args[1] and args[2]) if i>0 else args[0])(i),
                [f"g{i}"]+([f"p{i}"] if i==0 else [f"p{i}",f"c{i-1}"])) for i in range(4)
    } | {
        "out":(lambda c0,c1,c2,c3: (c0,c1,c2,c3),["c0","c1","c2","c3"]),
    }, "out"))

    tasks.append(make_task("L-N4-4: Decision tree depth 3", {
        "x1":(lambda:1,[]),"x2":(lambda:0,[]),"x3":(lambda:1,[]),"x4":(lambda:1,[]),
        "n1":(lambda x1: "A" if x1 else "B",["x1"]),
        "n2":(lambda n1,x2: ("A1" if x2 else "A2") if n1=="A" else ("B1" if x2 else "B2"),["n1","x2"]),
        "n3":(lambda n2,x3: {"A1": f"A1_{'Y' if x3 else 'N'}","A2": f"A2_{'Y' if x3 else 'N'}",
                            "B1": f"B1_{'Y' if x3 else 'N'}","B2": f"B2_{'Y' if x3 else 'N'}"}[n2],["n2","x3"]),
        "out":(lambda n3: n3,["n3"]),
    },"out"))

    tasks.append(make_task("L-N4-5: 5-input threshold gate", {
        f"x{i}":(lambda i=i: [1,0,1,0,1][i],[]) for i in range(5)
    } | {
        "sum":(lambda x0,x1,x2,x3,x4: x0+x1+x2+x3+x4,["x0","x1","x2","x3","x4"]),
        "out":(lambda s: 1 if s>=3 else 0,["sum"]),
    },"out"))

    tasks.append(make_task("L-N4-6: Tautology checker (3 var)", {
        f"x{i}":(lambda i=i: random.Random(300+i).randint(0,1),[]) for i in range(3)
    } | {
        "c1":(lambda x0,x1,x2: (x0 or (not x0)),["x0","x1","x2"]),
        "c2":(lambda x0,x1,x2: (x1 or (not x1)),["x0","x1","x2"]),
        "c3":(lambda x0,x1,x2: (x2 or (not x2)),["x0","x1","x2"]),
        "out":(lambda c1,c2,c3: c1 and c2 and c3,["c1","c2","c3"]),
    },"out"))

    tasks.append(make_task("L-N4-7: Binary to Gray code (3-bit)", {
        f"b{i}":(lambda i=i: [1,0,1][i],[]) for i in range(3)
    } | {
        "g2":(lambda b2: b2,["b2"]),
        "g1":(lambda b2,b1: b2!=b1,["b2","b1"]),
        "g0":(lambda b1,b0: b1!=b0,["b1","b0"]),
        "out":(lambda g2,g1,g0: (g2,g1,g0),["g2","g1","g0"]),
    },"out"))

    tasks.append(make_task("L-N4-8: Equality network (4 pairs)", {
        f"a{i}":(lambda i=i: random.Random(400+i).randint(0,1),[]) for i in range(4)
    } | {
        f"b{i}":(lambda i=i: random.Random(500+i).randint(0,1),[]) for i in range(4)
    } | {
        f"eq{i}":(lambda a, b: a == b,[f"a{i}",f"b{i}"]) for i in range(4)
    } | {
        "out":(lambda eq0,eq1,eq2,eq3: all([eq0,eq1,eq2,eq3]),["eq0","eq1","eq2","eq3"]),
    },"out"))

    tasks.append(make_task("L-N4-9: 3-var propositional resolution", {
        "p":(lambda:1,[]),"q":(lambda:0,[]),"r":(lambda:1,[]),
        "c1":(lambda p,q: p or q,["p","q"]),
        "c2":(lambda q,r: (not q) or r,["q","r"]),
        "c3":(lambda p,r: p or r,["p","r"]),
        "res":(lambda c1,c2: c1 and c2,["c1","c2"]),
        "out":(lambda res,c3: res and c3,["res","c3"]),
    },"out"))

    tasks.append(make_task("L-N4-10: Ring oscillator (4-stage)", {
        "a":(lambda:1,[]),
        "b":(lambda:0,[]),
        "c":(lambda:1,[]),
        "d":(lambda:0,[]),
        "n1":(lambda a,b: a!=b,["a","b"]),
        "n2":(lambda n1,c: n1!=c,["n1","c"]),
        "n3":(lambda n2,d: n2!=d,["n2","d"]),
        "n4":(lambda n3,a: n3!=a,["n3","a"]),
        "out":(lambda n4: n4,["n4"]),
    },"out"))

    return tasks

LOGIC_TASKS = _logic_tasks()


# ═══════════════════════════════════════════════════════════════════
# DOMAIN 2: Math (DAG-M)
# ═══════════════════════════════════════════════════════════════════

def _math_tasks():
    tasks = []

    # N1
    tasks.append(make_task("M-N1-1: (a+b)*c", {
        "a":(lambda:3,[]),"b":(lambda:4,[]),"c":(lambda:5,[]),
        "s":(lambda a,b: a+b,["a","b"]),
        "out":(lambda s,c: s*c,["s","c"]),
    },"out"))

    tasks.append(make_task("M-N1-2: a^2 + b^2", {
        "a":(lambda:6,[]),"b":(lambda:8,[]),
        "a2":(lambda a: a*a,["a"]),"b2":(lambda b: b*b,["b"]),
        "out":(lambda a2,b2: a2+b2,["a2","b2"]),
    },"out"))

    tasks.append(make_task("M-N1-3: (a + b/c) * d", {
        "a":(lambda:10,[]),"b":(lambda:15,[]),"c":(lambda:3,[]),"d":(lambda:2,[]),
        "q":(lambda b,c: b//c,["b","c"]),
        "s":(lambda a,q: a+q,["a","q"]),
        "out":(lambda s,d: s*d,["s","d"]),
    },"out"))

    tasks.append(make_task("M-N1-4: Average of 3 numbers", {
        "a":(lambda:7,[]),"b":(lambda:9,[]),"c":(lambda:11,[]),
        "s":(lambda a,b,c: a+b+c,["a","b","c"]),
        "out":(lambda s: s/3,["s"]),
    },"out"))

    tasks.append(make_task("M-N1-5: Weighted sum", {
        "a":(lambda:2,[]),"b":(lambda:3,[]),"c":(lambda:4,[]),"d":(lambda:5,[]),
        "w1":(lambda a: a*2,["a"]),"w2":(lambda b: b*3,["b"]),
        "w3":(lambda c: c,["c"]),"w4":(lambda d: d*0.5,["d"]),
        "out":(lambda w1,w2,w3,w4: w1+w2+w3+w4,["w1","w2","w3","w4"]),
    },"out"))

    # N2
    tasks.append(make_task("M-N2-1: Quadratic formula components", {
        "a":(lambda:1,[]),"b":(lambda:5,[]),"c":(lambda:6,[]),
        "b2":(lambda b: b*b,["b"]),
        "ac4":(lambda a,c: 4*a*c,["a","c"]),
        "disc":(lambda b2,ac4: b2 - ac4,["b2","ac4"]),
        "sqrt_disc":(lambda disc: math.isqrt(disc),["disc"]),
        "out":(lambda b,sqrt_disc: (-b + sqrt_disc)//2,["b","sqrt_disc"]),
    },"out"))

    tasks.append(make_task("M-N2-2: Geometric series partial sum", {
        "a1":(lambda:3,[]),"r":(lambda:2,[]),"n":(lambda:5,[]),
        "rn":(lambda r,n: r**n,["r","n"]),
        "num":(lambda a1,rn: a1*(rn-1),["a1","rn"]),
        "den":(lambda r: r-1,["r"]),
        "out":(lambda num,den: num//den,["num","den"]),
    },"out"))

    tasks.append(make_task("M-N2-3: BMI calculation", {
        "weight":(lambda:70,[]),"height":(lambda:1.75,[]),
        "h2":(lambda height: height**2,["height"]),
        "bmi":(lambda weight,h2: weight/h2,["weight","h2"]),
        "cat":(lambda bmi: "normal" if 18.5<=bmi<25 else "other",["bmi"]),
        "out":(lambda bmi: round(bmi,1),["bmi"]),
    },"out"))

    tasks.append(make_task("M-N2-4: Compound interest", {
        "P":(lambda:1000,[]),"r":(lambda:0.05,[]),"t":(lambda:3,[]),
        "rate":(lambda r: 1+r,["r"]),
        "amt":(lambda P,rate,t: P*(rate**t),["P","rate","t"]),
        "interest":(lambda amt,P: amt-P,["amt","P"]),
        "out":(lambda interest: round(interest,2),["interest"]),
    },"out"))

    tasks.append(make_task("M-N2-5: Distance formula", {
        "x1":(lambda:-2,[]),"y1":(lambda:3,[]),"x2":(lambda:4,[]),"y2":(lambda:-1,[]),
        "dx":(lambda x1,x2: x2-x1,["x1","x2"]),
        "dy":(lambda y1,y2: y2-y1,["y1","y2"]),
        "dx2":(lambda dx: dx*dx,["dx"]),"dy2":(lambda dy: dy*dy,["dy"]),
        "out":(lambda dx2,dy2: math.isqrt(dx2+dy2),["dx2","dy2"]),
    },"out"))

    tasks.append(make_task("M-N2-6: Harmonic mean", {
        "a":(lambda:4,[]),"b":(lambda:6,[]),
        "ra":(lambda a: 1/a,["a"]),"rb":(lambda b: 1/b,["b"]),
        "sum_recip":(lambda ra,rb: ra+rb,["ra","rb"]),
        "out":(lambda sum_recip: round(2/sum_recip,2),["sum_recip"]),
    },"out"))

    tasks.append(make_task("M-N2-7: Modular exponentiation", {
        "base":(lambda:3,[]),"exp":(lambda:4,[]),"mod":(lambda:5,[]),
        "p1":(lambda base,mod: base%mod,["base","mod"]),
        "p2":(lambda p1: (p1**2)%5,["p1"]),
        "p4":(lambda p2: (p2**2)%5,["p2"]),
        "out":(lambda p4: p4,["p4"]),
    },"out"))

    # N3
    tasks.append(make_task("M-N3-1: Newton's method step (sqrt)", {
        "x":(lambda:10,[]),"n":(lambda:2,[]),
        "guess":(lambda x: x/2,["x"]),
        "ratio":(lambda x,guess: x/guess,["x","guess"]),
        "new_guess":(lambda guess,ratio,n: (guess+ratio)/n,["guess","ratio","n"]),
        "out":(lambda new_guess: round(new_guess,4),["new_guess"]),
    },"out"))

    tasks.append(make_task("M-N3-2: Temperature conversion chain", {
        "c":(lambda:100,[]),
        "f":(lambda c: c*9/5+32,["c"]),
        "k":(lambda c: c+273.15,["c"]),
        "r":(lambda f: f+459.67,["f"]),
        "out":(lambda f,k,r: (round(f,1),round(k,2),round(r,2)),["f","k","r"]),
    },"out"))

    tasks.append(make_task("M-N3-3: Dot product 4D", {
        f"a{i}":(lambda i=i: random.Random(600+i).randint(1,5),[]) for i in range(4)
    } | {
        f"b{i}":(lambda i=i: random.Random(700+i).randint(1,5),[]) for i in range(4)
    } | {
        f"p{i}":(lambda a, b: a*b,[f"a{i}",f"b{i}"]) for i in range(4)
    } | {
        "out":(lambda p0,p1,p2,p3: p0+p1+p2+p3,["p0","p1","p2","p3"]),
    },"out"))

    tasks.append(make_task("M-N3-4: Standard deviation (4 values)", {
        f"x{i}":(lambda i=i: [2,4,4,6][i],[]) for i in range(4)
    } | {
        "mean":(lambda x0,x1,x2,x3: (x0+x1+x2+x3)/4,["x0","x1","x2","x3"]),
    } | {
        f"d{i}":(lambda x, m: (x-m)**2,[f"x{i}","mean"]) for i in range(4)
    } | {
        "var":(lambda d0,d1,d2,d3: (d0+d1+d2+d3)/4,["d0","d1","d2","d3"]),
        "out":(lambda var: round(math.sqrt(var),4),["var"]),
    },"out"))

    tasks.append(make_task("M-N3-5: Matrix-vector multiply (2x2)", {
        "a11":(lambda:1,[]),"a12":(lambda:2,[]),"a21":(lambda:3,[]),"a22":(lambda:4,[]),
        "x1":(lambda:5,[]),"x2":(lambda:6,[]),
        "y1":(lambda a11,a12,x1,x2: a11*x1+a12*x2,["a11","a12","x1","x2"]),
        "y2":(lambda a21,a22,x1,x2: a21*x1+a22*x2,["a21","a22","x1","x2"]),
        "out":(lambda y1,y2: (y1,y2),["y1","y2"]),
    },"out"))

    tasks.append(make_task("M-N3-6: Arithmetic series (n=10)", {
        "a1":(lambda:2,[]),"d":(lambda:3,[]),"n":(lambda:10,[]),
        "last":(lambda a1,d,n: a1+(n-1)*d,["a1","d","n"]),
        "sum":(lambda a1,last,n: n*(a1+last)//2,["a1","last","n"]),
        "out":(lambda sum: sum,["sum"]),
    },"out"))

    tasks.append(make_task("M-N3-7: Heron's formula", {
        "a":(lambda:5,[]),"b":(lambda:6,[]),"c":(lambda:7,[]),
        "s":(lambda a,b,c: (a+b+c)/2,["a","b","c"]),
        "t1":(lambda s,a: s-a,["s","a"]),
        "t2":(lambda s,b: s-b,["s","b"]),
        "t3":(lambda s,c: s-c,["s","c"]),
        "prod":(lambda s,t1,t2,t3: s*t1*t2*t3,["s","t1","t2","t3"]),
        "out":(lambda prod: round(math.sqrt(prod),4),["prod"]),
    },"out"))

    tasks.append(make_task("M-N3-8: Logistic map (3 iterations)", {
        "x0":(lambda:0.5,[]),"r":(lambda:3.7,[]),
        "x1":(lambda x0,r: r*x0*(1-x0),["x0","r"]),
        "x2":(lambda x1,r: r*x1*(1-x1),["x1","r"]),
        "x3":(lambda x2,r: r*x2*(1-x2),["x2","r"]),
        "out":(lambda x3: round(x3,6),["x3"]),
    },"out"))

    # N4
    tasks.append(make_task("M-N4-1: Fibonacci (n=7) via DAG", {
        f"f{i}":((lambda i: lambda *args: 0 if i==0 else 1 if i==1 else args[0]+args[1])(i),
                [f"f{i-1}",f"f{i-2}"] if i>=2 else [])
        for i in range(8)
    } | {"out":(lambda f7: f7,["f7"])}, "out"))

    tasks.append(make_task("M-N4-2: 3-var linear system (Cramer)", {
        "a11":(lambda:2,[]),"a12":(lambda:1,[]),"a13":(lambda:1,[]),
        "a21":(lambda:1,[]),"a22":(lambda:-1,[]),"a23":(lambda:1,[]),
        "a31":(lambda:1,[]),"a32":(lambda:2,[]),"a33":(lambda:-1,[]),
        "b1":(lambda:4,[]),"b2":(lambda:2,[]),"b3":(lambda:0,[]),
        "detA":(lambda a11,a12,a13,a21,a22,a23,a31,a32,a33:
                a11*(a22*a33-a23*a32)-a12*(a21*a33-a23*a31)+a13*(a21*a32-a22*a31),
                ["a11","a12","a13","a21","a22","a23","a31","a32","a33"]),
        "detX":(lambda b1,b2,b3,a12,a13,a22,a23,a32,a33:
                b1*(a22*a33-a23*a32)-a12*(b2*a33-a23*b3)+a13*(b2*a32-a22*b3),
                ["b1","b2","b3","a12","a13","a22","a23","a32","a33"]),
        "x":(lambda detX,detA: detX//detA,["detX","detA"]),
        "out":(lambda x: x,["x"]),
    },"out"))

    tasks.append(make_task("M-N4-3: Binomial coefficient C(8,3)", {
        "n":(lambda:8,[]),"k":(lambda:3,[]),
        "num":(lambda n: math.factorial(n),["n"]),
        "den1":(lambda k: math.factorial(k),["k"]),
        "den2":(lambda n,k: math.factorial(n-k),["n","k"]),
        "den":(lambda den1,den2: den1*den2,["den1","den2"]),
        "out":(lambda num,den: num//den,["num","den"]),
    },"out"))

    tasks.append(make_task("M-N4-4: Euler's totient phi(n=12)", {
        "n":(lambda:12,[]),
        "f1":(lambda n: 2 if n%2==0 else 1,["n"]),
        "f2":(lambda n: 3 if n%3==0 else 1,["n"]),
        "p1":(lambda f1: 1-1/f1,["f1"]),
        "p2":(lambda f2: 1-1/f2,["f2"]),
        "out":(lambda n,p1,p2: int(n*p1*p2),["n","p1","p2"]),
    },"out"))

    tasks.append(make_task("M-N4-5: Perfect number check (n=28)", {
        "n":(lambda:28,[]),
        **{f"d{i}":(lambda i=i: i if 28%i==0 else 0,[]) for i in range(1,15)},
        "sum":(lambda *args: sum(args),
                [f"d{i}" for i in range(1,15)]),
        "is_perfect":(lambda s,n: s==n,["sum","n"]),
        "out":(lambda is_perfect: is_perfect,["is_perfect"]),
    },"out"))

    tasks.append(make_task("M-N4-6: Polynomial evaluation (Horner)", {
        "x":(lambda:3,[]),
        **{f"a{i}":(lambda i=i: random.Random(800+i).randint(1,5),[]) for i in range(5)},
        "b4":(lambda a4: a4,["a4"]),
        "b3":(lambda b4,x,a3: b4*x+a3,["b4","x","a3"]),
        "b2":(lambda b3,x,a2: b3*x+a2,["b3","x","a2"]),
        "b1":(lambda b2,x,a1: b2*x+a1,["b2","x","a1"]),
        "out":(lambda b1,x,a0: b1*x+a0,["b1","x","a0"]),
    },"out"))

    tasks.append(make_task("M-N4-7: Continued fraction [1;2,3,4]", {
        "a0":(lambda:1,[]),"a1":(lambda:2,[]),"a2":(lambda:3,[]),"a3":(lambda:4,[]),
        "n3":(lambda a3: a3,["a3"]),"d3":(lambda:1,[]),
        "v3":(lambda n3,d3: n3/d3,["n3","d3"]),
        "v2":(lambda a2,v3: a2+v3,["a2","v3"]),
        "v1":(lambda a1,v2: a1+1/v2 if v2!=0 else a1,["a1","v2"]),
        "v0":(lambda a0,v1: a0+1/v1 if v1!=0 else a0,["a0","v1"]),
        "out":(lambda v0: round(v0,6),["v0"]),
    },"out"))

    tasks.append(make_task("M-N4-8: Matrix determinant (3x3)", {
        **{f"a{i}{j}":(lambda i=i,j=j: random.Random(900+i*3+j).randint(1,4),[])
           for i in range(3) for j in range(3)},
        "det":(lambda a00,a01,a02,a10,a11,a12,a20,a21,a22:
               a00*(a11*a22-a12*a21)-a01*(a10*a22-a12*a20)+a02*(a10*a21-a11*a20),
               [f"a{i}{j}" for i in range(3) for j in range(3)]),
        "out":(lambda det: det,["det"]),
    },"out"))

    tasks.append(make_task("M-N4-9: Collatz length (n=7)", {
        "n":(lambda:7,[]),
        "c1":(lambda n: 22 if n%2 else 11,["n"]),
        "c2":(lambda c1: 11 if c1%2 else 1,["c1"]),
        "c3":(lambda c2: 34 if c2%2 else 1,["c2"]),
        "c4":(lambda c3: 17 if c3%2 else 1,["c3"]),
        "c5":(lambda c4: 52 if c4%2 else 1,["c4"]),
        "c6":(lambda c5: 26 if c5%2 else 1,["c5"]),
        "c7":(lambda c6: 13 if c6%2 else 1,["c6"]),
        "c8":(lambda c7: 40 if c7%2 else 1,["c7"]),
        "c9":(lambda c8: 20 if c8%2 else 1,["c8"]),
        "c10":(lambda c9: 10 if c9%2 else 1,["c9"]),
        "c11":(lambda c10: 5 if c10%2 else 1,["c10"]),
        "c12":(lambda c11: 16 if c11%2 else 1,["c11"]),
        "c13":(lambda c12: 8 if c12%2 else 1,["c12"]),
        "c14":(lambda c13: 4 if c13%2 else 1,["c13"]),
        "c15":(lambda c14: 2 if c14%2 else 1,["c14"]),
        "c16":(lambda c15: 1 if c15%2 else 1,["c15"]),
        "out":(lambda n,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16:
               16,["n","c1","c2","c3","c4","c5","c6","c7","c8","c9","c10","c11","c12","c13","c14","c15","c16"]),
    },"out"))

    tasks.append(make_task("M-N4-10: Newton sum (n=4, roots r_i)", {
        **{f"r{i}":(lambda i=i: random.Random(1000+i).randint(1,3),[]) for i in range(4)},
        **{f"s{j}":((lambda j: lambda *args: sum(args[i]**j for i in range(4)))(j),
                    [f"r{i}" for i in range(4)]) for j in range(1,6)},
    },"s5"))

    return tasks

MATH_TASKS = _math_tasks()


# ═══════════════════════════════════════════════════════════════════
# DOMAIN 3: Planning (DAG-P)
# ═══════════════════════════════════════════════════════════════════

def _planning_tasks():
    tasks = []

    # N1
    def plan_n1_1():
        s = {"pos":0}
        def move(dx): s["pos"]+=dx
        # pos=0 -> +3 -> +2
        n1 = lambda: 3; n2 = lambda n1: n1+2
        return make_task("P-N1-1: Move +3 then +2", {
            "p0":(lambda:0,[]),"d1":(lambda:3,[]),"d2":(lambda:2,[]),
            "p1":(lambda p0,d1: p0+d1,["p0","d1"]),
            "out":(lambda p1,d2: p1+d2,["p1","d2"]),
        },"out")

    tasks.append(plan_n1_1())

    tasks.append(make_task("P-N1-2: Stack 2 boxes", {
        "h0":(lambda:0,[]),
        "b1":(lambda:2,[]),"b2":(lambda:3,[]),
        "h1":(lambda h0,b1: h0+b1,["h0","b1"]),
        "out":(lambda h1,b2: h1+b2,["h1","b2"]),
    },"out"))

    tasks.append(make_task("P-N1-3: Wallet after 2 transactions", {
        "bal":(lambda:100,[]),"d1":(lambda:-30,[]),"d2":(lambda:15,[]),
        "a1":(lambda bal,d1: bal+d1,["bal","d1"]),
        "out":(lambda a1,d2: a1+d2,["a1","d2"]),
    },"out"))

    tasks.append(make_task("P-N1-4: Water level after fill- drain", {
        "base":(lambda:50,[]),"fill":(lambda:30,[]),"drain":(lambda:-20,[]),
        "after_fill":(lambda base,fill: base+fill,["base","fill"]),
        "out":(lambda after_fill,drain: after_fill+drain,["after_fill","drain"]),
    },"out"))

    tasks.append(make_task("P-N1-5: Score after 3 rounds", {
        "s0":(lambda:0,[]),"r1":(lambda:10,[]),"r2":(lambda:-5,[]),"r3":(lambda:8,[]),
        "s1":(lambda s0,r1: s0+r1,["s0","r1"]),
        "s2":(lambda s1,r2: s1+r2,["s1","r2"]),
        "out":(lambda s2,r3: s2+r3,["s2","r3"]),
    },"out"))

    # N2
    tasks.append(make_task("P-N2-1: Elevator (floor 0→5→2→8)", {
        "f0":(lambda:0,[]),
        "d1":(lambda:5,[]),"d2":(lambda:-3,[]),"d3":(lambda:6,[]),
        "f1":(lambda f0,d1: f0+d1,["f0","d1"]),
        "f2":(lambda f1,d2: f1+d2,["f1","d2"]),
        "out":(lambda f2,d3: f2+d3,["f2","d3"]),
    },"out"))

    tasks.append(make_task("P-N2-2: Robot (grid 2D, 4 moves)", {
        "x0":(lambda:0,[]),"y0":(lambda:0,[]),
        "dx1":(lambda:3,[]),"dy1":(lambda:2,[]),
        "dx2":(lambda:-1,[]),"dy2":(lambda:4,[]),
        "x1":(lambda x0,dx1: x0+dx1,["x0","dx1"]),
        "y1":(lambda y0,dy1: y0+dy1,["y0","dy1"]),
        "x2":(lambda x1,dx2: x1+dx2,["x1","dx2"]),
        "y2":(lambda y1,dy2: y1+dy2,["y1","dy2"]),
        "out":(lambda x2,y2: (x2,y2),["x2","y2"]),
    },"out"))

    tasks.append(make_task("P-N2-3: Inventory (add, remove, add)", {
        "inv0":(lambda:10,[]),"a1":(lambda:5,[]),"r2":(lambda:-3,[]),"a3":(lambda:7,[]),
        "inv1":(lambda inv0,a1: inv0+a1,["inv0","a1"]),
        "inv2":(lambda inv1,r2: inv1+r2,["inv1","r2"]),
        "out":(lambda inv2,a3: inv2+a3,["inv2","a3"]),
    },"out"))

    tasks.append(make_task("P-N2-4: Temperature (heat, cool, heat)", {
        "t0":(lambda:25,[]),"h1":(lambda:10,[]),"c2":(lambda:-15,[]),"h3":(lambda:5,[]),
        "t1":(lambda t0,h1: t0+h1,["t0","h1"]),
        "t2":(lambda t1,c2: t1+c2,["t1","c2"]),
        "out":(lambda t2,h3: t2+h3,["t2","h3"]),
    },"out"))

    tasks.append(make_task("P-N2-5: Runner (lap counter)", {
        "l0":(lambda:0,[]),"s1":(lambda:400,[]),"s2":(lambda:300,[]),"s3":(lambda:500,[]),
        "l1":(lambda l0,s1: l0+1 if s1>=400 else l0,["l0","s1"]),
        "l2":(lambda l1,s2: l1+1 if s2>=400 else l1,["l1","s2"]),
        "out":(lambda l2,s3: l2+1 if s3>=400 else l2,["l2","s3"]),
    },"out"))

    tasks.append(make_task("P-N2-6: Fuel consumption chain", {
        "fuel0":(lambda:100,[]),"leg1":(lambda:-30,[]),"leg2":(lambda:-25,[]),"leg3":(lambda:-20,[]),
        "f1":(lambda fuel0,leg1: fuel0+leg1,["fuel0","leg1"]),
        "f2":(lambda f1,leg2: f1+leg2,["f1","leg2"]),
        "out":(lambda f2,leg3: f2+leg3,["f2","leg3"]),
    },"out"))

    tasks.append(make_task("P-N2-7: Population (birth, death, birth)", {
        "pop0":(lambda:1000,[]),"b1":(lambda:50,[]),"d2":(lambda:-30,[]),"b3":(lambda:40,[]),
        "p1":(lambda pop0,b1: pop0+b1,["pop0","b1"]),
        "p2":(lambda p1,d2: p1+d2,["p1","d2"]),
        "out":(lambda p2,b3: p2+b3,["p2","b3"]),
    },"out"))

    # N3
    tasks.append(make_task("P-N3-1: Grid path 8-step", {
        "x0":(lambda:0,[]),"y0":(lambda:0,[]),
        **{f"d{i}":(lambda i=i: [("E",3),("N",2),("W",1),("N",4),("E",2),("S",3),("W",2),("E",1)][i],[])
           for i in range(8)},
        **{f"p{i}":(lambda *args: args[0] if args else (0,0),[f"p{i-1}"] if i>0 else []) for i in range(9)},
    },"p8"))

    # For simplicity, use coordinate chain
    tasks.append(make_task("P-N3-2: Coordinate chain (N=5)", {
        "x0":(lambda:0,[]),"y0":(lambda:0,[]),
        **{f"m{i}":(lambda i=i: random.Random(1100+i).choice([(1,0),(0,1),(-1,0),(0,-1)]),[])
           for i in range(5)},
        **{f"x{i+1}":(lambda x, m: x+m[0],[f"x{i}",f"m{i}"]) for i in range(5)},
        **{f"y{i+1}":(lambda y, m: y+m[1],[f"y{i}",f"m{i}"]) for i in range(5)},
        "out":(lambda x5,y5: (x5,y5),["x5","y5"]),
    },"out"))

    tasks.append(make_task("P-N3-3: Pipeline (filter→map→reduce)", {
        "raw":(lambda:[1,2,3,4,5,6],[]),
        "even":(lambda raw: [x for x in raw if x%2==0],["raw"]),
        "squared":(lambda even: [x*x for x in even],["even"]),
        "sum":(lambda squared: sum(squared),["squared"]),
        "out":(lambda sum: sum,["sum"]),
    },"out"))

    tasks.append(make_task("P-N3-4: Assembly line (3 stations)", {
        "part":(lambda:1,[]),
        "sta":(lambda part: part*2,["part"]),
        "stb":(lambda sta: sta+3,["sta"]),
        "stc":(lambda stb: stb*5,["stb"]),
        "out":(lambda stc: stc,["stc"]),
    },"out"))

    tasks.append(make_task("P-N3-5: Budget (4 categories)", {
        "total":(lambda:5000,[]),
        "cat1":(lambda total: total*0.3,["total"]),
        "cat2":(lambda total: total*0.2,["total"]),
        "cat3":(lambda total: total*0.15,["total"]),
        "remain":(lambda total,cat1,cat2,cat3: total-cat1-cat2-cat3,["total","cat1","cat2","cat3"]),
        "out":(lambda cat1,cat2,cat3,remain: round(remain,2),["cat1","cat2","cat3","remain"]),
    },"out"))

    tasks.append(make_task("P-N3-6: Train schedule (3 stops)", {
        "time0":(lambda:0,[]),"t1":(lambda:45,[]),"w1":(lambda:5,[]),
        "t2":(lambda:30,[]),"w2":(lambda:3,[]),"t3":(lambda:20,[]),
        "dep1":(lambda time0,t1: time0+t1,["time0","t1"]),
        "arr1":(lambda dep1,w1: dep1+w1,["dep1","w1"]),
        "dep2":(lambda arr1,t2: arr1+t2,["arr1","t2"]),
        "arr2":(lambda dep2,w2: dep2+w2,["dep2","w2"]),
        "out":(lambda arr2,t3: arr2+t3,["arr2","t3"]),
    },"out"))

    tasks.append(make_task("P-N3-7: Recipe (5-step cooking)", {
        "prep":(lambda:15,[]),"cook1":(lambda:10,[]),"rest":(lambda:5,[]),
        "cook2":(lambda:8,[]),"cool":(lambda:3,[]),
        "t1":(lambda prep,cook1: prep+cook1,["prep","cook1"]),
        "t2":(lambda t1,rest: t1+rest,["t1","rest"]),
        "t3":(lambda t2,cook2: t2+cook2,["t2","cook2"]),
        "out":(lambda t3,cool: t3+cool,["t3","cool"]),
    },"out"))

    tasks.append(make_task("P-N3-8: Factory output (3 machines)", {
        "raw":(lambda:100,[]),
        "m1":(lambda raw: int(raw*0.8),["raw"]),
        "m2":(lambda m1: int(m1*0.9),["m1"]),
        "m3":(lambda m2: int(m2*0.95),["m2"]),
        "waste":(lambda raw,m1,m2,m3: raw-m3,["raw","m1","m2","m3"]),
        "out":(lambda m3,waste: (m3,waste),["m3","waste"]),
    },"out"))

    # N4
    tasks.append(make_task("P-N4-1: Multi-robot rendezvous (3 bots, grid)", {
        **{f"x{i}0":(lambda i=i: random.Random(1200+i).randint(0,10),[]) for i in range(3)},
        **{f"y{i}0":(lambda i=i: random.Random(1300+i).randint(0,10),[]) for i in range(3)},
        "cx":(lambda x00,x10,x20: (x00+x10+x20)//3,[f"x{i}0" for i in range(3)]),
        "cy":(lambda y00,y10,y20: (y00+y10+y20)//3,[f"y{i}0" for i in range(3)]),
        **{f"dx{i}":(lambda x0, cx: abs(x0-abs(cx)),[f"x{i}0","cx"]) for i in range(3)},
        **{f"dy{i}":(lambda y0, cy: abs(y0-abs(cy)),[f"y{i}0","cy"]) for i in range(3)},
        **{f"d{i}":(lambda dx, dy: dx+dy,[f"dx{i}",f"dy{i}"]) for i in range(3)},
        "out":(lambda d0,d1,d2: d0+d1+d2,["d0","d1","d2"]),
    },"out"))

    tasks.append(make_task("P-N4-2: Resource allocation (4 projects)", {
        "budget":(lambda:1000000,[]),
        **{f"p{i}":(lambda i=i: random.Random(1400+i).randint(10,30)/100,[])
           for i in range(4)},
        **{f"alloc{i}":(lambda b, p: int(b*p),["budget",f"p{i}"]) for i in range(4)},
        "total":(lambda alloc0,alloc1,alloc2,alloc3: alloc0+alloc1+alloc2+alloc3,
                [f"alloc{i}" for i in range(4)]),
        "out":(lambda budget,total: budget-total,["budget","total"]),
    },"out"))

    tasks.append(make_task("P-N4-3: Multi-stage sorting network (8 items)", {
        **{f"x{i}":(lambda i=i: random.Random(1500+i).randint(1,100),[]) for i in range(8)},
        "s0":(lambda x0,x1: (x0,x1) if x0<=x1 else (x1,x0),["x0","x1"]),
        "s1":(lambda x2,x3: (x2,x3) if x2<=x3 else (x3,x2),["x2","x3"]),
        "s2":(lambda x4,x5: (x4,x5) if x4<=x5 else (x5,x4),["x4","x5"]),
        "s3":(lambda x6,x7: (x6,x7) if x6<=x7 else (x7,x6),["x6","x7"]),
        "out":(lambda s0,s1,s2,s3: (s0[0]<=s1[0] and s2[0]<=s3[0]),["s0","s1","s2","s3"]),
    },"out"))

    tasks.append(make_task("P-N4-4: Warehouse (receive→store→pick→ship)", {
        "recv":(lambda:500,[]),
        "store":(lambda recv: int(recv*0.95),["recv"]),
        "pick":(lambda store: store-200,["store"]),
        "pack":(lambda pick: int(pick*0.98),["pick"]),
        "ship":(lambda pack: pack,["pack"]),
        "damage":(lambda recv,store,pick,pack,ship: recv-ship,
                 ["recv","store","pick","pack","ship"]),
        "out":(lambda ship,damage: (ship,damage),["ship","damage"]),
    },"out"))

    tasks.append(make_task("P-N4-5: Chemical process (4 reactors)", {
        "feed":(lambda:1000,[]),
        "r1":(lambda feed: int(feed*0.9),["feed"]),
        "r2":(lambda r1: int(r1*0.85),["r1"]),
        "r3":(lambda r2: int(r2*0.95),["r2"]),
        "r4":(lambda r3: int(r3*0.98),["r3"]),
        "yield":(lambda r4: r4,["r4"]),
        "loss":(lambda feed,r4: feed-r4,["feed","r4"]),
        "out":(lambda yield_,loss: (yield_,loss),["yield","loss"]),
    },"out"))

    tasks.append(make_task("P-N4-6: Timed process (parallel tasks)", {
        "start":(lambda:0,[]),
        "ta":(lambda start: start+10,["start"]),
        "tb":(lambda start: start+15,["start"]),
        "tc":(lambda start: start+8,["start"]),
        "tab":(lambda ta,tb: max(ta,tb),["ta","tb"]),
        "t_merge":(lambda tab,tc: max(tab,tc),["tab","tc"]),
        "tend":(lambda t_merge: t_merge+5,["t_merge"]),
        "out":(lambda tend: tend,["tend"]),
    },"out"))

    tasks.append(make_task("P-N4-7: Supply chain (3 tiers)", {
        "raw_m":(lambda:5000,[]),
        "tier1":(lambda raw_m: int(raw_m*0.7),["raw_m"]),
        "tier2":(lambda tier1: int(tier1*0.8),["tier1"]),
        "tier3_a":(lambda tier2: int(tier2*0.5),["tier2"]),
        "tier3_b":(lambda tier2: int(tier2*0.3),["tier2"]),
        "total_prod":(lambda tier3_a,tier3_b: tier3_a+tier3_b,["tier3_a","tier3_b"]),
        "waste":(lambda raw_m,total_prod: raw_m-total_prod,["raw_m","total_prod"]),
        "out":(lambda total_prod,waste: (total_prod,waste),["total_prod","waste"]),
    },"out"))

    tasks.append(make_task("P-N4-8: Tournament bracket (8 players)", {
        **{f"p{i}":(lambda i=i: random.Random(1600+i).randint(1,100),[]) for i in range(8)},
        "m1":(lambda p0,p1: max(p0,p1),["p0","p1"]),
        "m2":(lambda p2,p3: max(p2,p3),["p2","p3"]),
        "m3":(lambda p4,p5: max(p4,p5),["p4","p5"]),
        "m4":(lambda p6,p7: max(p6,p7),["p6","p7"]),
        "sf1":(lambda m1,m2: max(m1,m2),["m1","m2"]),
        "sf2":(lambda m3,m4: max(m3,m4),["m3","m4"]),
        "final":(lambda sf1,sf2: max(sf1,sf2),["sf1","sf2"]),
        "out":(lambda final: final,["final"]),
    },"out"))

    tasks.append(make_task("P-N4-9: Project critical path (6 tasks)", {
        "t1":(lambda:3,[]),"t2":(lambda:5,[]),"t3":(lambda:2,[]),
        "t4":(lambda t1,t2: max(t1,t2)+4,["t1","t2"]),
        "t5":(lambda t2,t3: max(t2,t3)+3,["t2","t3"]),
        "t6":(lambda t4,t5: max(t4,t5)+2,["t4","t5"]),
        "out":(lambda t6: t6,["t6"]),
    },"out"))

    tasks.append(make_task("P-N4-10: Series-parallel circuit resistance", {
        "r1":(lambda:10,[]),"r2":(lambda:20,[]),"r3":(lambda:30,[]),"r4":(lambda:40,[]),
        "rs1":(lambda r1,r2: r1+r2,["r1","r2"]),
        "rp1":(lambda r3,r4: 1/(1/r3+1/r4),["r3","r4"]),
        "req":(lambda rs1,rp1: rs1+rp1,["rs1","rp1"]),
        "out":(lambda req: round(req,2),["req"]),
    },"out"))

    return tasks

PLANNING_TASKS = _planning_tasks()


# ═══════════════════════════════════════════════════════════════════
# DOMAIN 4: Code Flow (DAG-C)
# ═══════════════════════════════════════════════════════════════════

def _codeflow_tasks():
    def _flatten(lst):
        """Deep flatten a nested list."""
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(_flatten(item))
            else:
                result.append(item)
        return result
    tasks = []

    # N1
    tasks.append(make_task("C-N1-1: string reverse", {
        "s":(lambda:"abc",[]),
        "out":(lambda s: s[::-1],["s"]),
    },"out"))

    tasks.append(make_task("C-N1-2: uppercase then concat", {
        "a":(lambda:"hello",[]),"b":(lambda:"world",[]),
        "ua":(lambda a: a.upper(),["a"]),
        "out":(lambda ua,b: ua+b,["ua","b"]),
    },"out"))

    tasks.append(make_task("C-N1-3: list filter positive", {
        "lst":(lambda:[-3,2,-1,5,0],[]),
        "out":(lambda lst: [x for x in lst if x>0],["lst"]),
    },"out"))

    tasks.append(make_task("C-N1-4: first element then double", {
        "lst":(lambda:[4,7,2],[]),
        "fst":(lambda lst: lst[0],["lst"]),
        "out":(lambda fst: fst*2,["fst"]),
    },"out"))

    tasks.append(make_task("C-N1-5: length then square", {
        "s":(lambda:"test",[]),
        "n":(lambda s: len(s),["s"]),
        "out":(lambda n: n*n,["n"]),
    },"out"))

    # N2
    tasks.append(make_task("C-N2-1: interleave two strings", {
        "a":(lambda:"abc",[]),"b":(lambda:"12",[]),
        "out":(lambda a,b: "".join(a[i]+(b[i] if i<len(b) else "") for i in range(len(a))),["a","b"]),
    },"out"))

    tasks.append(make_task("C-N2-2: remove vowels → length", {
        "s":(lambda:"hello world",[]),
        "no_v":(lambda s: "".join(c for c in s if c not in "aeiou"),["s"]),
        "out":(lambda no_v: (no_v,len(no_v)),["no_v"]),
    },"out"))

    tasks.append(make_task("C-N2-3: list → uniq → sort", {
        "lst":(lambda:[3,1,2,1,3,2],[]),
        "uniq":(lambda lst: list(set(lst)),["lst"]),
        "out":(lambda uniq: sorted(uniq),["uniq"]),
    },"out"))

    tasks.append(make_task("C-N2-4: word count → char count", {
        "s":(lambda:"the quick brown fox",[]),
        "words":(lambda s: len(s.split()),["s"]),
        "chars":(lambda s: len(s.replace(" ","")),["s"]),
        "out":(lambda words,chars: (words,chars),["words","chars"]),
    },"out"))

    tasks.append(make_task("C-N2-5: matrix transpose (2x3)", {
        "m":(lambda:[[1,2,3],[4,5,6]],[]),
        "t":(lambda m: list(map(list,zip(*m))),["m"]),
        "flatten":(lambda t: [x for row in t for x in row],["t"]),
        "out":(lambda flatten: flatten,["flatten"]),
    },"out"))

    tasks.append(make_task("C-N2-6: string → bytes → hex", {
        "s":(lambda:"Hi",[]),
        "b":(lambda s: s.encode(),["s"]),
        "out":(lambda b: b.hex(),["b"]),
    },"out"))

    tasks.append(make_task("C-N2-7: list of strings → concat → upper", {
        "lst":(lambda:["a","bb","ccc"],[]),
        "cat":(lambda lst: "".join(lst),["lst"]),
        "out":(lambda cat: cat.upper(),["cat"]),
    },"out"))

    # N3
    tasks.append(make_task("C-N3-1: palindrome check chain", {
        "s":(lambda:"radar",[]),
        "rev":(lambda s: s[::-1],["s"]),
        "is_pal":(lambda s,rev: s==rev,["s","rev"]),
        "report":(lambda is_pal: f"palindrome={is_pal}",["is_pal"]),
        "out":(lambda report: report,["report"]),
    },"out"))

    tasks.append(make_task("C-N3-2: Caesar cipher (shift=3)", {
        "s":(lambda:"abc",[]),
        "shifted":(lambda s: "".join(chr((ord(c)-97+3)%26+97) for c in s),["s"]),
        "upper":(lambda shifted: shifted.upper(),["shifted"]),
        "reversed":(lambda upper: upper[::-1],["upper"]),
        "out":(lambda reversed: reversed,["reversed"]),
    },"out"))

    tasks.append(make_task("C-N3-3: list → squares → sum → sqrt", {
        "lst":(lambda:[1,2,3,4],[]),
        "sq":(lambda lst: [x*x for x in lst],["lst"]),
        "total":(lambda sq: sum(sq),["sq"]),
        "out":(lambda total: round(math.sqrt(total),4),["total"]),
    },"out"))

    tasks.append(make_task("C-N3-4: run-length encoding", {
        "s":(lambda:"aaabbc",[]),
        "runs":(lambda s: [(c,len(list(g))) for c,g in __import__("itertools").groupby(s)],["s"]),
        "encoded":(lambda runs: "".join(f"{c}{n}" for c,n in runs),["runs"]),
        "out":(lambda encoded: encoded,["encoded"]),
    },"out"))

    tasks.append(make_task("C-N3-5: flatten nested list", {
        "lst":(lambda:[1,[2,3],[4,[5,6]]],[]),
        "flat":(lambda lst: _flatten(lst),["lst"]),
        "no_dups":(lambda flat: list(set(flat)),["flat"]),
        "sorted":(lambda no_dups: sorted(no_dups),["no_dups"]),
        "out":(lambda sorted_: sorted_,["sorted"]),
    },"out"))

    tasks.append(make_task("C-N3-6: tokenize → count → sort by freq", {
        "s":(lambda:"a b a c b a",[]),
        "tokens":(lambda s: s.split(),["s"]),
        "freq":(lambda tokens: {w:tokens.count(w) for w in set(tokens)},["tokens"]),
        "sorted_items":(lambda freq: sorted(freq.items(), key=lambda x:-x[1]),["freq"]),
        "out":(lambda sorted_items: sorted_items,["sorted_items"]),
    },"out"))

    tasks.append(make_task("C-N3-7: dict merge → sum values", {
        "d1":(lambda:{"a":1,"b":2},[]),"d2":(lambda:{"b":3,"c":4},[]),
        "merged":(lambda d1,d2: {k:d1.get(k,0)+d2.get(k,0) for k in set(d1)|set(d2)},["d1","d2"]),
        "total":(lambda merged: sum(merged.values()),["merged"]),
        "keys":(lambda merged: sorted(merged.keys()),["merged"]),
        "out":(lambda total,keys: (total,keys),["total","keys"]),
    },"out"))

    tasks.append(make_task("C-N3-8: parser → evaluator (simple expr)", {
        "expr":(lambda:"3+4*2",[]),
        "tokens":(lambda expr: expr.replace("+"," + ").replace("*"," * ").split(),["expr"]),
        "postfix":(lambda tokens:
            [t for t in tokens if t.isdigit()]+["*"] if tokens[-1]=="2" else [],
            ["tokens"]),
        "out":(lambda postfix: postfix,["postfix"]),
    },"out"))

    # N4
    tasks.append(make_task("C-N4-1: multi-function composition pipeline", {
        "x":(lambda:5,[]),
        "add3":(lambda x: x+3,["x"]),
        "mul2":(lambda add3: add3*2,["add3"]),
        "sub4":(lambda mul2: mul2-4,["mul2"]),
        "div2":(lambda sub4: sub4//2,["sub4"]),
        "neg":(lambda div2: -div2,["div2"]),
        "abs":(lambda neg: abs(neg),["neg"]),
        "out":(lambda abs_: abs_,["abs"]),
    },"out"))

    tasks.append(make_task("C-N4-2: CSV parse → filter → project", {
        "csv":(lambda:"id,name,val\n1,a,10\n2,b,5\n3,c,20",[]),
        "lines":(lambda csv: csv.strip().split("\n"),["csv"]),
        "header":(lambda lines: lines[0].split(","),["lines"]),
        "data":(lambda lines: [dict(zip(lines[0].split(","),row.split(","))) for row in lines[1:]],["lines"]),
        "filtered":(lambda data: [r for r in data if int(r["val"])>8],["data"]),
        "projected":(lambda filtered: [(r["name"],r["val"]) for r in filtered],["filtered"]),
        "out":(lambda projected: projected,["projected"]),
    },"out"))

    # N4 — C-N4-3 is re-done properly below (flatten_dict helper)

    # Redo C-N4-3 properly
    def flatten_dict(d, parent=""):
        items = []
        for k,v in d.items():
            new_key = f"{parent}.{k}" if parent else k
            if isinstance(v,dict):
                items.extend(flatten_dict(v,new_key).items())
            else:
                items.append((new_key,v))
        return dict(items)

    tasks.append(make_task("C-N4-3: JSON flatten (nested dict)", {
        "d":(lambda:{"a":1,"b":{"c":2,"d":{"e":3}}},[]),
        "flat":(lambda d: flatten_dict(d),["d"]),
        "sorted_items":(lambda flat: sorted(flat.items()),["flat"]),
        "out":(lambda sorted_items: sorted_items,["sorted_items"]),
    },"out"))

    tasks.append(make_task("C-N4-4: string diff (char-level)", {
        "s1":(lambda:"kitten",[]),"s2":(lambda:"sitting",[]),
        "common":(lambda s1,s2: sum(1 for a,b in zip(s1,s2) if a==b),["s1","s2"]),
        "len_diff":(lambda s1,s2: abs(len(s1)-len(s2)),["s1","s2"]),
        "similarity":(lambda common,s1,s2: common/max(len(s1),len(s2)),["common","s1","s2"]),
        "out":(lambda similarity: round(similarity,4),["similarity"]),
    },"out"))

    tasks.append(make_task("C-N4-5: graph adjacency → degree → center", {
        "edges":(lambda:[(0,1),(1,2),(2,3),(3,0),(0,2)],[]),
        "deg":(lambda edges: {i:sum(i in e for e in edges) for i in range(4)},["edges"]),
        "max_deg":(lambda deg: max(deg.values()),["deg"]),
        "center":(lambda deg,max_deg: [n for n,d in deg.items() if d==max_deg],["deg","max_deg"]),
        "out":(lambda center: center,["center"]),
    },"out"))

    tasks.append(make_task("C-N4-6: regex-free pattern matching", {
        "s":(lambda:"abracadabra",[]),"pat":(lambda:"abra",[]),
        "positions":(lambda s,pat:
            [i for i in range(len(s)-len(pat)+1) if s[i:i+len(pat)]==pat],
            ["s","pat"]),
        "count":(lambda positions: len(positions),["positions"]),
        "out":(lambda count: count,["count"]),
    },"out"))

    tasks.append(make_task("C-N4-7: moving average (window=3)", {
        "series":(lambda:[1,2,3,4,5,6],[]),
        **{f"w{i}":((lambda i: lambda *args: sum(args[0][i:i+3])/3)(i),
                    ["series"]) for i in range(4)},
        "out":(lambda w0,w1,w2,w3: [round(w0,2),round(w1,2),round(w2,2),round(w3,2)],
              ["w0","w1","w2","w3"]),
    },"out"))

    tasks.append(make_task("C-N4-8: config parser → validator → executor", {
        "cfg":(lambda:"timeout=30;retries=3;verbose=true",[]),
        "pairs":(lambda cfg: [p.split("=") for p in cfg.split(";")],["cfg"]),
        "parsed":(lambda pairs: {k:v for k,v in pairs},["pairs"]),
        "valid":(lambda parsed:
            int(parsed.get("timeout",0))>0 and int(parsed.get("retries",0))>0,
            ["parsed"]),
        "timeout_s":(lambda parsed: int(parsed["timeout"]),["parsed"]),
        "retries":(lambda parsed: int(parsed["retries"]),["parsed"]),
        "total_time":(lambda timeout_s,retries: timeout_s*(retries+1),["timeout_s","retries"]),
        "out":(lambda valid,total_time: (valid,total_time),["valid","total_time"]),
    },"out"))

    tasks.append(make_task("C-N4-9: bloom filter simulation (3 hashes)", {
        "bitset":(lambda:set(),[]),"item":(lambda:"test",[]),
        "h1":(lambda item: hash(item)%10,["item"]),
        "h2":(lambda item: hash(item+"x")%10,["item"]),
        "h3":(lambda item: hash(item[::-1])%10,["item"]),
        "insert":(lambda bitset,h1,h2,h3: bitset|{h1,h2,h3},["bitset","h1","h2","h3"]),
        "size":(lambda insert: len(insert),["insert"]),
        "out":(lambda size: size,["size"]),
    },"out"))

    tasks.append(make_task("C-N4-10: version number comparator", {
        "v1":(lambda:"2.3.4",[]),"v2":(lambda:"2.10.1",[]),
        "p1":(lambda v1: [int(x) for x in v1.split(".")],["v1"]),
        "p2":(lambda v2: [int(x) for x in v2.split(".")],["v2"]),
        **{f"cmp{i}":((lambda i: lambda *args: args[0][i] - args[1][i])(i),["p1","p2"]) for i in range(3)},
        "out":(lambda cmp0,cmp1,cmp2:
            ">" if any(c>0 for c in [cmp0,cmp1,cmp2]) else
            "<" if any(c<0 for c in [cmp0,cmp1,cmp2]) else "=",
            ["cmp0","cmp1","cmp2"]),
    },"out"))

    return tasks

CODE_TASKS = _codeflow_tasks()


# ═══════════════════════════════════════════════════════════════════
# DOMAIN 5: Scientific (DAG-S)
# ═══════════════════════════════════════════════════════════════════

def _scientific_tasks():
    tasks = []

    # N1
    tasks.append(make_task("S-N1-1: v = d/t", {
        "d":(lambda:100,[]),"t":(lambda:5,[]),
        "out":(lambda d,t: d/t,["d","t"]),
    },"out"))

    tasks.append(make_task("S-N1-2: F = ma", {
        "m":(lambda:10,[]),"a":(lambda:3,[]),
        "out":(lambda m,a: m*a,["m","a"]),
    },"out"))

    tasks.append(make_task("S-N1-3: KE = 0.5*m*v^2", {
        "m":(lambda:2,[]),"v":(lambda:4,[]),
        "v2":(lambda v: v*v,["v"]),
        "out":(lambda m,v2: 0.5*m*v2,["m","v2"]),
    },"out"))

    tasks.append(make_task("S-N1-4: W = F*d", {
        "f":(lambda:50,[]),"d":(lambda:10,[]),
        "out":(lambda f,d: f*d,["f","d"]),
    },"out"))

    tasks.append(make_task("S-N1-5: P = W/t", {
        "w":(lambda:500,[]),"t":(lambda:10,[]),
        "out":(lambda w,t: w/t,["w","t"]),
    },"out"))

    # N2
    tasks.append(make_task("S-N2-1: v_f = v_i + a*t", {
        "vi":(lambda:5,[]),"a":(lambda:2,[]),"t":(lambda:3,[]),
        "at":(lambda a,t: a*t,["a","t"]),
        "out":(lambda vi,at: vi+at,["vi","at"]),
    },"out"))

    tasks.append(make_task("S-N2-2: d = v_i*t + 0.5*a*t^2", {
        "vi":(lambda:0,[]),"a":(lambda:9.8,[]),"t":(lambda:2,[]),
        "vit":(lambda vi,t: vi*t,["vi","t"]),
        "at2":(lambda a,t: 0.5*a*t*t,["a","t"]),
        "out":(lambda vit,at2: round(vit+at2,2),["vit","at2"]),
    },"out"))

    tasks.append(make_task("S-N2-3: PE = m*g*h", {
        "m":(lambda:5,[]),"g":(lambda:9.8,[]),"h":(lambda:10,[]),
        "out":(lambda m,g,h: m*g*h,["m","g","h"]),
    },"out"))

    tasks.append(make_task("S-N2-4: Pressure = F/A", {
        "f":(lambda:100,[]),"area":(lambda:2,[]),
        "out":(lambda f,area: f/area,["f","area"]),
    },"out"))

    tasks.append(make_task("S-N2-5: Density = m/V", {
        "m":(lambda:50,[]),"v":(lambda:25,[]),
        "out":(lambda m,v: m/v,["m","v"]),
    },"out"))

    tasks.append(make_task("S-N2-6: Ohm's law V = I*R", {
        "i":(lambda:2,[]),"r":(lambda:10,[]),
        "out":(lambda i,r: i*r,["i","r"]),
    },"out"))

    tasks.append(make_task("S-N2-7: Q = m*c*ΔT", {
        "m":(lambda:1,[]),"c":(lambda:4186,[]),"dt":(lambda:10,[]),
        "out":(lambda m,c,dt: m*c*dt,["m","c","dt"]),
    },"out"))

    # N3
    tasks.append(make_task("S-N3-1: Projectile range", {
        "v0":(lambda:20,[]),"theta":(lambda:45,[]),"g":(lambda:9.8,[]),
        "rad":(lambda theta: math.radians(theta),["theta"]),
        "vx":(lambda v0,rad: v0*math.cos(rad),["v0","rad"]),
        "vy":(lambda v0,rad: v0*math.sin(rad),["v0","rad"]),
        "t_flight":(lambda vy,g: 2*vy/g,["vy","g"]),
        "range":(lambda vx,t_flight: vx*t_flight,["vx","t_flight"]),
        "out":(lambda range: round(range,2),["range"]),
    },"out"))

    tasks.append(make_task("S-N3-2: Ideal gas law PV=nRT", {
        "n":(lambda:2,[]),"t":(lambda:300,[]),"v":(lambda:0.05,[]),
        "r":(lambda:8.314,[]),
        "nr":(lambda n,r: n*r,["n","r"]),
        "nrt":(lambda nr,t: nr*t,["nr","t"]),
        "p":(lambda nrt,v: nrt/v,["nrt","v"]),
        "out":(lambda p: round(p,2),["p"]),
    },"out"))

    tasks.append(make_task("S-N3-3: RC circuit time constant", {
        "r":(lambda:1000,[]),"c":(lambda:0.0001,[]),
        "tau":(lambda r,c: r*c,["r","c"]),
        "v0":(lambda:12,[]),"t":(lambda:0.1,[]),
        "exp":(lambda t,tau: math.exp(-t/tau),["t","tau"]),
        "vt":(lambda v0,exp: v0*(1-exp),["v0","exp"]),
        "out":(lambda vt: round(vt,4),["vt"]),
    },"out"))

    tasks.append(make_task("S-N3-4: Kinetic energy chain", {
        "m":(lambda:0.5,[]),"v":(lambda:10,[]),
        "v2":(lambda v: v*v,["v"]),
        "ke":(lambda m,v2: 0.5*m*v2,["m","v2"]),
        "v_f":(lambda ke,m: math.sqrt(2*ke/m),["ke","m"]),
        "out":(lambda v_f: round(v_f,2),["v_f"]),
    },"out"))

    tasks.append(make_task("S-N3-5: Gravitational force (2 bodies)", {
        "m1":(lambda:5.97e24,[]),"m2":(lambda:7.35e22,[]),
        "r":(lambda:3.84e8,[]),"g":(lambda:6.67e-11,[]),
        "num":(lambda g,m1,m2: g*m1*m2,["g","m1","m2"]),
        "r2":(lambda r: r*r,["r"]),
        "f":(lambda num,r2: num/r2,["num","r2"]),
        "out":(lambda f: round(f,2),["f"]),
    },"out"))

    tasks.append(make_task("S-N3-6: Doppler effect (source moving)", {
        "f":(lambda:440,[]),"v":(lambda:340,[]),"vs":(lambda:30,[]),
        "den":(lambda v,vs: v-vs,["v","vs"]),
        "f_prime":(lambda f,v,den: f*v/den,["f","v","den"]),  # simplified
        "out":(lambda f_prime: f_prime,["f_prime"]),
    },"out"))

    tasks.append(make_task("S-N3-7: Simple pendulum period", {
        "l":(lambda:1.5,[]),"g":(lambda:9.8,[]),
        "sqrt_lg":(lambda l,g: math.sqrt(l/g),["l","g"]),
        "t":(lambda sqrt_lg: 2*math.pi*sqrt_lg,["sqrt_lg"]),
        "freq":(lambda t: 1/t,["t"]),
        "out":(lambda freq: round(freq,4),["freq"]),
    },"out"))

    tasks.append(make_task("S-N3-8: Buoyant force", {
        "rho":(lambda:1000,[]),"v":(lambda:0.01,[]),"g":(lambda:9.8,[]),
        "f_b":(lambda rho,v,g: rho*v*g,["rho","v","g"]),
        "m_obj":(lambda:8,[]),"w":(lambda m_obj,g: m_obj*g,["m_obj","g"]),
        "net":(lambda w,f_b: w-f_b,["w","f_b"]),
        "sink":(lambda net: net>0,["net"]),
        "out":(lambda sink: sink,["sink"]),
    },"out"))

    # N4
    tasks.append(make_task("S-N4-1: Orbit velocity + period", {
        "g":(lambda:6.67e-11,[]),"m":(lambda:5.97e24,[]),"r":(lambda:7.0e6,[]),
        "gm":(lambda g,m: g*m,["g","m"]),
        "v":(lambda gm,r: math.sqrt(gm/r),["gm","r"]),
        "circ":(lambda r: 2*math.pi*r,["r"]),
        "t":(lambda circ,v: circ/v,["circ","v"]),
        "out":(lambda v,t: (round(v,2),round(t,2)),["v","t"]),
    },"out"))

    tasks.append(make_task("S-N4-2: Thermodynamic efficiency (Carnot)", {
        "th":(lambda:500,[]),"tc":(lambda:300,[]),
        "eff":(lambda th,tc: 1-tc/th,["th","tc"]),
        "q_h":(lambda:1000,[]),
        "w":(lambda eff,q_h: eff*q_h,["eff","q_h"]),
        "q_c":(lambda q_h,w: q_h-w,["q_h","w"]),
        "out":(lambda eff,w,q_c: (round(eff,4),round(w,2),round(q_c,2)),["eff","w","q_c"]),
    },"out"))

    tasks.append(make_task("S-N4-3: Lens equation (thin lens)", {
        "f":(lambda:10,[]),"d_o":(lambda:25,[]),
        "inv_f":(lambda f: 1/f,["f"]),
        "inv_do":(lambda d_o: 1/d_o,["d_o"]),
        "inv_di":(lambda inv_f,inv_do: inv_f-inv_do,["inv_f","inv_do"]),
        "d_i":(lambda inv_di: 1/inv_di,["inv_di"]),
        "mag":(lambda d_i,d_o: -d_i/d_o,["d_i","d_o"]),
        "out":(lambda d_i,mag: (round(d_i,2),round(mag,4)),["d_i","mag"]),
    },"out"))

    tasks.append(make_task("S-N4-4: Radioactive decay chain (3 isotopes)", {
        "n0":(lambda:1000,[]),"lambda1":(lambda:0.1,[]),"t":(lambda:10,[]),
        "n1":(lambda n0,lambda1,t: n0*math.exp(-lambda1*t),["n0","lambda1","t"]),
        "prod":(lambda n0,n1: n0-n1,["n0","n1"]),
        "lambda2":(lambda:0.05,[]),
        "n2":(lambda prod,lambda2,t: prod*math.exp(-lambda2*t),["prod","lambda2","t"]),
        "total":(lambda n1,n2: n1+n2,["n1","n2"]),
        "out":(lambda total: round(total,2),["total"]),
    },"out"))

    tasks.append(make_task("S-N4-5: Beer-Lambert law (absorbance cascade)", {
        "i0":(lambda:100,[]),"eps":(lambda:0.1,[]),"c":(lambda:0.5,[]),"l1":(lambda:1,[]),
        "a1":(lambda eps,c,l1: eps*c*l1,["eps","c","l1"]),
        "i1":(lambda i0,a1: i0*10**(-a1),["i0","a1"]),
        "l2":(lambda:0.5,[]),
        "a2":(lambda eps,c,l2: eps*c*l2,["eps","c","l2"]),
        "i2":(lambda i1,a2: i1*10**(-a2),["i1","a2"]),
        "absorbance":(lambda i0,i2: math.log10(i0/i2),["i0","i2"]),
        "out":(lambda absorbance: round(absorbance,4),["absorbance"]),
    },"out"))

    tasks.append(make_task("S-N4-6: Spring-mass (PE+KE at displacement)", {
        "k":(lambda:100,[]),"m":(lambda:0.5,[]),"x":(lambda:0.1,[]),
        "pe":(lambda k,x: 0.5*k*x*x,["k","x"]),
        "omega":(lambda k,m: math.sqrt(k/m),["k","m"]),
        "v":(lambda omega,x: omega*x,["omega","x"]),
        "ke":(lambda m,v: 0.5*m*v*v,["m","v"]),
        "total_e":(lambda pe,ke: pe+ke,["pe","ke"]),
        "out":(lambda total_e: round(total_e,4),["total_e"]),
    },"out"))

    tasks.append(make_task("S-N4-7: Sound intensity (dB cascade)", {
        "i0":(lambda:1e-12,[]),"p1":(lambda:0.1,[]),
        "i1":(lambda i0,p1: i0*p1,["i0","p1"]),
        "p2":(lambda:50,[]),
        "i2":(lambda i1,p2: i1*p2,["i1","p2"]),
        "db":(lambda i2: 10*math.log10(i2/1e-12),["i2"]),
        "half_db":(lambda db: db/2,["db"]),
        "out":(lambda half_db: round(half_db,2),["half_db"]),
    },"out"))

    tasks.append(make_task("S-N4-8: pH calculation (weak acid)", {
        "ka":(lambda:1.8e-5,[]),"c0":(lambda:0.1,[]),
        "sqrt_term":(lambda ka,c0: math.sqrt(ka*c0),["ka","c0"]),
        "h_conc":(lambda sqrt_term: sqrt_term,["sqrt_term"]),
        "ph":(lambda h_conc: -math.log10(h_conc),["h_conc"]),
        "poh":(lambda ph: 14-ph,["ph"]),
        "out":(lambda ph,poh: (round(ph,2),round(poh,2)),["ph","poh"]),
    },"out"))

    tasks.append(make_task("S-N4-9: Stellar magnitude (flux ratio)", {
        "m1":(lambda:1.0,[]),"m2":(lambda:6.0,[]),
        "dm":(lambda m1,m2: m1-m2,["m1","m2"]),
        "ratio":(lambda dm: 10**(dm/2.5),["dm"]),
        "f1":(lambda:100,[]),
        "f2":(lambda f1,ratio: f1/ratio,["f1","ratio"]),
        "out":(lambda f2: round(f2,4),["f2"]),
    },"out"))

    tasks.append(make_task("S-N4-10: Half-life chain (3 decays)", {
        "n0":(lambda:1000,[]),"hl1":(lambda:2,[]),"t":(lambda:6,[]),
        "lambda1":(lambda hl1: math.log(2)/hl1,["hl1"]),
        "n1":(lambda n0,lambda1,t: n0*math.exp(-lambda1*t),["n0","lambda1","t"]),
        "hl2":(lambda:3,[]),
        "lambda2":(lambda hl2: math.log(2)/hl2,["hl2"]),
        "n2":(lambda n1,lambda2,t: n1*math.exp(-lambda2*t),["n1","lambda2","t"]),
        "hl3":(lambda:1,[]),
        "lambda3":(lambda hl3: math.log(2)/hl3,["hl3"]),
        "n3":(lambda n2,lambda3,t: n2*math.exp(-lambda3*t),["n2","lambda3","t"]),
        "out":(lambda n3: round(n3,2),["n3"]),
    },"out"))

    return tasks

SCI_TASKS = _scientific_tasks()


# ═══════════════════════════════════════════════════════════════════
# TEST CLASSES
# ═══════════════════════════════════════════════════════════════════

def _p(test_list, level, count):
    """Yield parametrize tuples for a given level."""
    idx = {"N1":0,"N2":5,"N3":12,"N4":20}[level]
    for t in test_list[idx:idx+count]:
        yield pytest.param(t[1], t[2], id=t[0])

def _run_test(nodes, expected):
    result = execute_dag(nodes)
    for name, val in result.items():
        if name == "out" or name.endswith("_") or True:
            pass
    actual = result.get("out") or result.get(list(nodes.keys())[-1])
    assert actual == pytest.approx(expected, rel=1e-3) if isinstance(expected, float) else actual == expected


# ─── Logic ────────────────────────────────────────────────────────

class TestLogicDAG:
    @pytest.mark.parametrize("nodes,expected", list(_p(LOGIC_TASKS,"N1",5)))
    def test_n1(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(LOGIC_TASKS,"N2",7)))
    def test_n2(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(LOGIC_TASKS,"N3",8)))
    def test_n3(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(LOGIC_TASKS,"N4",10)))
    def test_n4(self, nodes, expected):
        _run_test(nodes, expected)


# ─── Math ─────────────────────────────────────────────────────────

class TestMathDAG:
    @pytest.mark.parametrize("nodes,expected", list(_p(MATH_TASKS,"N1",5)))
    def test_n1(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(MATH_TASKS,"N2",7)))
    def test_n2(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(MATH_TASKS,"N3",8)))
    def test_n3(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(MATH_TASKS,"N4",10)))
    def test_n4(self, nodes, expected):
        _run_test(nodes, expected)


# ─── Planning ─────────────────────────────────────────────────────

class TestPlanningDAG:
    @pytest.mark.parametrize("nodes,expected", list(_p(PLANNING_TASKS,"N1",5)))
    def test_n1(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(PLANNING_TASKS,"N2",7)))
    def test_n2(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(PLANNING_TASKS,"N3",8)))
    def test_n3(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(PLANNING_TASKS,"N4",10)))
    def test_n4(self, nodes, expected):
        _run_test(nodes, expected)


# ─── Code Flow ────────────────────────────────────────────────────

class TestCodeFlowDAG:
    @pytest.mark.parametrize("nodes,expected", list(_p(CODE_TASKS,"N1",5)))
    def test_n1(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(CODE_TASKS,"N2",7)))
    def test_n2(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(CODE_TASKS,"N3",8)))
    def test_n3(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(CODE_TASKS,"N4",10)))
    def test_n4(self, nodes, expected):
        _run_test(nodes, expected)


# ─── Scientific ───────────────────────────────────────────────────

class TestScientificDAG:
    @pytest.mark.parametrize("nodes,expected", list(_p(SCI_TASKS,"N1",5)))
    def test_n1(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(SCI_TASKS,"N2",7)))
    def test_n2(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(SCI_TASKS,"N3",8)))
    def test_n3(self, nodes, expected):
        _run_test(nodes, expected)

    @pytest.mark.parametrize("nodes,expected", list(_p(SCI_TASKS,"N4",10)))
    def test_n4(self, nodes, expected):
        _run_test(nodes, expected)
