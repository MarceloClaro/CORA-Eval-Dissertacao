#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cascade Verifier v1.0 — Pipeline de Verificação em 4 Estágios para CORA-Eval.

Implementa a arquitetura de verificação sequencial descrita no LongCoT paper
(2604.14140v1, Seção 4.1): RegEx → RegEx Flexível → LLM → Revisão Manual.

Uso:
    python cascade_verifier.py --verify <answer.txt> <expected.json>
    python cascade_verifier.py --stage regex <answer.txt> <expected.json>
    python cascade_verifier.py --demo
    python cascade_verifier.py --report <results.json>
    python cascade_verifier.py --validate <test_file.py>
"""

import json
import os
import re
import sys
import time
import importlib.util
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import OrderedDict

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

random = __import__("random")
random.seed(42)

SCRIPT_DIR = Path(__file__).parent.resolve()

# ─── Constantes de Domínio ───────────────────────────────────────────

DIMENSION_NAMES = {
    "D1": "Raciocínio Matemático Formal",
    "D2": "Modelagem de Sistemas Físicos",
    "D3": "Análise Estatística e Inferência",
    "D4": "Química Computacional e Estrutural",
    "D5": "Biologia Molecular e Genômica",
    "D6": "Geociências e Modelagem Climática",
    "D7": "Verificação de Código Científico",
    "D8": "Revisão Sistemática de Literatura",
    "D9": "Desenho Experimental e Metodologia",
    "D10": "Síntese Interdisciplinar",
    "D11": "Raciocínio Long-Horizon (DAG)",
}

VERIFIER_VERSION = "1.0.0"

# ─── Estruturas de Dados ────────────────────────────────────────────


@dataclass
class VerificationResult:
    stage: str
    passed: bool
    confidence: float
    issues: List[str]
    details: str
    time_ms: float

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def header() -> str:
        return (
            f"{'Stage':<14} {'Passed':<8} {'Confidence':<12} {'Time(ms)':<10} Details"
        )

    def table_row(self) -> str:
        return (
            f"{self.stage:<14} {'✓' if self.passed else '✗':<8} "
            f"{self.confidence:<12.2f} {self.time_ms:<10.1f} {self.details[:60]}"
        )


@dataclass
class ExpectedAnswer:
    value: Any
    type: str  # "number", "boolean", "string", "expression", "code", "scientific", "set", "tuple"
    tolerance: float = 0.0
    alternatives: List[str] = field(default_factory=list)
    dimension: str = ""
    task_id: str = ""

    @classmethod
    def from_dict(cls, d: Dict) -> "ExpectedAnswer":
        return cls(
            value=d.get("value"),
            type=d.get("type", "string"),
            tolerance=d.get("tolerance", 0.0),
            alternatives=d.get("alternatives", []),
            dimension=d.get("dimension", ""),
            task_id=d.get("task_id", ""),
        )


@dataclass
class AnswerSample:
    question: str
    answer: str
    expected: ExpectedAnswer
    is_correct: bool
    reasoning: str = ""


# ─── Padrões Regex ──────────────────────────────────────────────────

REGEX_PATTERNS: Dict[str, re.Pattern] = {
    "integer": re.compile(r"^-?\d+$"),
    "float": re.compile(r"^-?\d+\.?\d*(?:[eE][+-]?\d+)?$"),
    "boolean": re.compile(r"^(?:true|false|True|False|TRUE|FALSE|V|F|v|f|verdadeiro|falso|Verdadeiro|Falso)$"),
    "scientific": re.compile(r"^-?\d+\.?\d*[eE][+-]?\d+$"),
    "fraction": re.compile(r"^-?\d+\s*/\s*\d+$"),
    "tuple": re.compile(r"^\(.+\)$"),
    "set": re.compile(r"^\{.*\}$"),
    "smiles": re.compile(r"^[A-Z][a-z]?[0-9]?(?:\([^)]*\))?[=#]?[A-Za-z0-9]+$"),
    "math_expr": re.compile(r"^[\d\s+\-*/^()\w]+$"),
    "code_snippet": re.compile(
        r"(?:def |class |import |function |let |var |const |->|=>|return\s)"
    ),
    "move_sequence": re.compile(
        r"^[a-h][1-8]-[a-h][1-8](?:\s+[a-h][1-8]-[a-h][1-8])*$"
    ),
}

FLEX_PATTERNS: Dict[str, re.Pattern] = {
    "integer": re.compile(r"^-?\s*\d+\s*$"),
    "float": re.compile(r"^-?\s*\d+\.?\d*(?:\s*[eE]\s*[+-]?\s*\d+)?\s*$"),
    "boolean": re.compile(
        r"^(?:true|false|True|False|TRUE|FALSE|V|F|v|f|yes|no|Yes|No|sim|não|verdadeiro|falso)$"
    ),
    "scientific": re.compile(r"^-?\s*\d+\.?\d*\s*[eE]\s*[+-]?\s*\d+\s*$"),
    "fraction": re.compile(r"^-?\s*\d+\s*/\s*\d+\s*$"),
    "tuple": re.compile(r"^\(?\s*.+\s*\)?$"),
    "set": re.compile(r"^\{?\s*.*\s*\}?$"),
    "number_word": re.compile(
        r"^(?:zero|um|dois|três|quatro|cinco|seis|sete|oito|nove|dez|"
        r"one|two|three|four|five|six|seven|eight|nine|ten)$",
        re.IGNORECASE,
    ),
}

NUMBER_WORDS: Dict[str, int] = {
    "zero": 0, "um": 1, "dois": 2, "três": 3, "quatro": 4,
    "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

# ─── Utilitários ────────────────────────────────────────────────────


def levenshtein(a: str, b: str) -> int:
    """Calcula distância de Levenshtein entre duas strings."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def normalize(s: str) -> str:
    """Normaliza string: trim, collapse whitespace, lowercase."""
    return re.sub(r"\s+", " ", s).strip().lower()


