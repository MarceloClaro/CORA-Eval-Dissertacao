#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trace Analyzer for CORA-Eval Benchmark — Round 12D.
Analyzes LLM reasoning traces, classifies behavioral steps (6 categories),
trains an MLP classifier, and computes health metrics.

Based on LongCoT (2604.14140) qualitative analysis methodology:
  Setup, Planning, Solving, Verification, Stuck, Backtracking

Uso:
    python trace_analyzer.py --analyze <trace_file.txt>
    python trace_analyzer.py --compare <trace1.txt> <trace2.txt>
    python trace_analyzer.py --train <dataset.json>
    python trace_analyzer.py --demo
    python trace_analyzer.py --metrics <trace_file.txt>
"""

import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

random.seed(42)
np.random.seed(42)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


CATEGORIES = ["Setup", "Planning", "Solving", "Verification", "Stuck", "Backtracking"]
CAT_SHORT = {"Setup": "SETUP", "Planning": "PLAN", "Solving": "SOLVE",
             "Verification": "VERIFY", "Stuck": "STUCK", "Backtracking": "BACK"}

KEYWORDS = {
    "Setup": [
        "understand", "parse", "initialize", "given", "let", "define",
        "consider", "suppose", "we have", "input", "problem", "task",
        "first", "read", "extract", "identify", "begin", "start",
        "the problem", "we need to", "goal", "objective", "we are given",
        "variables", "parameters", "assume", "notation", "represent",
        "setup", "configure", "prepare", "load", "import",
    ],
    "Planning": [
        "plan", "strategy", "approach", "step", "first we", "then we",
        "outline", "overview", "break down", "decompose", "subproblem",
        "algorithm", "method", "procedure", "framework", "scheme",
        "roadmap", "agenda", "we will", "our plan", "the idea",
        "sketch", "think about how", "to solve this", "let's try",
        "divide", "split into", "stages", "phases", "sequence",
    ],
    "Solving": [
        "compute", "calculate", "solve", "evaluate", "apply",
        "substitute", "simplify", "expand", "factor", "multiply",
        "add", "subtract", "divide", "integrate", "differentiate",
        "derive", "transform", "convert", "execute", "perform",
        "run", "process", "implement", "operation", "formula",
        "equation", "value", "result", "therefore", "thus",
        "so", "then", "using", "we get", "yields", "equals",
        "=", "==", "+", "-", "*", "/", "sum", "product",
    ],
    "Verification": [
        "check", "verify", "validate", "confirm", "ensure",
        "double-check", "review", "inspect", "examine", "test",
        "does this make sense", "let me verify", "verify that",
        "cross-check", "recalculate", "re-evaluate", "recompute",
        "make sure", "correct?", "is this right", "check if",
        "validate against", "consistency", "sanity check",
        "plug back in", "substitute back", "verify the result",
    ],
    "Stuck": [
        "i don't know", "not sure", "confused", "stuck", "unsure",
        "uncertain", "difficult", "complicated", "complex",
        "i cannot", "can't", "cannot", "don't understand",
        "unclear", "not working", "doesn't work", "wrong",
        "error", "mistake", "incorrect", "invalid", "failed",
        "give up", "skip", "moving on", "i give up",
        "i'm stuck", "not sure how", "no idea", "maybe",
        "perhaps", "try something else", "not confident",
        "this is hard", "too difficult", "confusing",
    ],
    "Backtracking": [
        "wait", "hold on", "actually", "revisit", "re-examine",
        "go back", "backtrack", "reconsider", "rethink",
        "previous step", "earlier", "let me reconsider",
        "on second thought", "alternatively", "instead",
        "different approach", "try again", "restart",
        "start over", "re-do", "rework", "revise",
        "correction", "corrected", "fixed", "recalculate",
        "that was wrong", "i made a mistake", "let me redo",
        "let me start over", "back up", "roll back",
        "alternative", "another way", "let me try",
    ],
}


def softmax(x: np.ndarray) -> np.ndarray:
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)


class SimpleMLP:
    """3-layer MLP: input -> hidden(8, ReLU) -> output(6, softmax)."""

    def __init__(self, input_dim: int, hidden_dim: int = 8, output_dim: int = 6, lr: float = 0.01):
        self.lr = lr
        limit1 = math.sqrt(6.0 / (input_dim + hidden_dim))
        self.W1 = np.random.uniform(-limit1, limit1, (input_dim, hidden_dim))
        self.b1 = np.zeros((1, hidden_dim))
        limit2 = math.sqrt(6.0 / (hidden_dim + output_dim))
        self.W2 = np.random.uniform(-limit2, limit2, (hidden_dim, output_dim))
        self.b2 = np.zeros((1, output_dim))

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        z1 = X @ self.W1 + self.b1
        a1 = relu(z1)
        z2 = a1 @ self.W2 + self.b2
        a2 = softmax(z2)
        return a1, a2, z1

    def predict(self, X: np.ndarray) -> np.ndarray:
        _, a2, _ = self.forward(X)
        return np.argmax(a2, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        _, a2, _ = self.forward(X)
        return a2

    def train_step(self, X: np.ndarray, y: np.ndarray):
        n = X.shape[0]
        a1, a2, z1 = self.forward(X)
        y_onehot = np.zeros((n, self.W2.shape[1]))
        y_onehot[np.arange(n), y] = 1
        dz2 = a2 - y_onehot
        dW2 = a1.T @ dz2 / n
        db2 = np.sum(dz2, axis=0, keepdims=True) / n
        da1 = dz2 @ self.W2.T
        dz1 = da1 * (z1 > 0)
        dW1 = X.T @ dz1 / n
        db1 = np.sum(dz1, axis=0, keepdims=True) / n
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 200, verbose: bool = False):
        for epoch in range(epochs):
            self.train_step(X, y)
            if verbose and (epoch + 1) % 50 == 0:
                preds = self.predict(X)
                acc = np.mean(preds == y)
                print(f"    Epoch {epoch+1}/{epochs} — accuracy: {acc:.3f}")


class TraceAnalyzer:
    """Main trace analysis engine."""

    def __init__(self):
        self.mlp: Optional[SimpleMLP] = None
        self.mlp_trained = False

    # ── Trace Parsing ──────────────────────────────────────────────

    def parse_trace(self, text: str) -> List[Dict]:
        """Parse raw trace text into segmented, classified steps."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return self._parse_json_trace(text)
        return self._parse_text_lines(lines)

    def _parse_json_trace(self, text: str) -> List[Dict]:
        """Parse JSON-formatted trace."""
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return [{"text": text[:200], "category": "Solving",
                     "confidence": 0.3, "idx": 0}]

        if isinstance(data, list):
            steps = []
            for i, item in enumerate(data):
                if isinstance(item, dict) and "text" in item:
                    seg_text = item["text"]
                    cat, conf = self.classify_segment(seg_text)
                    steps.append({
                        "idx": i, "text": seg_text,
                        "category": cat, "confidence": conf,
                    })
            if steps:
                return steps

        if isinstance(data, dict):
            text = data.get("trace", data.get("reasoning", json.dumps(data)))
            return self._parse_text_lines(text.split("\n"))

        return [{"text": str(data)[:200], "category": "Solving",
                 "confidence": 0.3, "idx": 0}]

    def _parse_text_lines(self, lines: List[str]) -> List[Dict]:
        """Segment text lines into classified steps."""
        steps = []
        buffer = ""
        idx = 0

        for line in lines:
            if self._is_segment_boundary(line, buffer):
                if buffer.strip():
                    cat, conf = self.classify_segment(buffer.strip())
                    steps.append({
                        "idx": idx, "text": buffer.strip(),
                        "category": cat, "confidence": conf,
                    })
                    idx += 1
                buffer = line
            else:
                buffer += " " + line if buffer else line

        if buffer.strip():
            cat, conf = self.classify_segment(buffer.strip())
            steps.append({
                "idx": idx, "text": buffer.strip(),
                "category": cat, "confidence": conf,
            })

        return steps

    def _is_segment_boundary(self, line: str, buffer: str) -> bool:
        if not buffer:
            return False
        if re.match(r'^\d+\.\s', line):
            return True
        if re.match(r'^Step\s+\d+', line, re.IGNORECASE):
            return True
        if line.startswith(("- ", "* ", "•")):
            return True
        if line.isupper() and len(line) > 3 and len(line) < 60:
            return True
        if line == "":
            return True
        if buffer.endswith((".", "!", "?")) and len(buffer) > 40:
            return True
        return False

    # ── Keyword Classification ─────────────────────────────────────

    def classify_segment(self, text: str) -> Tuple[str, float]:
        """Classify a text segment into one of 6 categories with confidence."""
        text_lower = text.lower()
        scores = {}

        for cat in CATEGORIES:
            count = sum(1 for kw in KEYWORDS[cat] if kw in text_lower)
            if count > 0:
                density = count / max(len(text.split()), 1)
                scores[cat] = min(1.0, density * 3.0 + 0.1)
            else:
                scores[cat] = 0.0

        if self.mlp_trained and len(text.split()) >= 3:
            fv = self._extract_features(text)
            if fv is not None:
                mlp_pred = self.mlp.predict(fv.reshape(1, -1))[0]
                mlp_conf = np.max(self.mlp.predict_proba(fv.reshape(1, -1)))
                mlp_cat = CATEGORIES[int(mlp_pred)]
                if mlp_conf > 0.4:
                    scores[mlp_cat] = max(scores.get(mlp_cat, 0), mlp_conf * 0.6)

        best_cat = max(scores, key=scores.get)
        best_score = scores[best_cat]

        if best_score < 0.05:
            return ("Solving", 0.3)

        return (best_cat, round(best_score, 3))

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract keyword count feature vector (6 per category)."""
        text_lower = text.lower()
        words = text_lower.split()
        word_set = set(words)
        features = []
        for cat in CATEGORIES:
            cat_kws = KEYWORDS[cat]
            exact_count = sum(1 for kw in cat_kws if kw in text_lower)
            token_overlap = len(set(kw.replace(" ", "_") for kw in cat_kws if len(kw.split()) == 1) & word_set)
            bi_overlap = 0
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                if bigram in cat_kws:
                    bi_overlap += 1
            n_words = len(words)
            features.extend([
                exact_count,
                token_overlap,
                bi_overlap,
                min(1.0, exact_count / max(n_words, 1) * 10),
                min(1.0, len(text) / 500),
                float(len(cat_kws)),
            ])
        return np.array(features, dtype=np.float32)

    # ── MLP Training ────────────────────────────────────────────────

    def train_mlp(self, dataset_path: str) -> Dict:
        """Train MLP on a labeled dataset JSON file."""
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        samples = data if isinstance(data, list) else data.get("samples", [])
        if not samples:
            print("  Dataset vazio ou formato invalido.")
            return {"status": "error", "message": "empty dataset"}

        X_list, y_list = [], []
        label_map = {c: i for i, c in enumerate(CATEGORIES)}

        for s in samples:
            text = s.get("text", s.get("trace", ""))
            label = s.get("label", s.get("category", ""))
            if not text or label not in label_map:
                continue
            fv = self._extract_features(text)
            if fv is not None:
                X_list.append(fv)
                y_list.append(label_map[label])

        if len(X_list) < 6:
            print(f"  Apenas {len(X_list)} amostras validas. MLP precisa de >= 6.")
            return {"status": "error", "samples": len(X_list)}

        X = np.array(X_list)
        y = np.array(y_list)

        indices = np.random.permutation(len(X))
        split = int(len(X) * 0.8)
        train_idx, test_idx = indices[:split], indices[split:]

        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]

        input_dim = X.shape[1]
        self.mlp = SimpleMLP(input_dim=input_dim, hidden_dim=8, output_dim=6, lr=0.01)
        self.mlp.train(X_train, y_train, epochs=300, verbose=True)

        train_preds = self.mlp.predict(X_train)
        test_preds = self.mlp.predict(X_test)

        train_acc = float(np.mean(train_preds == y_train))
        test_acc = float(np.mean(test_preds == y_test))

        self.mlp_trained = True

        result = {
            "status": "ok",
            "samples": len(X_list),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_accuracy": round(train_acc, 4),
            "test_accuracy": round(test_acc, 4),
            "input_dim": input_dim,
        }

        print(f"\n  Resultados do treinamento MLP:")
        print(f"    Amostras totais: {len(X_list)}")
        print(f"    Treino: {len(X_train)}, Teste: {len(X_test)}")
        print(f"    Acurácia treino: {train_acc:.3f}")
        print(f"    Acurácia teste:  {test_acc:.3f}")

        return result

    # ── Metrics ─────────────────────────────────────────────────────

    def compute_metrics(self, steps: List[Dict]) -> Dict:
        """Compute all trace metrics."""
        if not steps:
            return {}

        cats = [s["category"] for s in steps]
        total = len(steps)
        dist = Counter(cats)
        distribution = {c: {"count": dist.get(c, 0), "pct": dist.get(c, 0) / total * 100}
                        for c in CATEGORIES}

        transition = defaultdict(Counter)
        for i in range(len(cats) - 1):
            transition[cats[i]][cats[i + 1]] += 1
        transition_matrix = {
            src: dict(dst) for src, dst in transition.items()
        }

        stuck_count = dist.get("Stuck", 0)
        backtrack_count = dist.get("Backtracking", 0)
        stuck_bt_ratio = (stuck_count / backtrack_count
                          if backtrack_count > 0 else float("inf"))

        plan_count = dist.get("Planning", 0)
        solve_count = dist.get("Solving", 0)
        plan_solve_ratio = (plan_count / solve_count
                            if solve_count > 0 else float("inf"))

        health_score = self._compute_health_score(
            distribution, stuck_bt_ratio, plan_solve_ratio, total)

        return {
            "total_steps": total,
            "distribution": distribution,
            "transition_matrix": transition_matrix,
            "stuck_backtrack_ratio": round(stuck_bt_ratio, 2) if stuck_bt_ratio != float("inf") else None,
            "stuck_backtrack_ratio_raw": stuck_bt_ratio,
            "plan_solve_ratio": round(plan_solve_ratio, 2) if plan_solve_ratio != float("inf") else None,
            "plan_solve_ratio_raw": plan_solve_ratio,
            "health_score": health_score,
        }

    def _compute_health_score(self, dist: Dict, sbr: float, psr: float, total: int) -> int:
        """Compute overall health score 0-100."""
        score = 50.0

        setup_pct = dist.get("Setup", {}).get("pct", 0)
        plan_pct = dist.get("Planning", {}).get("pct", 0)
        solve_pct = dist.get("Solving", {}).get("pct", 0)
        ver_pct = dist.get("Verification", {}).get("pct", 0)
        stuck_pct = dist.get("Stuck", {}).get("pct", 0)
        bt_pct = dist.get("Backtracking", {}).get("pct", 0)

        if 5 <= setup_pct <= 25:
            score += 10
        elif setup_pct > 40:
            score -= 10

        if 5 <= plan_pct <= 20:
            score += 15
        elif plan_pct < 3:
            score -= 10

        if 25 <= solve_pct <= 60:
            score += 15
        elif solve_pct < 15:
            score -= 10

        if 5 <= ver_pct <= 20:
            score += 10
        elif ver_pct < 2:
            score -= 5

        if stuck_pct > 30:
            score -= 20
        elif stuck_pct > 20:
            score -= 10
        elif stuck_pct < 5:
            score += 5

        if bt_pct > 15:
            score -= 10
        elif 2 <= bt_pct <= 10:
            score += 5

        if sbr != float("inf"):
            if sbr <= 2.0:
                score += 10
            elif sbr <= 4.0:
                score += 5
            else:
                score -= 10

        if psr != float("inf"):
            if 0.2 <= psr <= 0.5:
                score += 10
            elif psr < 0.1:
                score -= 5
            elif psr > 1.0:
                score -= 10

        if total < 5:
            score -= 20

        return max(0, min(100, int(score)))

    def mlp_predict_success(self, steps: List[Dict]) -> Dict:
        """Use trained MLP to predict success/failure."""
        if not self.mlp_trained or not steps:
            return {"prediction": "UNKNOWN", "confidence": 0.0}

        fvs = []
        for s in steps:
            fv = self._extract_features(s["text"])
            if fv is not None:
                fvs.append(fv)
        if not fvs:
            return {"prediction": "UNKNOWN", "confidence": 0.0}

        X = np.array(fvs)
        preds = self.mlp.predict(X)
        probas = self.mlp.predict_proba(X)

        cat_counts = Counter(preds)
        dominant = cat_counts.most_common(1)[0][0]
        dominant_cat = CATEGORIES[int(dominant)]

        avg_proba = float(np.mean(probas, axis=0)[int(dominant)])

        stuck_idx = CATEGORIES.index("Stuck")
        solve_idx = CATEGORIES.index("Solving")
        stuck_ratio = np.mean(preds == stuck_idx)
        solve_ratio = np.mean(preds == solve_idx)

        if stuck_ratio > 0.3:
            pred = "LIKELY TO FAIL"
            conf = min(0.95, stuck_ratio + 0.2)
        elif solve_ratio > 0.4 and stuck_ratio < 0.1:
            pred = "LIKELY TO SUCCEED"
            conf = min(0.9, solve_ratio + 0.2)
        elif dominant_cat == "Stuck":
            pred = "LIKELY TO FAIL"
            conf = min(0.85, avg_proba + 0.1)
        elif dominant_cat == "Solving":
            pred = "LIKELY TO SUCCEED"
            conf = min(0.8, avg_proba + 0.1)
        else:
            balanced = solve_ratio / max(stuck_ratio, 0.01)
            if balanced > 2.0:
                pred = "LIKELY TO SUCCEED"
                conf = min(0.75, balanced * 0.15)
            elif balanced < 0.8:
                pred = "LIKELY TO FAIL"
                conf = min(0.75, (1 - balanced) * 0.3)
            else:
                pred = "UNCERTAIN"
                conf = 0.5

        return {
            "prediction": pred,
            "confidence": round(conf, 3),
            "dominant_category": dominant_cat,
            "stuck_ratio": round(float(stuck_ratio), 3),
            "solve_ratio": round(float(solve_ratio), 3),
        }

    # ── Visualization ───────────────────────────────────────────────

    def format_report(self, steps: List[Dict], metrics: Dict,
                      mlp_result: Optional[Dict] = None,
                      filename: str = "") -> str:
        """Generate formatted ASCII report."""
        lines = []
        lines.append("")
        lines.append("\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557")
        lines.append("\u2551   Trace Analysis Report — CORA-Eval (Round 12D)              \u2551")
        lines.append("\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d")
        lines.append("")

        if filename:
            lines.append(f"  File: {filename}")
        lines.append(f"  Total steps: {metrics.get('total_steps', len(steps))}")
        lines.append("")

        dist = metrics.get("distribution", {})
        lines.append("  Category Distribution:")
        for cat in CATEGORIES:
            d = dist.get(cat, {})
            count = d.get("count", 0)
            pct = d.get("pct", 0)
            bar_len = 16
            filled = int(pct / 100 * bar_len)
            bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
            lines.append(f"    {cat:15s}: {count:3d} steps ({pct:5.1f}%)  {bar}")
        lines.append("")

        flow = [CAT_SHORT.get(s["category"], "????") for s in steps]
        flow_str = " \u2192 ".join(flow[:20])
        if len(flow) > 20:
            flow_str += " \u2192 ..."
        lines.append(f"  Flow: {flow_str}")
        lines.append("")

        lines.append("  Metrics:")
        sbr = metrics.get("stuck_backtrack_ratio")
        psr = metrics.get("plan_solve_ratio")
        hs = metrics.get("health_score", 0)

        if sbr is not None:
            flag = "\u26a0 high" if sbr > 2.0 else "\u2713 healthy"
            lines.append(f"    Stuck/Backtracking ratio: {sbr:.2f} ({flag})")
        else:
            lines.append("    Stuck/Backtracking ratio: N/A")

        if psr is not None:
            if 0.2 <= psr <= 0.5:
                flag = "\u2713 healthy"
            elif psr < 0.2:
                flag = "\u26a0 very low (lacks planning)"
            else:
                flag = "\u26a0 high (too much planning)"
            lines.append(f"    Planning/Solving ratio: {psr:.2f} ({flag})")
        else:
            lines.append("    Planning/Solving ratio: N/A")

        hs_bar_len = 20
        hs_filled = int(hs / 100 * hs_bar_len)
        hs_bar = "\u2588" * hs_filled + "\u2591" * (hs_bar_len - hs_filled)
        hs_grade = "EXCELLENT" if hs >= 80 else "GOOD" if hs >= 60 else "FAIR" if hs >= 40 else "POOR"
        lines.append(f"    Trace Health Score: {hs}/100 [{hs_bar}] ({hs_grade})")
        lines.append("")

        if mlp_result:
            pred = mlp_result.get("prediction", "N/A")
            conf = mlp_result.get("confidence", 0)
            lines.append(f"  MLP Prediction: {pred} (confidence: {conf:.1%})")
            lines.append("")

        return "\n".join(lines)

    def format_comparison(self, results: List[Tuple[str, List[Dict], Dict]]) -> str:
        """Generate side-by-side comparison of two or more traces."""
        lines = []
        lines.append("")
        lines.append("\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557")
        lines.append("\u2551   Trace Comparison — CORA-Eval (Round 12D)                                       \u2551")
        lines.append("\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d")
        lines.append("")

        col_w = 35
        header = f"  {'Metric':22s}"
        for name, _, _ in results:
            header += f"  {name[:col_w]:{col_w}s}"
        lines.append(header)
        lines.append("  " + "-" * (22 + (col_w + 2) * len(results)))

        for cat in CATEGORIES:
            row = f"  {cat:22s}"
            for _, _, m in results:
                d = m.get("distribution", {}).get(cat, {})
                pct = d.get("pct", 0)
                count = d.get("count", 0)
                row += f"  {count:3d} ({pct:5.1f}%){' ' * (col_w - 12)}"
            lines.append(row)

        lines.append("")
        row = f"  {'Health Score':22s}"
        for _, _, m in results:
            hs = m.get("health_score", 0)
            row += f"  {hs:3d}/100{' ' * (col_w - 8)}"
        lines.append(row)

        row = f"  {'Stuck/BT Ratio':22s}"
        for _, _, m in results:
            sbr = m.get("stuck_backtrack_ratio", "N/A")
            row += f"  {str(sbr):10s}{' ' * (col_w - 12)}"
        lines.append(row)

        row = f"  {'Plan/Solve Ratio':22s}"
        for _, _, m in results:
            psr = m.get("plan_solve_ratio", "N/A")
            row += f"  {str(psr):10s}{' ' * (col_w - 12)}"
        lines.append(row)

        lines.append("")
        return "\n".join(lines)

    def generate_synthetic_trace(self, length: int = 50) -> str:
        """Generate a synthetic reasoning trace for demo purposes."""
        templates = {
            "Setup": [
                "Let me understand the problem. We are given a set of {n} points in {d}-dimensional space.",
                "First, I need to parse the input. The problem asks us to find the {target}.",
                "Let me define the variables: x is the unknown, y is the constraint.",
                "The problem states: given an array of length n, find the {target}.",
                "I need to identify what is being asked. This is a {domain} problem.",
                "Let me restate: we have {n} items, each with weight w_i and value v_i.",
                "I will approach this step by step. First, the setup phase.",
            ],
            "Planning": [
                "My strategy is to first compute the prefix sums, then query each range.",
                "The plan: decompose into subproblems, solve each recursively, then combine.",
                "I will use dynamic programming: define dp[i] as the optimal solution up to i.",
                "The approach is binary search on the answer, checking feasibility at each step.",
                "Let me outline the steps: 1) Sort the data  2) Apply two-pointer  3) Return result.",
                "My plan is to traverse the graph using DFS and track visited nodes.",
                "I can break this into 3 phases: preprocessing, main computation, postprocessing.",
                "The idea is to use divide-and-conquer: split in half, solve each, merge.",
            ],
            "Solving": [
                "Computing the value: sum = 0; for i in range(n): sum += arr[i].",
                "Applying the formula: result = (a + b) * c / d.",
                "dp[i] = max(dp[i-1], dp[i-2] + value[i]). Let me compute this iteratively.",
                "Sorting the array using quicksort: pick pivot, partition, recurse.",
                "The distance between points p and q is sqrt((x2-x1)^2 + (y2-y1)^2).",
                "Substituting x = {val} into the equation: f({val}) = {val}^2 + 2*{val} + 1 = {result}.",
                "Now I compute the gradient: df/dx = 2x + 3. At x = {val}, gradient = {result}.",
                "Expanding the product: (a+b)(a-b) = a^2 - b^2 = {result}.",
            ],
            "Verification": [
                "Let me double-check this result by plugging it back into the original equation.",
                "Verifying: if x = {val}, then the left side equals the right side. Confirmed.",
                "Let me recalculate to ensure accuracy. {val1} * {val2} = {result}. Yes, correct.",
                "Checking edge cases: empty input, single element, all negative values. All pass.",
                "I should verify the invariant holds at each step of the loop.",
                "Let me cross-check with a simple example: if n = 1, the answer should be {val}.",
                "Does this result make sense? Given the constraints, it seems reasonable.",
            ],
            "Stuck": [
                "I am not sure how to proceed from here. The approach is not working.",
                "This is getting very complicated. I cannot see a clear path forward.",
                "Hmm, this does not match my expectations. I might have made an error earlier.",
                "I have tried several approaches and none of them seem to work correctly.",
                "Maybe I do not understand the problem correctly. Let me reconsider.",
                "This is too difficult. I am not confident in my ability to solve this.",
                "I keep getting incorrect results. Something is fundamentally wrong.",
            ],
            "Backtracking": [
                "Wait, I made a mistake. Let me go back and re-examine the previous step.",
                "Actually, that approach is incorrect. Let me backtrack and try a different method.",
                "Hold on, I misread the problem. Let me restart with the correct interpretation.",
                "On second thought, I should reconsider my assumption about the data structure.",
                "Let me revisit step 3. The value I computed does not propagate correctly.",
                "I need to backtrack here. The current path leads to a contradiction.",
                "Alternative approach: instead of DP, I could use greedy here.",
            ],
        }

        domains = ["mathematics", "computer science", "logic", "optimization", "search"]
        targets = ["maximum value", "minimum cost", "shortest path", "optimal solution", "median element"]
        trace_lines = []

        story_state = {"n": random.randint(5, 20), "d": random.randint(2, 5),
                       "val": random.randint(1, 100), "val2": random.randint(1, 10),
                       "domain": random.choice(domains), "target": random.choice(targets),
                       "result": random.randint(10, 999), "val1": random.randint(1, 50)}

        weights = [0.15, 0.12, 0.35, 0.12, 0.16, 0.10]
        rng = random.Random(42)

        for i in range(length):
            cat = rng.choices(CATEGORIES, weights=weights, k=1)[0]
            tmpl = rng.choice(templates[cat])
            try:
                text = tmpl.format(**story_state)
            except KeyError:
                text = tmpl
            trace_lines.append(text)

            if rng.random() < 0.1:
                story_state["val"] = random.randint(1, 100)
                story_state["result"] = random.randint(10, 999)

        return "\n\n".join(trace_lines)

    # ── Main Analysis ───────────────────────────────────────────────

    def analyze(self, text: str, filename: str = "") -> Dict:
        """Full analysis pipeline."""
        steps = self.parse_trace(text)
        if not steps:
            print("  Warning: no steps parsed from trace.")
            return {"steps": [], "metrics": {}, "mlp_result": None}

        metrics = self.compute_metrics(steps)

        mlp_result = None
        if self.mlp_trained:
            mlp_result = self.mlp_predict_success(steps)

        report = self.format_report(steps, metrics, mlp_result, filename)
        print(report)

        result = {
            "steps": steps,
            "metrics": metrics,
            "mlp_result": mlp_result,
            "report": report,
        }
        return result

    def analyze_file(self, filepath: str) -> Dict:
        """Analyze trace from file."""
        path = Path(filepath)
        if not path.exists():
            print(f"  Error: file not found: {filepath}")
            return {"error": "file not found"}

        text = path.read_text(encoding="utf-8")
        return self.analyze(text, filename=path.name)

    def compare(self, filepath1: str, filepath2: str):
        """Compare two trace files."""
        r1 = self.analyze_file(filepath1)
        r2 = self.analyze_file(filepath2)

        if "error" in r1 or "error" in r2:
            return

        name1 = Path(filepath1).name
        name2 = Path(filepath2).name

        comparison = self.format_comparison([
            (name1, r1["steps"], r1["metrics"]),
            (name2, r2["steps"], r2["metrics"]),
        ])
        print(comparison)
        return comparison


def run_demo():
    """Run demo with synthetic trace."""
    print("  Generating synthetic trace...")
    analyzer = TraceAnalyzer()
    trace_text = analyzer.generate_synthetic_trace(50)
    result = analyzer.analyze(trace_text, filename="synthetic_demo_trace.txt")

    print("  Training MLP on synthetic data (self-supervised)...")
    samples = []
    for s in result["steps"]:
        samples.append({"text": s["text"], "label": s["category"]})
    train_data = {"samples": samples}
    train_path = Path(__file__).parent / "_synthetic_train_data.json"
    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=2, ensure_ascii=False)

    analyzer.train_mlp(str(train_path))

    print("\n  MLP prediction on same trace:")
    mlp_r = analyzer.mlp_predict_success(result["steps"])
    print(f"    {mlp_r['prediction']} (confidence: {mlp_r['confidence']:.1%})")

    os.unlink(train_path)

    output = {
        "analysis": result,
        "mlp_prediction": mlp_r,
    }
    json_path = Path(__file__).parent / "trace_analysis_demo.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  JSON output saved to: {json_path.name}")

    return output


def cmd_analyze(filepath: str):
    analyzer = TraceAnalyzer()
    analyzer.analyze_file(filepath)


def cmd_compare(fp1: str, fp2: str):
    analyzer = TraceAnalyzer()
    analyzer.compare(fp1, fp2)


def cmd_train(dataset_path: str):
    analyzer = TraceAnalyzer()
    result = analyzer.train_mlp(dataset_path)
    if result.get("status") == "ok":
        json_path = Path(__file__).parent / "mlp_training_result.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n  Result saved to: {json_path.name}")


def cmd_metrics(filepath: str):
    analyzer = TraceAnalyzer()
    path = Path(filepath)
    if not path.exists():
        print(f"  Error: file not found: {filepath}")
        return
    text = path.read_text(encoding="utf-8")
    steps = analyzer.parse_trace(text)
    metrics = analyzer.compute_metrics(steps)
    report = analyzer.format_report(steps, metrics, filename=path.name)
    print(report)

    json_path = Path(__file__).parent / "trace_metrics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"  JSON metrics saved to: {json_path.name}")


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "--demo":
        run_demo()
    elif cmd == "--analyze":
        if len(args) < 2:
            print("Uso: --analyze <trace_file.txt>")
            return
        cmd_analyze(args[1])
    elif cmd == "--compare":
        if len(args) < 3:
            print("Uso: --compare <trace1.txt> <trace2.txt>")
            return
        cmd_compare(args[1], args[2])
    elif cmd == "--train":
        if len(args) < 2:
            print("Uso: --train <dataset.json>")
            return
        cmd_train(args[1])
    elif cmd == "--metrics":
        if len(args) < 2:
            print("Uso: --metrics <trace_file.txt>")
            return
        cmd_metrics(args[1])
    else:
        print(f"Unknown command: {cmd}")
        print("Use --help for usage.")


if __name__ == "__main__":
    main()