def strip_punctuation(s: str) -> str:
    """Remove pontuação básica para comparação."""
    return re.sub(r"[.,;:!?\"'()\[\]{}]", "", s)


def parse_expected_answer(path: str) -> ExpectedAnswer:
    """Carrega expected.json e retorna ExpectedAnswer."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ExpectedAnswer.from_dict(data)


def load_answer_text(path: str) -> str:
    """Carrega answer.txt."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


# ─── Verificador de Expressões Numéricas ────────────────────────────


def _eval_expression(expr: str):
    """Avalia expressão matemática simples com segurança."""
    safe = re.sub(r"[^0-9+\-*/^().%\s]", "", expr)
    safe = safe.replace("^", "**")
    if not safe.strip():
        return None
    try:
        return eval(safe, {"__builtins__": {}}, {})
    except Exception:
        return None


def _numbers_close(a: Any, b: Any, tolerance: float = 0.0) -> bool:
    """Compara números com tolerância."""
    try:
        fa, fb = float(a), float(b)
        if tolerance > 0:
            return abs(fa - fb) <= tolerance
        return abs(fa - fb) < 1e-9
    except (ValueError, TypeError):
        return False


# ─── Estágio 1: Regex (Verificação Rígida) ──────────────────────────


def stage1_regex(answer: str, expected: ExpectedAnswer) -> VerificationResult:
    """Verificação rápida por padrão regex exato."""
    start = time.perf_counter()
    issues: List[str] = []
    passed = False
    confidence = 0.0
    details = ""

    ans_stripped = answer.strip()
    exp_type = expected.type

    # 1. Match de tipo
    pattern = REGEX_PATTERNS.get(exp_type)
    if pattern:
        if pattern.match(ans_stripped):
            type_ok = True
        else:
            type_ok = False
            issues.append(f"Formato não corresponde ao tipo esperado '{exp_type}'")
    else:
        type_ok = True  # tipos sem pattern específico passam

    # 2. Comparação de valor
    if type_ok:
        if exp_type in ("integer", "float", "scientific"):
            try:
                ans_val = float(ans_stripped)
                exp_val = float(expected.value)
                if _numbers_close(ans_val, exp_val, expected.tolerance):
                    passed = True
                    confidence = 1.0
                    details = f"Valor numérico {ans_val} corresponde ao esperado {exp_val}"
                else:
                    issues.append(
                        f"Valor {ans_val} difere do esperado {exp_val}"
                    )
                    details = f"Valor {ans_val} != {exp_val}"
            except ValueError:
                issues.append(f"Valor '{ans_stripped}' não é numérico")
                details = "Falha ao converter valor numérico"

        elif exp_type == "boolean":
            ans_bool = ans_stripped.lower() in ("true", "v", "t", "yes", "verdadeiro")
            exp_bool = str(expected.value).lower() in (
                "true",
                "v",
                "t",
                "yes",
                "verdadeiro",
            )
            if ans_bool == exp_bool:
                passed = True
                confidence = 1.0
                details = f"Booleano {ans_bool} corresponde"
            else:
                issues.append(f"Booleano {ans_bool} != {exp_bool}")
                details = "Valor booleano divergente"

        elif exp_type == "fraction":
            try:
                # Avalia fração como divisão
                num, den = re.split(r"\s*/\s*", ans_stripped)
                ans_val = float(num) / float(den)
                exp_val = _eval_expression(str(expected.value)) or float(expected.value)
                if _numbers_close(ans_val, exp_val, expected.tolerance):
                    passed = True
                    confidence = 1.0
                    details = f"Fração {ans_stripped} = {ans_val} corresponde"
                else:
                    issues.append(f"Fração {ans_stripped} = {ans_val} != {exp_val}")
                    details = "Valor de fração divergente"
            except (ValueError, ZeroDivisionError) as e:
                issues.append(f"Erro ao avaliar fração: {e}")
                details = "Falha na avaliação da fração"

        elif exp_type in ("expression", "math_expr"):
            ans_val = _eval_expression(ans_stripped)
            exp_val = _eval_expression(str(expected.value))
            if ans_val is not None and exp_val is not None:
                if _numbers_close(ans_val, exp_val, expected.tolerance):
                    passed = True
                    confidence = 0.95
                    details = f"Expressão avaliada: {ans_val} ≈ {exp_val}"
                else:
                    issues.append(f"Expressão {ans_val} != {exp_val}")
                    details = "Resultado da expressão diverge"
            else:
                issues.append("Não foi possível avaliar expressão")
                details = "Falha na avaliação da expressão"

        elif exp_type == "string":
            if ans_stripped == str(expected.value):
                passed = True
                confidence = 1.0
                details = "String corresponde exatamente"
            else:
                issues.append("String não corresponde exatamente")
                details = "String divergente"

        elif exp_type == "code_snippet":
            # Verifica presença de keywords
            has_code = REGEX_PATTERNS["code_snippet"].search(ans_stripped)
            if has_code:
                passed = True
                confidence = 0.9
                details = "Código detectado por padrões sintáticos"
            else:
                issues.append("Nenhum padrão de código detectado")
                details = "Sem sinais de snippet de código"

        elif exp_type == "set":
            passed = True
            confidence = 0.8
            details = "Formato de conjunto reconhecido"

        else:
            # Fallback: igualdade exata
            if ans_stripped == str(expected.value):
                passed = True
                confidence = 0.9
                details = "Correspondência exata"
            else:
                issues.append("Sem correspondência exata")
                details = "Fallback: sem match"

    elapsed = (time.perf_counter() - start) * 1000
    return VerificationResult("regex", passed, confidence, issues, details, elapsed)


# ─── Estágio 2: Regex Flexível ──────────────────────────────────────


def stage2_flex_regex(answer: str, expected: ExpectedAnswer) -> VerificationResult:
    """Regex relaxado com Levenshtein e equivalências."""
    start = time.perf_counter()
    issues: List[str] = []
    passed = False
    confidence = 0.0
    details = ""

    ans_norm = normalize(answer)
    exp_val = str(expected.value)
    exp_norm = normalize(exp_val)
    exp_type = expected.type

    # 1. Tenta pattern flexível
    flex_pass = False
    flex = FLEX_PATTERNS.get(exp_type)
    if flex and flex.match(answer.strip()):
        flex_pass = True
        confidence = max(confidence, 0.8)
        details = f"Flex pattern match ({exp_type})"

    # 2. Tenta fuzzy: Levenshtein ≤ 2 para respostas curtas
    fuzzy_pass = False
    if len(ans_norm) <= 20 and len(exp_norm) <= 20:
        dist = levenshtein(ans_norm, exp_norm)
        if dist <= 2:
            fuzzy_pass = True
            confidence = max(confidence, 0.7)
            details = f"Fuzzy match (Levenshtein={dist} ≤ 2)"

    # 3. Tenta equivalência numérica
    num_pass = False
    try:
        ans_num = float(answer.strip())
        exp_num = float(expected.value)
        if _numbers_close(ans_num, exp_num, expected.tolerance):
            num_pass = True
            confidence = max(confidence, 0.95)
            details = f"Numeric equivalence: {ans_num} ≈ {exp_num}"
    except (ValueError, TypeError):
        pass

    # 4. Tenta palavra → número
    word_pass = False
    ans_clean = strip_punctuation(ans_norm)
    if ans_clean in NUMBER_WORDS:
        word_val = NUMBER_WORDS[ans_clean]
        try:
            exp_num_val = float(expected.value)
            if _numbers_close(float(word_val), exp_num_val, expected.tolerance):
                word_pass = True
                confidence = max(confidence, 0.85)
                details = f"Word-to-number: '{ans_clean}' → {word_val}"
        except (ValueError, TypeError):
            pass

    # 5. Tenta alternativas
    alt_pass = False
    for alt in expected.alternatives:
        alt_norm = normalize(alt)
        if ans_norm == alt_norm or levenshtein(ans_norm, alt_norm) <= 2:
            alt_pass = True
            confidence = max(confidence, 0.9)
            details = f"Alternative match: '{ans_norm}' ≈ '{alt_norm}'"
            break

    # 6. Normalização + equivalência semântica leve
    norm_pass = False
    ans_nopunct = strip_punctuation(ans_norm)
    exp_nopunct = strip_punctuation(exp_norm)
    if ans_nopunct == exp_nopunct:
        norm_pass = True
        confidence = max(confidence, 0.85)
        details = "Match pós-normalização (sem pontuação)"

    passed = flex_pass or fuzzy_pass or num_pass or word_pass or alt_pass or norm_pass

    if not passed:
        issues.append("Nenhum padrão flexível correspondeu")
        details = "Todos os métodos flexíveis falharam"
        confidence = 0.1

    elapsed = (time.perf_counter() - start) * 1000
    return VerificationResult(
        "flex_regex", passed, round(confidence, 2), issues, details, elapsed
    )


# ─── Estágio 3: LLM (Verificação Semântica Simulada) ────────────────

# Configuração para plugar LLM real posteriormente
LLM_CONFIG = {
    "provider": "simulated",
    "model": "heuristic-v1",
    "endpoint": None,
    "api_key": None,
    "threshold": 0.7,
    "use_real_llm": False,
}


def _simulate_llm_check(
    answer: str, expected: ExpectedAnswer
) -> Tuple[bool, float, List[str], str]:
    """Verificador heurístico que simula LLM. Projetado para ser substituído
    por chamada real de LLM (ex: GPT-5-mini) configurando LLM_CONFIG."""
    issues: List[str] = []
    score = 0.0
    details_parts: List[str] = []

    ans_norm = normalize(answer)
    exp_val = str(expected.value)
    exp_norm = normalize(exp_val)

    # Análise de coerência do raciocínio (simulado)
    reasoning_indicators = [
        "portanto", "logo", "assim", "concluímos", "resulta em",
        "therefore", "thus", "hence", "consequently", "so",
        "passo", "step", "então", "then", "primeiro", "first",
        "segundo", "second", "finalmente", "finally",
    ]
    reasoning_score = 0.0
    for indicator in reasoning_indicators:
        if indicator in ans_norm:
            reasoning_score = min(reasoning_score + 0.15, 1.0)
    if reasoning_score > 0:
        details_parts.append(f"Raciocínio estruturado detectado ({reasoning_score:.2f})")

    # Análise de correspondência semântica via n-gramas
    ans_words = set(ans_norm.split())
    exp_words = set(exp_norm.split())
    if ans_words and exp_words:
        overlap = len(ans_words & exp_words)
        union = len(ans_words | exp_words)
        jaccard = overlap / union if union > 0 else 0
        details_parts.append(f"Similaridade Jaccard: {jaccard:.2f}")
        score = max(score, jaccard * 0.8)

    # Correspondência numérica
    try:
        ans_nums = [
            float(x) for x in re.findall(r"-?\d+\.?\d*(?:[eE][+-]?\d+)?", answer)
        ]
        exp_nums = [
            float(x) for x in re.findall(r"-?\d+\.?\d*(?:[eE][+-]?\d+)?", exp_val)
        ]
        if ans_nums and exp_nums and len(ans_nums) == len(exp_nums):
            match_ratio = sum(
                1
                for a, e in zip(ans_nums, exp_nums)
                if _numbers_close(a, e, expected.tolerance)
            ) / len(exp_nums)
            score = max(score, match_ratio * 0.9)
            details_parts.append(f"Match numérico: {match_ratio:.0%}")
    except (ValueError, TypeError):
        pass

    # Penalidades
    if len(answer) > 5000:
        issues.append("Resposta muito longa, possível incoerência")
        score *= 0.9
    if "não sei" in ans_norm or "i don't know" in ans_norm:
        issues.append("Modelo declarou desconhecimento")
        score *= 0.3
    if answer.count("\n") > 100:
        issues.append("Muitas linhas, possível repetição")
        score *= 0.95
    if len(set(ans_norm.split())) / max(len(ans_norm.split()), 1) < 0.3:
        issues.append("Baixa diversidade lexical, possível loop")
        score *= 0.7

    # Substitui por LLM real se configurado
    if LLM_CONFIG["use_real_llm"]:
        pass  # Aqui entraria: response = call_llm_api(...)

    score = min(max(score, 0.0), 1.0)
    passed = score >= LLM_CONFIG["threshold"]
    details = "; ".join(details_parts) if details_parts else "Análise heurística concluída"
    return passed, round(score, 2), issues, details


def stage3_llm(answer: str, expected: ExpectedAnswer) -> VerificationResult:
    """Verificação semântica usando LLM (simulado ou real)."""
    start = time.perf_counter()
    passed, confidence, issues, details = _simulate_llm_check(answer, expected)
    if not passed and confidence < LLM_CONFIG["threshold"]:
        issues.append(
            f"Confiança {confidence} abaixo do limiar {LLM_CONFIG['threshold']}"
        )
    elapsed = (time.perf_counter() - start) * 1000
    return VerificationResult("llm", passed, confidence, issues, details, elapsed)


# ─── Estágio 4: Manual (Interface de Revisão Humana) ────────────────


def stage4_manual(
    answer: str,
    expected: ExpectedAnswer,
    prior_results: Optional[List[VerificationResult]] = None,
    stop_reason: Optional[str] = None,
) -> VerificationResult:
    """Gera relatório estruturado para auditor humano."""
    start = time.perf_counter()
    issues: List[str] = []
    report_parts: List[str] = []

    if stop_reason:
        report_parts.append(f"Cascata interrompida: {stop_reason}")

    if prior_results:
        failed_stages = [
            r.stage for r in prior_results if not r.passed and r.stage != "manual"
        ]
        if failed_stages:
            issues.append(f"Estágios com falha: {', '.join(failed_stages)}")
            report_parts.append(
                f"{len(failed_stages)}/{len(prior_results) - 1} estágios falharam"
            )

        all_confidences = [r.confidence for r in prior_results if r.stage != "manual"]
        avg_conf = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        report_parts.append(f"Confiança média entre estágios: {avg_conf:.2f}")
    else:
        avg_conf = 0.5
        report_parts.append("Sem resultados de estágios anteriores")

    report_parts.append("Aguardando revisão humana")
    details = "; ".join(report_parts)
    elapsed = (time.perf_counter() - start) * 1000

    return VerificationResult("manual", False, round(avg_conf, 2), issues, details, elapsed)


# ─── Pipeline Completo ──────────────────────────────────────────────


STAGE_THRESHOLDS: Dict[str, float] = {
    "regex": 0.95,
    "flex_regex": 0.90,
    "llm": 0.85,
}


def run_pipeline(answer: str, expected: ExpectedAnswer) -> List[VerificationResult]:
    """Executa os 4 estágios em cascata com parada precoce (LongCoT paper)."""
    stop_reason = None
    results: List[VerificationResult] = []

    r1 = stage1_regex(answer, expected)
    if r1.passed and r1.confidence >= STAGE_THRESHOLDS["regex"]:
        stop_reason = f"Stage 1 (regex) aprovado com confiança {r1.confidence:.2f}"
    results.append(r1)

    if stop_reason is None:
        r2 = stage2_flex_regex(answer, expected)
        if r2.passed and r2.confidence >= STAGE_THRESHOLDS["flex_regex"]:
            stop_reason = f"Stage 2 (flex_regex) aprovado com confiança {r2.confidence:.2f}"
        results.append(r2)
    else:
        r2 = VerificationResult("flex_regex", True, r1.confidence, [], f"Skipped: {stop_reason}", 0.0)
        results.append(r2)

    if stop_reason is None:
        r3 = stage3_llm(answer, expected)
        if r3.passed and r3.confidence >= STAGE_THRESHOLDS["llm"]:
            stop_reason = f"Stage 3 (llm) aprovado com confiança {r3.confidence:.2f}"
        results.append(r3)
    else:
        r3 = VerificationResult("llm", True, r1.confidence, [], f"Skipped: {stop_reason}", 0.0)
        results.append(r3)

    r4 = stage4_manual(answer, expected, prior_results=results, stop_reason=stop_reason)
    results.append(r4)

    return results


# ─── Formatação de Saída ─────────────────────────────────────────────


def format_results_table(results: List[VerificationResult]) -> str:
    """Tabela de resultados formatada para console."""
    lines = [VerificationResult.header(), "-" * 90]
    for r in results:
        lines.append(r.table_row())
    return "\n".join(lines)


def aggregate_stats(results: List[VerificationResult]) -> Dict:
    """Estatísticas agregadas de uma execução."""
    passed = sum(1 for r in results if r.passed)
    avg_conf = sum(r.confidence for r in results) / len(results)
    total_time = sum(r.time_ms for r in results)
    return {
        "passed": passed,
        "total": len(results),
        "passed_ratio": round(passed / len(results), 2),
        "avg_confidence": round(avg_conf, 2),
        "total_time_ms": round(total_time, 1),
        "per_stage": {r.stage: {"passed": r.passed, "confidence": r.confidence} for r in results},
    }


def generate_review_report(
    answer: str,
    expected: ExpectedAnswer,
    results: List[VerificationResult],
    reviewer_notes: str = "",
) -> Dict:
    """Gera relatório JSON completo para auditor humano."""
    return {
        "report_version": VERIFIER_VERSION,
        "generated_at": datetime.now().isoformat(),
        "answer_text": answer,
        "expected": asdict(expected),
        "pipeline_results": [r.to_dict() for r in results],
        "aggregate": aggregate_stats(results),
        "overall_verdict": all(r.passed for r in results if r.stage != "manual"),
        "reviewer_notes": reviewer_notes,
        "requires_human_review": True,
    }


# ─── Dados de Demonstração ────────────────────────────────────────────


def _build_demo_samples() -> List[AnswerSample]:
    """Gera 5 amostras para demonstração."""
    return [
        AnswerSample(
            question="Calcule a integral definida ∫₀¹ x² dx",
            answer="0.333",
            expected=ExpectedAnswer(
                value=1.0 / 3.0,
                type="float",
                tolerance=0.01,
                dimension="D1",
                task_id="D1-N3-01",
            ),
            is_correct=True,
            reasoning="1/3 = 0.333..., dentro da tolerância 0.01",
        ),
        AnswerSample(
            question="A função f(x)=x² é contínua em ℝ?",
            answer="verdadeiro",
            expected=ExpectedAnswer(
                value=True,
                type="boolean",
                dimension="D1",
                task_id="D1-N1-02",
            ),
            is_correct=True,
            reasoning="Polinômios são contínuos em todo ℝ. 'verdadeiro' é equivalente a True.",
        ),
        AnswerSample(
            question="Resolva a equação: 2x + 5 = 13",
            answer="4",
            expected=ExpectedAnswer(
                value=4,
                type="integer",
                dimension="D1",
                task_id="D1-N1-03",
            ),
            is_correct=True,
            reasoning="2x + 5 = 13 → 2x = 8 → x = 4",
        ),
        AnswerSample(
            question="Qual a fórmula da força segundo Newton?",
            answer="F = m * a^2",
            expected=ExpectedAnswer(
                value="F = m * a",
                type="expression",
                dimension="D2",
                task_id="D2-N1-04",
            ),
            is_correct=False,
            reasoning="Erro comum: F = m * a (segunda lei), não a²",
        ),
        AnswerSample(
            question="Calcule a média de [2, 4, 6, 8]",
            answer="5.0",
            expected=ExpectedAnswer(
                value=5,
                type="float",
                tolerance=0.001,
                dimension="D3",
                task_id="D3-N1-05",
            ),
            is_correct=True,
            reasoning="(2+4+6+8)/4 = 20/4 = 5.0",
        ),
    ]


# ─── CLI ─────────────────────────────────────────────────────────────


def cmd_verify(answer_path: str, expected_path: str):
    """Executa pipeline completo e exibe resultados."""
    answer = load_answer_text(answer_path)
    expected = parse_expected_answer(expected_path)
    results = run_pipeline(answer, expected)

    print(f"\n{'=' * 90}")
    print(f"  Cascade Verification — {Path(answer_path).name}")
    print(f"{'=' * 90}")
    print(f"  Question: {expected.task_id} ({DIMENSION_NAMES.get(expected.dimension, '')})")
    print(f"  Expected: {expected.value} ({expected.type})")
    print(f"  Answer:   {answer[:120]}{'...' if len(answer) > 120 else ''}")
    print()
    print(format_results_table(results))
    print()
    stats = aggregate_stats(results)
    print(f"  {'✓ APROVADO' if all(r.passed for r in results if r.stage != 'manual') else '✗ REJEITADO'}"
          f" | Passed: {stats['passed']}/{stats['total']}"
          f" | Avg Confidence: {stats['avg_confidence']}"
          f" | Total: {stats['total_time_ms']:.1f}ms")

    # Salva relatório
    report_path = SCRIPT_DIR / f"cascade_report_{Path(answer_path).stem}.json"
    report = generate_review_report(answer, expected, results)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  Relatório salvo: {report_path}")
    return results


def cmd_stage(stage: str, answer_path: str, expected_path: str):
    """Executa um único estágio."""
    answer = load_answer_text(answer_path)
    expected = parse_expected_answer(expected_path)

    stage_map = {
        "regex": stage1_regex,
        "flex": stage2_flex_regex,
        "flex_regex": stage2_flex_regex,
        "llm": stage3_llm,
        "manual": stage4_manual,
    }

    func = stage_map.get(stage)
    if not func:
        print(f"✗ Estágio inválido: {stage}")
        print(f"  Opções: regex, flex_regex, llm, manual")
        sys.exit(1)

    prior = None
    if stage == "manual":
        prior = [
            stage1_regex(answer, expected),
            stage2_flex_regex(answer, expected),
            stage3_llm(answer, expected),
        ]
        result = stage4_manual(answer, expected, prior_results=prior)
    else:
        result = func(answer, expected)

    print(f"\n{'=' * 60}")
    print(f"  Stage: {result.stage.upper()}")
    print(f"{'=' * 60}")
    print(f"  {'✓ PASSED' if result.passed else '✗ FAILED'}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Time: {result.time_ms:.2f}ms")
    print(f"  Details: {result.details}")
    if result.issues:
        print(f"  Issues ({len(result.issues)}):")
        for issue in result.issues:
            print(f"    • {issue}")

    return result


def cmd_demo():
    """Executa demonstração com 5 amostras."""
    samples = _build_demo_samples()
    all_stats: List[Dict] = []

    print(f"\n{'=' * 100}")
    print(f"  CORA-Eval Cascade Verifier v{VERIFIER_VERSION} — Demo Mode")
    print(f"  Simulando o pipeline de verificação do LongCoT paper (4 estágios)")
    print(f"{'=' * 100}")

    for i, sample in enumerate(samples, 1):
        print(f"\n{'─' * 100}")
        print(f"  Sample #{i}: {sample.question[:80]}")
        print(f"  Correct: {'✓' if sample.is_correct else '✗'} | "
              f"Expected: {sample.expected.value} ({sample.expected.type}) | "
              f"Answer: {sample.answer}")
        print(f"  Reasoning: {sample.reasoning}")
        print(f"{'─' * 100}")

        results = run_pipeline(sample.answer, sample.expected)
        print(format_results_table(results))

        stats = aggregate_stats(results)
        all_stats.append(stats)
        print(f"  → {'PASS' if all(r.passed for r in results if r.stage != 'manual') else 'FAIL'}")

    # Tabela agregada
    print(f"\n{'=' * 100}")
    print(f"  Aggregate Results")
    print(f"{'=' * 100}")
    print(f"{'Sample':<10} {'Regex':<10} {'FlexRegex':<12} {'LLM':<10} {'Manual':<10} {'AvgConf':<10}")
    print(f"{'-' * 60}")
    for i, stats in enumerate(all_stats, 1):
        s = stats["per_stage"]
        label = f"#{i}"
        print(
            f"{label:<10} "
            f"{'✓' if s['regex']['passed'] else '✗':<10} "
            f"{'✓' if s['flex_regex']['passed'] else '✗':<12} "
            f"{'✓' if s['llm']['passed'] else '✗':<10} "
            f"{'✗':<10} "
            f"{stats['avg_confidence']:<10.2f}"
        )

    # Totais
    total_pass = sum(1 for s in all_stats if s["passed"] >= 3)
    print(f"\n  Overall: {total_pass}/{len(samples)} samples fully approved")
    print(f"  Average confidence across all: "
          f"{sum(s['avg_confidence'] for s in all_stats) / len(all_stats):.2f}")
    print(f"  Average time per sample: "
          f"{sum(s['total_time_ms'] for s in all_stats) / len(all_stats):.1f}ms")

    # Salva relatório consolidado
    demo_report = {
        "version": VERIFIER_VERSION,
        "mode": "demo",
        "timestamp": datetime.now().isoformat(),
        "samples": [
            {
                "question": s.question,
                "answer": s.answer,
                "expected": asdict(s.expected),
                "is_correct": s.is_correct,
                "reasoning": s.reasoning,
            }
            for s in samples
        ],
        "per_sample_stats": all_stats,
        "summary": {
            "total_samples": len(samples),
            "approved": total_pass,
            "avg_confidence": round(
                sum(s["avg_confidence"] for s in all_stats) / len(all_stats), 2
            ),
            "avg_time_ms": round(
                sum(s["total_time_ms"] for s in all_stats) / len(all_stats), 1
            ),
        },
    }
    report_path = SCRIPT_DIR / "cascade_demo_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(demo_report, f, indent=2, ensure_ascii=False)
    print(f"\n  Demo report saved: {report_path}")


def cmd_report(results_path: str):
    """Gera relatório de revisão humana a partir de results.json."""
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n{'=' * 90}")
    print(f"  Human Review Report — {Path(results_path).name}")
    print(f"{'=' * 90}")

    if "pipeline_results" in data:
        print(f"\n  Pipeline Results:")
        print(f"  {'Stage':<14} {'Passed':<8} {'Confidence':<12} {'Issues':<10}")
        print(f"  {'-' * 50}")
        for r in data["pipeline_results"]:
            print(
                f"  {r['stage']:<14} {'✓' if r['passed'] else '✗':<8} "
                f"{r['confidence']:<12.2f} {len(r['issues']):<10}"
            )
        if "aggregate" in data:
            agg = data["aggregate"]
            print(f"\n  Aggregate: {agg['passed']}/{agg['total']} passed")
            print(f"  Avg Confidence: {agg['avg_confidence']}")
            print(f"  Total Time: {agg['total_time_ms']}ms")

    print(f"\n  {'OVERALL VERDICT: APPROVED' if data.get('overall_verdict') else 'OVERALL VERDICT: NEEDS REVIEW'}")
    print(f"  Generated: {data.get('generated_at', 'N/A')}")
    print(f"\n  Reviewer Notes: {data.get('reviewer_notes', '(empty)')}")
    print(f"\n  To add notes, edit the 'reviewer_notes' field in {results_path}")

    return data


def cmd_validate(test_file: str):
    """Valida um arquivo de teste Python usando os verificadores."""
    spec = importlib.util.spec_from_file_location("test_module", test_file)
    if spec is None or spec.loader is None:
        print(f"✗ Não foi possível carregar spec de {test_file}")
        sys.exit(1)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"✗ Erro ao carregar módulo: {e}")
        sys.exit(1)

    # Procura funções de teste
    test_funcs = [
        name for name in dir(mod) if name.startswith("test_") and callable(getattr(mod, name))
    ]
    if not test_funcs:
        print(f"✗ Nenhuma função test_* encontrada em {test_file}")
        sys.exit(1)

    print(f"\n{'=' * 90}")
    print(f"  Validating test file: {test_file}")
    print(f"  Found {len(test_funcs)} test functions")
    print(f"{'=' * 90}")

    passed = 0
    failed = 0
    for func_name in test_funcs:
        func = getattr(mod, func_name)
        try:
            func()
            print(f"  ✓ {func_name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {func_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {func_name}: [ERROR] {e}")
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed, {len(test_funcs)} total")
    return passed, failed


# ─── Entry Point ───────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "--verify":
        if len(sys.argv) < 4:
            print("Uso: python cascade_verifier.py --verify <answer.txt> <expected.json>")
            sys.exit(1)
        cmd_verify(sys.argv[2], sys.argv[3])

    elif cmd == "--stage":
        if len(sys.argv) < 5:
            print(
                "Uso: python cascade_verifier.py --stage <regex|flex_regex|llm|manual> "
                "<answer.txt> <expected.json>"
            )
            sys.exit(1)
        cmd_stage(sys.argv[2], sys.argv[3], sys.argv[4])

    elif cmd == "--demo":
        cmd_demo()

    elif cmd == "--report":
        if len(sys.argv) < 3:
            print("Uso: python cascade_verifier.py --report <results.json>")
            sys.exit(1)
        cmd_report(sys.argv[2])

    elif cmd == "--validate":
        if len(sys.argv) < 3:
            print("Uso: python cascade_verifier.py --validate <test_file.py>")
            sys.exit(1)
        cmd_validate(sys.argv[2])

    elif cmd in ("-h", "--help"):
        print(__doc__)

    else:
        print(f"Comando desconhecido: {cmd}")
        print("Use --help para ver as opções.")
        sys.exit(1)


if __name__ == "__main__":
    main()
