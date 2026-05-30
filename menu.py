#!/usr/bin/env python3
"""
menu.py — Painel de Controle Adaptativo SDD+TDD+AutoEvolve
============================================================
Auto-descobre documentos, testes, pipelines, backups e comandos
registrados para construir o menu dinamicamente.

Funciona em QUALQUER projeto LaTeX com estrutura:
    projeto/
    ├── menu.py              (este arquivo)
    ├── *.tex                (documentos-fonte)
    ├── tests/               (suites TDD)
    │   ├── test_*.py
    │   ├── run_all_tests.py
    │   └── reports/
    ├── orchestration/       (pipeline e framework)
    │   ├── *.py
    │   ├── refinement_loop.py
    │   ├── backups/
    │   ├── evolutions/
    │   ├── FRAMEWORK.md
    │   └── SPEC_ORCHESTRATION.md
    └── .menu_registry.json  (opcional: comandos customizados)

Uso:
    python menu.py                  # menu interativo
    python menu.py --quick          # diagnóstico rápido
    python menu.py --list           # listar itens descobertos
    python menu.py <numero>         # executar opção diretamente
    python menu.py --help           # esta mensagem
"""

# ============================================================
# IMPORTS
# ============================================================
from __future__ import annotations
import sys
import os
import json
import re
import subprocess
import shutil
import textwrap
from datetime import datetime
from pathlib import Path
from typing import (
    List, Dict, Optional, Tuple, Callable, Any, NamedTuple,
    Union, Sequence
)
from dataclasses import dataclass, field
from enum import Enum, auto

# ── CORREÇÃO DE ENCODING PARA WINDOWS ────────────────────
# Garante que caracteres Unicode sejam exibidos corretamente
# mesmo quando a saída é redirecionada (pipe, redirecionamento)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (ValueError, OSError):
        pass
elif hasattr(sys.stdout, 'encoding') and sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    # Fallback: definir variável de ambiente para forçar UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# ============================================================
# CONSTANTES DE APRESENTAÇÃO
# ============================================================
C = {
    "VERDE": "\033[92m",
    "VERMELHO": "\033[91m",
    "AMARELO": "\033[93m",
    "AZUL": "\033[94m",
    "MAGENTA": "\033[95m",
    "CIANO": "\033[96m",
    "BOLD": "\033[1m",
    "RESET": "\033[0m",
    "CINZA": "\033[90m",
    "LARANJA": "\033[38;5;208m",
}

# Categorias do menu
class Categoria(str, Enum):
    OPERACIONAR = "OPERACIONAR"
    REPRODUZIR  = "REPRODUZIR"
    REGISTRAR   = "REGISTRAR"
    AUDITAR     = "AUDITAR"
    APRENDER    = "APRENDER"
    FERRAMENTAS = "FERRAMENTAS"

    @property
    def cor(self) -> str:
        return {
            Categoria.OPERACIONAR: "VERDE",
            Categoria.REPRODUZIR:  "AMARELO",
            Categoria.REGISTRAR:   "AZUL",
            Categoria.AUDITAR:     "MAGENTA",
            Categoria.APRENDER:    "LARANJA",
            Categoria.FERRAMENTAS: "CIANO",
        }[self]

    @property
    def icone(self) -> str:
        return {
            Categoria.OPERACIONAR: "▶",
            Categoria.REPRODUZIR:  "↻",
            Categoria.REGISTRAR:   "✎",
            Categoria.AUDITAR:     "✓",
            Categoria.APRENDER:    "○",
            Categoria.FERRAMENTAS: "⚙",
        }[self]


# ============================================================
# MODELOS DE DADOS
# ============================================================

@dataclass
class TexDocument:
    """Documento LaTeX descoberto."""
    path: str
    nome: str
    tem_log: bool = False
    tem_pdf: bool = False
    paginas: int = 0
    tamanho_kb: float = 0.0

    @property
    def base(self) -> str:
        return os.path.splitext(self.nome)[0]


@dataclass
class TestSuite:
    """Suíte de teste descoberta."""
    path: str
    nome: str
    descricao: str = ""
    ultimo_status: Optional[str] = None  # PASS / FAIL / nunca


@dataclass
class Pipeline:
    """Script de pipeline descoberto."""
    path: str
    nome: str
    descricao: str = ""


@dataclass
class BackupItem:
    """Backup descoberto."""
    path: str
    nome: str
    timestamp: str = ""
    tamanho_kb: float = 0.0
    data_hora: str = ""


@dataclass
class InsightItem:
    """Arquivo de insight descoberto."""
    path: str
    nome: str
    data: str = ""


@dataclass
class RegisteredCommand:
    """Comando registrado via .menu_registry.json."""
    id: str
    nome: str
    descricao: str
    categoria: str
    comando: List[str]
    cwd: str = "."
    timeout: int = 120


# Ação do menu — pode ser builtin, descoberta ou registrada
@dataclass
class MenuAction:
    """Uma ação executável no menu."""
    id: str
    nome: str
    descricao: str
    categoria: Categoria
    origem: str  # builtin | discovered | registered
    executar: Callable[[], int]
    item_ref: Any = None  # referência ao item original (TexDoc, etc.)


@dataclass
class MenuCatalog:
    """Catálogo completo de tudo que foi descoberto."""
    tex_files: List[TexDocument] = field(default_factory=list)
    test_suites: List[TestSuite] = field(default_factory=list)
    pipelines: List[Pipeline] = field(default_factory=list)
    backups: List[BackupItem] = field(default_factory=list)
    insights: List[InsightItem] = field(default_factory=list)
    registered: List[RegisteredCommand] = field(default_factory=list)

    @property
    def tem_multiplos_tex(self) -> bool:
        return len(self.tex_files) > 1

    @property
    def primeiro_tex(self) -> Optional[TexDocument]:
        return self.tex_files[0] if self.tex_files else None


# ============================================================
# UTILITÁRIOS DE DISPLAY
# ============================================================

def _c(cor: str, texto: str) -> str:
    """Aplica cor ANSI se terminal suportar."""
    if not sys.stdout.isatty():
        return texto
    code = C.get(cor, "")
    if not code:
        return texto
    return f"{code}{texto}{C['RESET']}"


def _cabecalho(titulo: str):
    """Exibe cabeçalho formatado."""
    largura = 68
    print()
    print(_c("CIANO", "╔" + "═" * largura + "╗"))
    linhas = titulo.split("\n")
    for linha in linhas:
        esp = (largura - len(linha)) // 2
        print(_c("CIANO", "║") + " " * esp + _c("BOLD", linha) + " " * (largura - esp - len(linha)) + _c("CIANO", "║"))
    print(_c("CIANO", "╚" + "═" * largura + "╝"))
    print()


def _sub(titulo: str):
    """Exibe subtítulo."""
    print(f"\n  {_c('AZUL', '▶')} {_c('BOLD', titulo)}")
    print(f"  {_c('CINZA', '─' * 60)}")


def _ok(msg: str):
    print(f"  {_c('VERDE', '✓')} {msg}")


def _fail(msg: str):
    print(f"  {_c('VERMELHO', '✗')} {msg}")


def _warn(msg: str):
    print(f"  {_c('AMARELO', '⚠')} {msg}")


def _info(msg: str):
    print(f"    {_c('CINZA', msg)}")


def _enter():
    """Aguarda Enter. Se não houver stdin (pipe/automation), prossegue."""
    try:
        input(f"\n  {_c('CINZA', '[Enter] para continuar...')}")
    except EOFError:
        pass  # modo não-interativo


def _limpar():
    """Limpa terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ler_json(caminho: str):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _escrever_json(caminho: str, dados: dict):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


# ============================================================
# DISCOVERY ENGINE
# ============================================================

class DiscoveryEngine:
    """Varre o diretório do projeto e descobre todos os artefatos."""

    def __init__(self, base_dir: str):
        self.base = Path(base_dir)
        self.tests_dir = self.base / "tests"
        self.orch_dir = self.base / "orchestration"
        self.backup_dir = self.orch_dir / "backups"
        self.evolve_dir = self.orch_dir / "evolutions"
        self.reports_dir = self.tests_dir / "reports"
        self.registry_file = self.base / ".menu_registry.json"

    def scan(self) -> MenuCatalog:
        """Executa todas as varreduras e retorna o catálogo."""
        return MenuCatalog(
            tex_files=self._scan_tex(),
            test_suites=self._scan_tests(),
            pipelines=self._scan_pipelines(),
            backups=self._scan_backups(),
            insights=self._scan_insights(),
            registered=self._scan_registry(),
        )

    def _scan_tex(self) -> List[TexDocument]:
        """Descobre arquivos .tex no diretório base."""
        encontrados: List[TexDocument] = []
        for f in sorted(self.base.glob("*.tex")):
            nome = f.name
            stem = f.stem
            tex = TexDocument(
                path=str(f.resolve()),
                nome=nome,
                tem_log=(self.base / f"{stem}.log").exists(),
                tem_pdf=(self.base / f"{stem}.pdf").exists(),
                tamanho_kb=round(f.stat().st_size / 1024, 1),
            )
            # Tentar extrair páginas do .log correspondente
            if tex.tem_log:
                log_path = self.base / f"{stem}.log"
                try:
                    with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
                        conteudo = lf.read()
                    m = re.search(r"Output written on .*?\((\d+) pages?", conteudo)
                    if m:
                        tex.paginas = int(m.group(1))
                except (OSError, ValueError):
                    pass
            encontrados.append(tex)
        return encontrados

    def _scan_tests(self) -> List[TestSuite]:
        """Descobre arquivos test_*.py no diretório tests/."""
        if not self.tests_dir.exists():
            return []
        encontrados: List[TestSuite] = []
        for f in sorted(self.tests_dir.glob("test_*.py")):
            nome = f.name
            # Extrair descrição do docstring
            desc = ""
            try:
                with open(f, "r", encoding="utf-8") as tf:
                    conteudo = tf.read()
                # Pega a primeira linha do docstring
                m = re.search(r'"""(.*?)\n', conteudo, re.DOTALL)
                if m:
                    desc = m.group(1).strip().split("\n")[0][:80]
            except OSError:
                pass
            encontrados.append(TestSuite(
                path=str(f.resolve()),
                nome=nome,
                descricao=desc,
            ))
        # Verificar se existe run_all_tests.py
        runner = self.tests_dir / "run_all_tests.py"
        if runner.exists() and not any(t.nome == "run_all_tests.py" for t in encontrados):
            encontrados.append(TestSuite(
                path=str(runner.resolve()),
                nome="run_all_tests.py",
                descricao="Executor completo (compila + 3 gates)",
            ))
        return encontrados

    def _scan_pipelines(self) -> List[Pipeline]:
        """Descobre scripts .py em orchestration/ (exceto subdirs)."""
        if not self.orch_dir.exists():
            return []
        encontrados: List[Pipeline] = []
        for f in sorted(self.orch_dir.glob("*.py")):
            nome = f.name
            # Pular se for __init__ ou similar
            if nome.startswith("__"):
                continue
            desc = ""
            try:
                with open(f, "r", encoding="utf-8") as pf:
                    conteudo = pf.read()
                m = re.search(r'"""(.*?)\n', conteudo, re.DOTALL)
                if m:
                    desc = m.group(1).strip().split("\n")[0][:80]
            except OSError:
                pass
            encontrados.append(Pipeline(
                path=str(f.resolve()),
                nome=nome,
                descricao=desc,
            ))
        return encontrados

    def _scan_backups(self) -> List[BackupItem]:
        """Descobre backups .tex em orchestration/backups/."""
        if not self.backup_dir.exists():
            return []
        encontrados: List[BackupItem] = []
        for f in sorted(self.backup_dir.glob("*.tex"), reverse=True):
            stat = f.stat()
            ts = datetime.fromtimestamp(stat.st_mtime)
            encontrados.append(BackupItem(
                path=str(f.resolve()),
                nome=f.name,
                timestamp=ts.strftime("%Y%m%d_%H%M%S"),
                tamanho_kb=round(stat.st_size / 1024, 1),
                data_hora=ts.strftime("%d/%m/%Y %H:%M"),
            ))
        return encontrados

    def _scan_insights(self) -> List[InsightItem]:
        """Descobre arquivos insight_*.md em orchestration/evolutions/."""
        if not self.evolve_dir.exists():
            return []
        encontrados: List[InsightItem] = []
        for f in sorted(self.evolve_dir.glob("insight_*.md"), reverse=True):
            encontrados.append(InsightItem(
                path=str(f.resolve()),
                nome=f.name,
                data=f.stem.replace("insight_", ""),
            ))
        return encontrados

    def _scan_registry(self) -> List[RegisteredCommand]:
        """Lê .menu_registry.json se existir."""
        if not self.registry_file.exists():
            return []
        try:
            with open(self.registry_file, "r", encoding="utf-8") as rf:
                dados = json.load(rf)
            comandos = []
            for item in dados.get("commands", []):
                comandos.append(RegisteredCommand(
                    id=item.get("id", "unknown"),
                    nome=item.get("name", "Sem nome"),
                    descricao=item.get("description", ""),
                    categoria=item.get("category", Categoria.FERRAMENTAS.value),
                    comando=item.get("command", []),
                    cwd=item.get("cwd", "."),
                    timeout=item.get("timeout", 120),
                ))
            return comandos
        except (json.JSONDecodeError, OSError) as e:
            print(f"  {_c('AMARELO', '⚠')} Erro ao ler .menu_registry.json: {e}")
            return []


# ============================================================
# RUNNER ENGINE
# ============================================================

class RunnerEngine:
    """Executa comandos com segurança, timeout e captura de saída."""

    @staticmethod
    def pdflatex(tex_path: str, passes: int = 2, timeout: int = 120) -> Tuple[int, str]:
        """Compila documento .tex com N passes."""
        cwd = os.path.dirname(tex_path)
        tex_name = os.path.basename(tex_path)
        ultima_saida = ""
        for i in range(passes):
            print(f"    Passo {i+1}/{passes}... ", end="", flush=True)
            try:
                r = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_name],
                    cwd=cwd, capture_output=True, text=True, timeout=timeout
                )
                ultima_saida = r.stdout
                if r.returncode == 0:
                    _ok(f"OK (exit {r.returncode})")
                else:
                    _fail(f"exit={r.returncode}")
                    for linha in r.stdout.split("\n")[-5:]:
                        if linha.strip():
                            _info(linha.strip()[:120])
            except FileNotFoundError:
                _fail("pdflatex não encontrado! TeX Live instalado?")
                return 1, "pdflatex not found"
            except subprocess.TimeoutExpired:
                _fail(f"Timeout após {timeout}s")
                return 1, "timeout"
        return 0, ultima_saida

    @staticmethod
    def python(script_path: str, cwd: Optional[str] = None,
               timeout: int = 120, args: Optional[List[str]] = None) -> Tuple[int, str, str]:
        """Executa script Python e retorna (exit_code, stdout, stderr)."""
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        try:
            r = subprocess.run(
                cmd, cwd=cwd or os.path.dirname(script_path),
                capture_output=True, text=True, timeout=timeout
            )
            return r.returncode, r.stdout, r.stderr
        except FileNotFoundError:
            return 1, "", f"Python não encontrado: {sys.executable}"
        except subprocess.TimeoutExpired:
            return 1, "", f"Timeout após {timeout}s"

    @staticmethod
    def comando(comando: List[str], cwd: str = ".",
                timeout: int = 120) -> Tuple[int, str, str]:
        """Executa comando arbitrário com timeout."""
        try:
            r = subprocess.run(
                comando, cwd=cwd,
                capture_output=True, text=True, timeout=timeout
            )
            return r.returncode, r.stdout, r.stderr
        except FileNotFoundError as e:
            return 1, "", f"Comando não encontrado: {e}"
        except subprocess.TimeoutExpired:
            return 1, "", f"Timeout após {timeout}s"

    @staticmethod
    def testar(test_path: str, cwd: Optional[str] = None,
               timeout: int = 120) -> Tuple[int, str, str]:
        """Executa um arquivo de teste Python."""
        return RunnerEngine.python(test_path, cwd, timeout)


# ============================================================
# OPERAÇÕES BUILT-IN
# ============================================================

class BuiltinOperations:
    """Operações nativas do framework. Recebem o catálogo e o diretório."""

    def __init__(self, catalog: MenuCatalog, base_dir: str):
        self.cat = catalog
        self.base = base_dir

    # ── PROPRIEDADES DERIVADAS ──────────────────────────────

    @property
    def tex_primario(self) -> Optional[TexDocument]:
        """Retorna o .tex principal (primeiro ou único)."""
        return self.cat.primeiro_tex

    @property
    def tex_path(self) -> Optional[str]:
        t = self.tex_primario
        return t.path if t else None

    @property
    def log_path(self) -> Optional[str]:
        t = self.tex_primario
        if t:
            return os.path.join(self.base, f"{t.base}.log")
        return None

    @property
    def pdf_path(self) -> Optional[str]:
        t = self.tex_primario
        if t:
            return os.path.join(self.base, f"{t.base}.pdf")
        return None

    @property
    def fix_history_path(self) -> str:
        return os.path.join(self.base, "orchestration", "fix_history.json")

    @property
    def tests_dir(self) -> str:
        return os.path.join(self.base, "tests")

    @property
    def orch_dir(self) -> str:
        return os.path.join(self.base, "orchestration")

    @property
    def reports_dir(self) -> str:
        return os.path.join(self.tests_dir, "reports")

    # ── OPERACIONAR ─────────────────────────────────────────

    def compilar(self, tex: Optional[TexDocument] = None) -> int:
        """Compilar documento .tex (2 passes)."""
        alvo = tex or self.tex_primario
        if not alvo:
            _fail("Nenhum arquivo .tex encontrado para compilar!")
            _enter()
            return 1

        _sub(f"Compilando: {alvo.nome} (2 passes pdflatex)")
        code, _ = RunnerEngine.pdflatex(alvo.path)

        # Verificar PDF gerado
        if alvo.tem_pdf:
            kb = alvo.tamanho_kb
            pag = alvo.paginas
            _ok(f"PDF: {kb:.1f} KB, {pag} páginas")
        else:
            # Tentar encontrar PDF mesmo assim
            pdf_caminho = os.path.join(self.base, f"{alvo.base}.pdf")
            if os.path.exists(pdf_caminho):
                kb = os.path.getsize(pdf_caminho) / 1024
                _ok(f"PDF gerado: {kb:.0f} KB")
            else:
                _warn("PDF não encontrado (verifique erros de compilação)")

        _enter()
        return code

    def compilar_escolher(self) -> int:
        """Compilar: mostra submenu se múltiplos .tex."""
        if len(self.cat.tex_files) == 1:
            return self.compilar()
        if not self.cat.tex_files:
            _fail("Nenhum arquivo .tex encontrado!")
            _enter()
            return 1

        _sub("Escolha o documento para compilar:")
        for i, tex in enumerate(self.cat.tex_files, 1):
            status = _c("VERDE", "✓") if tex.tem_pdf else _c("CINZA", "─")
            print(f"    {i}. {status} {tex.nome}  ({tex.tamanho_kb:.0f} KB)")
        try:
            esc = input(f"\n  {_c('CIANO', 'Documento nº')} {_c('CINZA', '(0=cancelar)')} {_c('CIANO', '>')} ").strip()
            n = int(esc)
            if n == 0:
                return 0
            if 1 <= n <= len(self.cat.tex_files):
                return self.compilar(self.cat.tex_files[n - 1])
            _warn("Nº inválido.")
        except (ValueError, IndexError):
            _warn("Entrada inválida.")
        _enter()
        return 1

    def testar(self, suite: Optional[TestSuite] = None) -> int:
        """Executar suíte(s) de teste TDD."""
        if suite:
            suites = [suite]
        else:
            suites = self.cat.test_suites

        if not suites:
            _fail("Nenhuma suíte de teste encontrada em tests/!")
            _enter()
            return 1

        _sub("Executando suites TDD")
        total_pass = 0
        total_fail = 0
        resultados = {}

        for s in suites:
            nome = s.nome
            print(f"\n    ── {nome} ──")
            code, stdout, stderr = RunnerEngine.testar(s.path, self.tests_dir)
            # Mostrar linhas relevantes
            for linha in stdout.split("\n"):
                if linha.strip() and any(k in linha for k in ("TEST", "PASS", "FAIL", "RESULT", "SUITE", "GATE")):
                    if "FAIL" in linha and "PASS" not in linha:
                        print(f"      {_c('VERMELHO', linha.strip())}")
                    elif "PASS" in linha:
                        print(f"      {_c('VERDE', linha.strip())}")
                    else:
                        print(f"      {_c('CINZA', linha.strip())}")

            if code == 0:
                total_pass += 1
                resultados[nome] = "PASS"
            else:
                total_fail += 1
                resultados[nome] = "FAIL"

        print(f"\n    {'─' * 40}")
        if total_fail == 0:
            _ok(f"{total_pass}/{len(suites)} suites PASSARAM")
        else:
            _fail(f"{total_fail}/{len(suites)} suites FALHARAM")

        # Salvar relatório rápido
        os.makedirs(self.reports_dir, exist_ok=True)
        rel = {
            "timestamp": datetime.now().isoformat(),
            "all_passed": total_fail == 0,
            "suites": resultados,
        }
        _escrever_json(os.path.join(self.reports_dir, f"report_{_timestamp()}.json"), rel)
        _enter()
        return 0 if total_fail == 0 else 1

    def pipeline(self, script: Optional[Pipeline] = None) -> int:
        """Executar pipeline AutoEvolve."""
        alvo = script
        if not alvo:
            # Usar refinement_loop.py se existir, senão o primeiro pipeline
            for p in self.cat.pipelines:
                if "refinement" in p.nome.lower() or "loop" in p.nome.lower():
                    alvo = p
                    break
            if not alvo and self.cat.pipelines:
                alvo = self.cat.pipelines[0]

        if not alvo:
            _fail("Nenhum script de pipeline encontrado em orchestration/!")
            _enter()
            return 1

        _sub(f"Pipeline: {alvo.nome}")
        if alvo.descricao:
            _info(alvo.descricao)
        print(f"    Script: {os.path.relpath(alvo.path, self.base)}")
        print()
        code, stdout, stderr = RunnerEngine.python(alvo.path, self.orch_dir, timeout=600)
        if stdout:
            # Mostrar últimas linhas
            linhas = stdout.strip().split("\n")
            for linha in linhas[-10:]:
                if linha.strip():
                    print(f"    {linha[:120]}")
        if code == 0:
            _ok("Pipeline concluído com sucesso")
        else:
            _fail(f"Pipeline falhou (exit={code})")
            if stderr:
                for linha in stderr.strip().split("\n")[-3:]:
                    if linha.strip():
                        _info(linha[:120])
        _enter()
        return code

    # ── REPRODUZIR ──────────────────────────────────────────

    def listar_backups(self) -> List[BackupItem]:
        """Lista backups disponíveis e retorna lista."""
        _sub("Backups disponíveis")
        if not self.cat.backups:
            _info("Nenhum backup encontrado.")
            return []
        for i, b in enumerate(self.cat.backups, 1):
            print(f"    {i:2d}. {b.nome}  ({b.data_hora}, {b.tamanho_kb:.0f} KB)")
        return self.cat.backups

    def restaurar(self) -> int:
        """Restaurar backup para o .tex primário."""
        backups = self.listar_backups()
        if not backups:
            _enter()
            return 1
        if not self.tex_primario:
            _fail("Nenhum documento .tex alvo para restaurar!")
            _enter()
            return 1
        try:
            esc = input(f"\n    {_c('AMARELO', 'Nº do backup para restaurar (0=cancelar):')} ")
            n = int(esc)
            if n == 0:
                _info("Cancelado.")
                _enter()
                return 0
            if n < 1 or n > len(backups):
                _warn("Nº inválido.")
                _enter()
                return 1
            origem = backups[n - 1].path
            shutil.copy2(origem, self.tex_primario.path)
            _ok(f"Restaurado: {backups[n - 1].nome} → {self.tex_primario.nome}")
        except (ValueError, OSError) as e:
            _fail(f"Erro: {e}")
        _enter()
        return 0

    def refinamento_guiado(self) -> int:
        """Refinamento manual guiado passo a passo."""
        if not self.tex_primario:
            _fail("Nenhum documento .tex disponível!")
            _enter()
            return 1

        _sub("Refinamento Manual Guiado")
        print("    Este assistente guia você pelas etapas de diagnóstico e")
        print("    correção manual de problemas LaTeX.\n")

        tex_path = self.tex_primario.path
        tex_name = self.tex_primario.nome
        log_path = self.log_path or tex_path.replace(".tex", ".log")

        # Passo 1: Compilar
        print(f"  {_c('AZUL', 'Passo 1/4')}: Compilar documento...")
        RunnerEngine.pdflatex(tex_path, passes=2)
        _ok("Compilado.")

        # Passo 2: Diagnosticar
        print(f"\n  {_c('AZUL', 'Passo 2/4')}: Diagnosticar problemas...")
        if not os.path.exists(log_path):
            _fail("Log não encontrado após compilação")
            _enter()
            return 1
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            log = f.read()

        issues = []
        for m in re.finditer(r"Overfull \\hbox \(([0-9.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)", log):
            issues.append(("OVERFULL", float(m.group(1)), m.group(2), m.group(3)))
        for m in re.finditer(r"Underfull \\hbox \(badness (\d+)\) in paragraph at lines (\d+)--(\d+)", log):
            b = int(m.group(1))
            if b >= 10000:
                issues.append(("UNDERFULL", b, m.group(2), m.group(3)))

        if not issues:
            _ok("Nenhum problema encontrado. Documento limpo!")
        else:
            _warn(f"{len(issues)} problema(s) encontrado(s):")
            for tipo, val, li, lf in issues:
                if tipo == "OVERFULL":
                    print(f"      OVERFULL {val:.1f}pt  linhas {li}–{lf}")
                    if val < 3:
                        _info(f"     → Sugestão: auto-fix com sloppy wrapper (F01)")
                    else:
                        _info(f"     → Sugestão: encurtamento textual (F04)")
                else:
                    print(f"      UNDERFULL badness {val}  linhas {li}–{lf}")
                    _info(f"     → Sugestão: raggedright em coluna p{{}} (F02)")

        # Passo 3: Backup
        print(f"\n  {_c('AZUL', 'Passo 3/4')}: Backup automático...")
        backup_dir = os.path.join(self.base, "orchestration", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        ts = _timestamp()
        shutil.copy2(tex_path, os.path.join(backup_dir, f"{self.tex_primario.base}_{ts}.tex"))
        _ok(f"Backup salvo: {self.tex_primario.base}_{ts}.tex")

        # Passo 4: Pós-correção
        print(f"\n  {_c('AZUL', 'Passo 4/4')}: Pós-correção")
        print("    Após aplicar as correções manualmente no .tex:")
        print(f"      1. python tests\\run_all_tests.py   (validar)")
        print(f"      2. python orchestration\\refinement_loop.py   (registrar)")
        print()
        _enter()
        return 0

    # ── REGISTRAR ───────────────────────────────────────────

    def registrar_correcao(self) -> int:
        """Registrar correção manual no histórico."""
        _sub("Registrar Correção Manual no Histórico")
        print("    Preencha os dados da correção realizada:\n")
        try:
            tipo = input("    Tipo (overfull/underfull/erro/estrutura): ").strip()
            descricao = input("    Descrição da correção: ").strip()
            local = input("    Local (linhas ou seção): ").strip()
            estrategia = input("    Estratégia (F01–F10): ").strip()

            if not tipo or not descricao:
                _warn("Dados mínimos não preenchidos. Cancelado.")
                _enter()
                return 1

            historico = _ler_json(self.fix_history_path) or {"sessions": [], "fix_patterns": {}}
            entrada = {
                "timestamp": datetime.now().isoformat(),
                "tipo": tipo,
                "descricao": descricao,
                "local": local,
                "estrategia": estrategia,
            }

            historico.setdefault("manual_fixes", []).append(entrada)
            if estrategia and estrategia.startswith("F"):
                nome_padrao = {
                    "F01": "sloppy wrapper", "F02": "raggedright column",
                    "F04": "text shortening",
                }.get(estrategia, f"manual_{estrategia}")
                historico.setdefault("fix_patterns", {})
                historico["fix_patterns"][nome_padrao] = historico["fix_patterns"].get(nome_padrao, 0) + 1

            _escrever_json(self.fix_history_path, historico)
            _ok("Correção registrada com sucesso!")
        except (KeyboardInterrupt, EOFError):
            _warn("\nCancelado.")
        _enter()
        return 0

    def gerar_relatorio(self) -> int:
        """Gerar relatório de estado atual."""
        _sub("Relatório de Estado Atual")
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "documentos": [t.nome for t in self.cat.tex_files],
        }

        # Estado dos .tex
        for tex in self.cat.tex_files:
            _ok(f"Documento: {tex.nome} ({tex.tamanho_kb:.0f} KB, {tex.paginas}p)")
        if not self.cat.tex_files:
            _fail("Nenhum arquivo .tex!")

        # Estado do PDF primário
        if self.tex_primario and os.path.exists(self.pdf_path or ""):
            kb = os.path.getsize(self.pdf_path) / 1024  # type: ignore[arg-type]
            relatorio["pdf"] = {"tamanho_kb": round(kb, 1)}
            _ok(f"PDF: {kb:.0f} KB")
        else:
            relatorio["pdf"] = None
            _warn("PDF não encontrado (compile primeiro)")

        # Estado dos testes
        ultimo_rel = None
        reports_dir = self.reports_dir
        if os.path.exists(reports_dir):
            reports = sorted(Path(reports_dir).glob("*.json"), reverse=True)
            if reports:
                ultimo_rel = _ler_json(str(reports[0]))
        if ultimo_rel:
            relatorio["ultimo_teste"] = ultimo_rel
            if ultimo_rel.get("all_passed"):
                _ok("Último TDD: TODOS PASSARAM")
            else:
                _fail("Último TDD: ALGUMA SUITE FALHOU")
        else:
            relatorio["ultimo_teste"] = None
            _warn("Nenhum relatório de teste encontrado")

        # Histórico
        hist = _ler_json(self.fix_history_path)
        if hist:
            relatorio["historico"] = {
                "sessoes": len(hist.get("sessions", [])),
                "correcoes_manuais": len(hist.get("manual_fixes", [])),
                "padroes": hist.get("fix_patterns", {}),
            }
            _ok(f"Histórico: {relatorio['historico']['sessoes']} sessões, "
                f"{relatorio['historico']['correcoes_manuais']} correções manuais")
        else:
            relatorio["historico"] = None

        # Páginas do log
        log_path = self.log_path
        if log_path and os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                m = re.search(r"Output written on .*?\((\d+) pages?", f.read())
                if m:
                    relatorio["paginas"] = int(m.group(1))
                    _ok(f"Páginas: {relatorio['paginas']}")

        # Salvar
        nome_rel = f"report_estado_{_timestamp()}.json"
        caminho_rel = os.path.join(reports_dir, nome_rel)
        os.makedirs(reports_dir, exist_ok=True)
        _escrever_json(caminho_rel, relatorio)
        _ok(f"Relatório salvo: tests/reports/{nome_rel}")
        _enter()
        return 0

    # ── AUDITAR ─────────────────────────────────────────────

    def auditar_integridade(self) -> int:
        """Verificar integridade do framework."""
        _sub("Auditoria de Integridade do Framework")
        erros = 0
        avisos = 0

        # 1. Arquivos obrigatórios (só existentes)
        obrigatorios = []
        if self.tex_primario:
            obrigatorios.append((self.tex_primario.path, "Documento principal .tex"))
        for s in self.cat.test_suites:
            obrigatorios.append((s.path, f"Teste: {s.nome}"))
        for p in self.cat.pipelines:
            obrigatorios.append((p.path, f"Pipeline: {p.nome}"))

        # Arquivos de framework (sempre checar)
        framework_files = [
            (os.path.join(self.orch_dir, "SPEC_ORCHESTRATION.md"), "Spec do pipeline"),
            (os.path.join(self.orch_dir, "FRAMEWORK.md"), "Framework conceitual"),
            (os.path.join(self.orch_dir, "fix_history.json"), "Histórico de correções"),
            (os.path.join(self.tests_dir, "README.md"), "README dos testes"),
        ]
        for caminho, desc in framework_files:
            if os.path.exists(caminho):
                _ok(f"{desc} — {os.path.basename(caminho)}")
            else:
                _warn(f"{desc} — não encontrado (opcional)")
                avisos += 1

        print(f"\n  {_c('AZUL', 'Artefatos descobertos:')}")
        _ok(f"{len(self.cat.tex_files)} documento(s) .tex")
        _ok(f"{len(self.cat.test_suites)} suíte(s) de teste")
        _ok(f"{len(self.cat.pipelines)} script(s) de pipeline")
        _ok(f"{len(self.cat.backups)} backup(s) disponíveis")
        _ok(f"{len(self.cat.insights)} insight(s) de evolução")

        # 2. Integridade do JSON
        print(f"\n  {_c('AZUL', 'Integridade dos dados:')}")
        if hist := _ler_json(self.fix_history_path):
            sessoes = hist.get("sessions", [])
            _ok(f"fix_history.json: {len(sessoes)} sessões, "
                f"{len(hist.get('fix_patterns', {}))} padrões")
        else:
            _warn("fix_history.json: não lido ou vazio")
            avisos += 1

        # 3. Estrutura de diretórios
        print(f"\n  {_c('AZUL', 'Estrutura de diretórios:')}")
        for diretorio, desc in [
            (os.path.join(self.orch_dir, "backups"), "Backups"),
            (os.path.join(self.orch_dir, "evolutions"), "Evoluções/insights"),
            (self.reports_dir, "Relatórios de teste"),
        ]:
            if os.path.exists(diretorio):
                arquivos = list(Path(diretorio).iterdir())
                _ok(f"{desc}: {len(arquivos)} arquivo(s)")
            else:
                _warn(f"{desc}: diretório não existe")
                avisos += 1

        # 4. Testes com sintaxe válida
        print(f"\n  {_c('AZUL', 'Testes executáveis:')}")
        for s in self.cat.test_suites:
            r = subprocess.run([sys.executable, "-m", "py_compile", s.path],
                             capture_output=True, text=True)
            if r.returncode == 0:
                _ok(f"{s.nome}: sintaxe OK")
            else:
                _fail(f"{s.nome}: erro de sintaxe!")
                erros += 1

        # 5. Estratégias documentadas
        framework_path = os.path.join(self.orch_dir, "FRAMEWORK.md")
        if os.path.exists(framework_path):
            with open(framework_path, "r", encoding="utf-8") as f:
                conteudo = f.read()
            estrategias = re.findall(r"\|\s*(F\d{2})\s*\|", conteudo)
            if len(estrategias) >= 10:
                _ok(f"Estratégias documentadas: {len(estrategias)}")
            else:
                _warn(f"Apenas {len(estrategias)} estratégias (desejável ≥10)")
                avisos += 1

        print(f"\n    {'─' * 40}")
        if erros == 0 and avisos == 0:
            _ok("Auditoria completa: 0 erros, 0 avisos")
        elif erros == 0:
            _ok(f"Auditoria: 0 erros, {avisos} avisos")
        else:
            _fail(f"Auditoria: {erros} erro(s), {avisos} aviso(s)")
        _enter()
        return erros

    def exibir_historico(self) -> int:
        """Exibir histórico de execuções."""
        _sub("Histórico de Execuções")
        hist = _ler_json(self.fix_history_path)
        if not hist:
            _warn("Nenhum histórico encontrado.")
            _enter()
            return 1

        sessoes = hist.get("sessions", [])
        if sessoes:
            print(f"  {_c('AZUL', f'Sessões automáticas ({len(sessoes)}):')}")
            print(f"    {'Data':<22} {'Iter':<6} {'Issues':<8} {'Fixes':<8} {'Status':<10}")
            print(f"    {'─' * 54}")
            for s in sessoes:
                data = s.get("timestamp", "?").replace("T", " ")[:19]
                it = s.get("iteration", "?")
                iss = s.get("issues_found", "?")
                fx = s.get("fixes_applied", "?")
                st = "PASS" if s.get("tests_passed") else "FAIL"
                cor_st = _c("VERDE", st) if st == "PASS" else _c("VERMELHO", st)
                print(f"    {data:<22} {it:<6} {iss:<8} {fx:<8} {cor_st}")
        else:
            _warn("Nenhuma sessão registrada.")

        manuais = hist.get("manual_fixes", [])
        if manuais:
            print(f"\n  {_c('AZUL', f'Correções manuais ({len(manuais)}):')}")
            for m in manuais:
                ts = m.get("timestamp", "?")[:19]
                desc = m.get("descricao", "?")[:60]
                print(f"    • {ts} | {desc}")

        if hist.get("fix_patterns"):
            print(f"\n  {_c('AZUL', 'Padrões de correção:')}")
            for padrao, freq in sorted(hist["fix_patterns"].items(), key=lambda x: -x[1]):
                print(f"    • {padrao}: {freq}x")

        if hist.get("insights"):
            print(f"\n  {_c('AZUL', 'Insights:')}")
            for k, v in hist["insights"].items():
                print(f"    • {k}: {v}")

        _enter()
        return 0

    def exibir_metricas(self) -> int:
        """Exibir métricas de qualidade."""
        _sub("Métricas de Qualidade")
        log_path = self.log_path
        if not log_path or not os.path.exists(log_path):
            _warn("Log não encontrado. Compile primeiro.")
            _enter()
            return 1

        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            log = f.read()

        # Overfulls
        overfulls = re.findall(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", log)
        over_vals = [float(o) for o in overfulls]
        limite_over = 8
        print(f"  Overfull boxes:     {_c('VERDE' if len(over_vals) <= limite_over else 'VERMELHO', str(len(over_vals)))} "
              f"(limite: {limite_over})")
        if over_vals:
            print(f"    Máximo:           {max(over_vals):.1f}pt  (limite: 12.0pt)")
            print(f"    Média:            {sum(over_vals)/len(over_vals):.1f}pt")
            for i, v in enumerate(over_vals, 1):
                cor = "VERDE" if v < 3 else ("AMARELO" if v < 12 else "VERMELHO")
                print(f"    {i}. {_c(cor, f'{v:.1f}pt')}")

        # Underfulls
        underfulls = re.findall(r"Underfull \\hbox \(badness (\d+)\)", log)
        under_vals = [int(u) for u in underfulls]
        print(f"\n  Underfull boxes:    {_c('VERDE' if len(under_vals) == 0 else 'AMARELO', str(len(under_vals)))}")
        if under_vals:
            print(f"    Máximo badness:   {max(under_vals)}  (limite: 10000)")

        # Páginas
        paginas = re.search(r"Output written on .*?\((\d+) pages?", log)
        if paginas:
            print(f"\n  Páginas:            {paginas.group(1)}")

        # Erros
        erros = re.findall(r"^! ", log, re.MULTILINE)
        print(f"\n  Erros LaTeX:        {_c('VERDE' if len(erros) == 0 else 'VERMELHO', str(len(erros)))}")

        # Font warnings
        fonts = re.findall(r"LaTeX Font Warning:", log)
        print(f"  Font warnings:      {_c('VERDE' if len(fonts) == 0 else 'AMARELO', str(len(fonts)))}")

        # TDD status
        print(f"\n  {_c('AZUL', 'Último TDD:')}")
        reports_dir = self.reports_dir
        if os.path.exists(reports_dir):
            reports = sorted(Path(reports_dir).glob("*.json"), reverse=True)
            if reports:
                ultimo = _ler_json(str(reports[0]))
                if ultimo:
                    status = "PASS" if ultimo.get("all_passed") else "FAIL"
                    cor = "VERDE" if status == "PASS" else "VERMELHO"
                    print(f"    Status:           {_c(cor, status)}")
                    print(f"    Timestamp:        {ultimo.get('timestamp', '?')}")
                    for suite, res in ultimo.get("suites", {}).items():
                        s = "PASS" if res.get("passed") else "FAIL"
                        sc = "VERDE" if s == "PASS" else "VERMELHO"
                        print(f"      {suite}: {_c(sc, s)}")

        _enter()
        return 0

    def verificar_dependencias(self) -> int:
        """Verificar dependências do sistema."""
        _sub("Verificação de Dependências")

        # pdflatex
        try:
            r = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                versao = r.stdout.split("\n")[0][:80] if r.stdout else "OK"
                _ok(f"pdflatex: {versao}")
            else:
                _fail("pdflatex: erro na execução")
        except FileNotFoundError:
            _fail("pdflatex: NÃO ENCONTRADO (TeX Live?)")
        except Exception as e:
            _fail(f"pdflatex: {e}")

        # Python
        _ok(f"Python: {sys.version.split()[0]} ({sys.executable})")

        # Módulos Python essenciais
        for modulo in ["json", "re", "subprocess", "shutil", "pathlib"]:
            try:
                __import__(modulo)
                _ok(f"Módulo: {modulo}")
            except ImportError:
                _fail(f"Módulo: {modulo} — AUSENTE")

        # Pacotes LaTeX ausentes (via .log)
        log_path = self.log_path
        if log_path and os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                log = f.read()
            faltando = re.findall(r"! LaTeX Error: File `([^']+)' not found", log)
            if faltando:
                for pkg in set(faltando):
                    _fail(f"Pacote LaTeX ausente: {pkg}")
            else:
                _ok("Pacotes LaTeX: OK")

        # Permissão de escrita
        try:
            test_file = os.path.join(self.base, ".write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            _ok("Permissão de escrita: OK")
        except OSError:
            _fail("Permissão de escrita: NEGADA")

        _enter()
        return 0

    # ── APRENDER ────────────────────────────────────────────

    def exibir_insights(self) -> int:
        """Exibir insights de evolução disponíveis."""
        _sub("Insights de Evolução")
        if not self.cat.insights:
            _info("Nenhum insight disponível.")
            _info("Execute o pipeline AutoEvolve para gerar insights.")
            _enter()
            return 1
        for i, ins in enumerate(self.cat.insights, 1):
            print(f"    {i}. {ins.nome}  ({ins.data})")
        try:
            esc = input(f"\n  {_c('CIANO', 'Nº do insight para ler (0=cancelar)')} {_c('CIANO', '>')} ").strip()
            n = int(esc)
            if n == 0:
                return 0
            if 1 <= n <= len(self.cat.insights):
                caminho = self.cat.insights[n - 1].path
                print(f"\n  {_c('CINZA', '─' * 60)}")
                with open(caminho, "r", encoding="utf-8") as f:
                    print(f.read())
                print(f"  {_c('CINZA', '─' * 60)}")
            else:
                _warn("Nº inválido.")
        except (ValueError, IndexError):
            _warn("Entrada inválida.")
        _enter()
        return 0

    def documentacao(self) -> int:
        """Exibir caminhos da documentação."""
        _sub("Documentação do Framework")
        docs = [
            ("Framework conceitual", os.path.join(self.orch_dir, "FRAMEWORK.md")),
            ("Spec do pipeline", os.path.join(self.orch_dir, "SPEC_ORCHESTRATION.md")),
            ("README dos testes", os.path.join(self.tests_dir, "README.md")),
        ]
        if self.cat.insights:
            docs.append(("Índice de evoluções", os.path.join(
                self.orch_dir, "evolutions", "INDEX.md")))
        for nome, caminho in docs:
            if os.path.exists(caminho):
                _ok(f"{nome}: {os.path.relpath(caminho, self.base)}")
            else:
                _warn(f"{nome}: não encontrado")
        print(f"\n  {_c('CINZA', 'Para abrir: type <caminho> (Windows) ou cat <caminho> (Linux/Mac)')}")
        _enter()
        return 0


# ============================================================
# CONSTRUTOR DE MENU
# ============================================================

class MenuActionBuilder:
    """Constrói a lista de ações do menu a partir do catálogo."""

    def __init__(self, catalog: MenuCatalog, base_dir: str):
        self.cat = catalog
        self.base = base_dir
        self.ops = BuiltinOperations(catalog, base_dir)

    def construir(self) -> List[MenuAction]:
        """Monta todas as ações do menu (builtins + descobertas + registradas)."""
        acoes: List[MenuAction] = []

        # ── BUILTINS (sempre presentes) ────────────────────

        # OPERACIONAR
        acoes.append(MenuAction(
            id="compilar", nome="Compilar documento LaTeX",
            descricao="2 passes pdflatex",
            categoria=Categoria.OPERACIONAR, origem="builtin",
            executar=self.ops.compilar_escolher,
        ))
        acoes.append(MenuAction(
            id="testar", nome="Executar testes TDD",
            descricao=f"{len(self.cat.test_suites)} suíte(s) encontrada(s)",
            categoria=Categoria.OPERACIONAR, origem="builtin",
            executar=lambda: self.ops.testar(),
        ))
        # Pipeline: um por script encontrado + atalho unificado
        if self.cat.pipelines:
            acoes.append(MenuAction(
                id="pipeline", nome="Executar pipeline AutoEvolve",
                descricao=f"{len(self.cat.pipelines)} script(s) disponível(is)",
                categoria=Categoria.OPERACIONAR, origem="builtin",
                executar=lambda: self.ops.pipeline(),
            ))

        # REPRODUZIR
        acoes.append(MenuAction(
            id="restaurar", nome="Restaurar backup anterior",
            descricao=f"{len(self.cat.backups)} backup(s) disponível(is)",
            categoria=Categoria.REPRODUZIR, origem="builtin",
            executar=self.ops.restaurar,
        ))
        acoes.append(MenuAction(
            id="refinar", nome="Refinamento manual guiado",
            descricao="Diagnóstico + backup + instruções",
            categoria=Categoria.REPRODUZIR, origem="builtin",
            executar=self.ops.refinamento_guiado,
        ))

        # REGISTRAR
        acoes.append(MenuAction(
            id="registrar", nome="Registrar correção manual",
            descricao="Adicionar entrada no histórico",
            categoria=Categoria.REGISTRAR, origem="builtin",
            executar=self.ops.registrar_correcao,
        ))
        acoes.append(MenuAction(
            id="relatorio", nome="Gerar relatório de estado",
            descricao="Métricas do documento e testes",
            categoria=Categoria.REGISTRAR, origem="builtin",
            executar=self.ops.gerar_relatorio,
        ))

        # AUDITAR
        acoes.append(MenuAction(
            id="auditar", nome="Auditar integridade do framework",
            descricao="Verificar arquivos, dados, estrutura",
            categoria=Categoria.AUDITAR, origem="builtin",
            executar=self.ops.auditar_integridade,
        ))
        acoes.append(MenuAction(
            id="historico", nome="Exibir histórico de execuções",
            descricao="Sessões automáticas e manuais",
            categoria=Categoria.AUDITAR, origem="builtin",
            executar=self.ops.exibir_historico,
        ))
        acoes.append(MenuAction(
            id="metricas", nome="Exibir métricas de qualidade",
            descricao="Overfulls, underfulls, erros, TDD",
            categoria=Categoria.AUDITAR, origem="builtin",
            executar=self.ops.exibir_metricas,
        ))
        acoes.append(MenuAction(
            id="dependencias", nome="Verificar dependências",
            descricao="pdflatex, Python, pacotes",
            categoria=Categoria.AUDITAR, origem="builtin",
            executar=self.ops.verificar_dependencias,
        ))

        # APRENDER
        if self.cat.insights:
            acoes.append(MenuAction(
                id="insights", nome="Explorar insights de evolução",
                descricao=f"{len(self.cat.insights)} arquivo(s)",
                categoria=Categoria.APRENDER, origem="builtin",
                executar=self.ops.exibir_insights,
            ))
        acoes.append(MenuAction(
            id="docs", nome="Documentação do framework",
            descricao="FRAMEWORK.md, SPEC, README",
            categoria=Categoria.APRENDER, origem="builtin",
            executar=self.ops.documentacao,
        ))

        # ── DESCOBERTAS: pipelines individuais ─────────────

        # Scripts de pipeline como opções separadas (apenas se >1)
        if len(self.cat.pipelines) > 1:
            for p in self.cat.pipelines:
                # Pular se já existe atalho builtin
                if "refinement" in p.nome.lower() or "loop" in p.nome.lower():
                    continue
                desc = p.descricao[:60] if p.descricao else ""
                acoes.append(MenuAction(
                    id=f"pipeline:{p.nome}", nome=f"Pipeline: {p.nome}",
                    descricao=desc,
                    categoria=Categoria.OPERACIONAR, origem="discovered",
                    executar=lambda p=p: self.ops.pipeline(p),
                    item_ref=p,
                ))

        # ── DESCOBERTAS: backups individuais (atalhos) ─────

        # Atalhos para backups recentes (máx 3)
        backups_recentes = self.cat.backups[:3]
        for b in backups_recentes:
            acoes.append(MenuAction(
                id=f"backup:{b.nome}", nome=f"Restaurar: {b.nome}",
                descricao=f"{b.data_hora}, {b.tamanho_kb:.0f} KB",
                categoria=Categoria.REPRODUZIR, origem="discovered",
                executar=lambda b=b: self._restaurar_direto(b),
                item_ref=b,
            ))

        # ── REGISTRADAS: .menu_registry.json ────────────────

        for cmd in self.cat.registered:
            try:
                cat = Categoria(cmd.categoria.upper())
            except (ValueError, AttributeError):
                cat = Categoria.FERRAMENTAS
            acoes.append(MenuAction(
                id=f"registered:{cmd.id}", nome=cmd.nome,
                descricao=cmd.descricao,
                categoria=cat, origem="registered",
                executar=lambda cmd=cmd: self._executar_registrado(cmd),
                item_ref=cmd,
            ))

        return acoes

    def _restaurar_direto(self, backup: BackupItem) -> int:
        """Restaura backup específico."""
        if not self.ops.tex_primario:
            _fail("Nenhum documento .tex alvo!")
            _enter()
            return 1
        try:
            shutil.copy2(backup.path, self.ops.tex_primario.path)
            _ok(f"Restaurado: {backup.nome} → {self.ops.tex_primario.nome}")
        except OSError as e:
            _fail(f"Erro ao restaurar: {e}")
        _enter()
        return 0

    def _executar_registrado(self, cmd: RegisteredCommand) -> int:
        """Executa comando registrado."""
        _sub(f"Comando: {cmd.nome}")
        if cmd.descricao:
            _info(cmd.descricao)
        print(f"    {_c('CINZA', ' '.join(cmd.comando))}")
        print()
        code, stdout, stderr = RunnerEngine.comando(
            cmd.comando, cwd=os.path.join(self.base, cmd.cwd),
            timeout=cmd.timeout
        )
        if stdout:
            for linha in stdout.strip().split("\n")[-8:]:
                if linha.strip():
                    print(f"    {linha[:120]}")
        if code == 0:
            _ok("Comando executado com sucesso")
        else:
            _fail(f"Comando falhou (exit={code})")
            if stderr:
                for linha in stderr.strip().split("\n")[-3:]:
                    if linha.strip():
                        _info(linha[:120])
        _enter()
        return code


# ============================================================
# RENDERIZADOR DO MENU
# ============================================================

class MenuRenderer:
    """Renderiza o menu adaptativo e processa a entrada."""

    COR_SECAO = {
        Categoria.OPERACIONAR: "VERDE",
        Categoria.REPRODUZIR:  "AMARELO",
        Categoria.REGISTRAR:   "AZUL",
        Categoria.AUDITAR:     "MAGENTA",
        Categoria.APRENDER:    "LARANJA",
        Categoria.FERRAMENTAS: "CIANO",
    }

    def __init__(self, acoes: List[MenuAction], base_dir: str):
        self.acoes = acoes
        self.base = base_dir
        self.secoes: Dict[Categoria, List[Tuple[int, MenuAction]]] = {}
        self._organizar()

    def _organizar(self):
        """Organiza ações em seções por categoria com numeração sequencial."""
        self.secoes.clear()
        ordem_cat = [
            Categoria.OPERACIONAR,
            Categoria.REPRODUZIR,
            Categoria.REGISTRAR,
            Categoria.AUDITAR,
            Categoria.APRENDER,
            Categoria.FERRAMENTAS,
        ]
        idx = 1
        for cat in ordem_cat:
            itens = [a for a in self.acoes if a.categoria == cat]
            if itens:
                self.secoes[cat] = []
                for acao in itens:
                    self.secoes[cat].append((idx, acao))
                    idx += 1

    def renderizar(self):
        """Exibe o menu completo no terminal."""
        _limpar()
        print()
        print(_c("CIANO", "╔" + "═" * 68 + "╗"))
        print(_c("CIANO", "║") + _c("BOLD", "  SDD+TDD+AutoEvolve  —  Painel de Controle Adaptativo").ljust(69)
              + _c("CIANO", "║"))
        # Mostrar documento ativo
        info_rodape = datetime.now().strftime("%d/%m/%Y %H:%M")
        print(_c("CIANO", "║") + _c("CINZA", f"  {os.path.basename(self.base)}  |  {info_rodape}").ljust(69)
              + _c("CIANO", "║"))
        print(_c("CIANO", "╚" + "═" * 68 + "╝"))
        print()

        # Renderizar cada seção
        for cat, itens in self.secoes.items():
            cor = self.COR_SECAO[cat]
            icone = cat.icone
            nome_secao = cat.value
            print(f"  {_c(cor, f'┌─ {icone} {nome_secao} ' + '─' * (52 - len(nome_secao)) + '┐')}")
            for num, acao in itens:
                # Indicador visual de origem
                origem_tag = ""
                if acao.origem == "discovered":
                    origem_tag = _c("CINZA", " ⟐")
                elif acao.origem == "registered":
                    origem_tag = _c("CIANO", " ◈")

                nome_display = acao.nome
                desc_display = acao.descricao
                # Truncar para caber
                max_nome = 50
                if len(nome_display) > max_nome:
                    nome_display = nome_display[:max_nome - 3] + "..."

                linha = f"  {_c(cor, '│')}  {_c('BOLD', str(num)):>4}{origem_tag}  {nome_display}"
                # Preencher até o fim
                linha = linha.ljust(66) + _c(cor, "│")
                print(linha)
            print(f"  {_c(cor, '└' + '─' * 62 + '┘')}")
            print()

        # Rodapé
        print(f"  {_c('CINZA', '─' * 64)}")
        print(f"   {_c('CINZA', '0')}  Sair")
        print(f"   {_c('CINZA', 'q')}  Diagnóstico rápido (--quick)")
        print(f"   {_c('CINZA', 'l')}  Listar itens descobertos")
        print()

    def obter_acao_por_numero(self, numero: int) -> Optional[MenuAction]:
        """Retorna a ação correspondente ao número."""
        for cat, itens in self.secoes.items():
            for num, acao in itens:
                if num == numero:
                    return acao
        return None

    def listar_descobertos(self):
        """Exibe todos os itens descobertos."""
        _sub("Itens Descobertos pelo Scanner")
        from collections import Counter
        tipos = Counter()
        for cat, itens in self.secoes.items():
            for num, acao in itens:
                tipos[acao.origem] += 1

        print(f"  {_c('AZUL', 'Estatísticas:')}")
        for origem, count in tipos.most_common():
            print(f"    • {origem}: {count}")
        print(f"\n  {_c('AZUL', 'Origem dos itens:')}")
        print(f"    {_c('VERDE', 'builtin')}     = operações nativas do framework (sempre presentes)")
        print(f"    {_c('AMARELO', 'discovered')} = descobertas por varredura do diretório")
        print(f"    {_c('CIANO', 'registered')}  = registradas via .menu_registry.json")
        print(f"\n  {_c('AZUL', 'Documentos .tex encontrados:')}")
        # Acessar catálogo via primeiras ações builtin
        print(f"  {_c('CINZA', 'Para registrar novos comandos, crie .menu_registry.json no diretório raiz.')}")
        print(f"  {_c('CINZA', 'Exemplo de .menu_registry.json:')}")
        print(r'''    {
      "commands": [
        {
          "id": "meu-script",
          "name": "Meu Script Personalizado",
          "description": "Faz algo útil",
          "category": "FERRAMENTAS",
          "command": ["python", "scripts/meu_script.py"],
          "cwd": ".",
          "timeout": 120
        }
      ]
    }''')
        _enter()

    def executar_por_numero(self, numero: int) -> int:
        """Executa a ação correspondente ao número."""
        acao = self.obter_acao_por_numero(numero)
        if not acao:
            _warn(f"Opção {numero} não encontrada.")
            _enter()
            return 1
        try:
            return acao.executar()
        except Exception as e:
            _fail(f"Erro ao executar '{acao.nome}': {e}")
            import traceback
            traceback.print_exc()
            _enter()
            return 1


# ============================================================
# MODO DIAGNÓSTICO RÁPIDO
# ============================================================

def diagnostico_rapido(catalog: MenuCatalog, base_dir: str) -> int:
    """Modo --quick: diagnóstico não-interativo."""
    _cabecalho("Diagnóstico Rápido — SDD+TDD+AutoEvolve")

    tex_primario = catalog.primeiro_tex
    log_path = os.path.join(base_dir, f"{tex_primario.base}.log") if tex_primario else None
    reports_dir = os.path.join(base_dir, "tests", "reports")
    fix_history_path = os.path.join(base_dir, "orchestration", "fix_history.json")

    if not catalog.tex_files:
        _fail("Nenhum documento .tex encontrado!")
        return 1

    # 1. Documentos
    for tex in catalog.tex_files:
        status = _c("VERDE", "✓") if tex.tem_pdf else _c("CINZA", "─")
        _ok(f"Documento: {status} {tex.nome} ({tex.tamanho_kb:.0f} KB)")

    # 2. PDF
    tex = tex_primario
    if tex and tex.tem_pdf:
        pdf_path = os.path.join(base_dir, f"{tex.base}.pdf")
        if os.path.exists(pdf_path):
            _ok(f"PDF: {os.path.getsize(pdf_path) / 1024:.0f} KB")
    else:
        _warn("PDF: não encontrado (compile primeiro)")

    # 3. Overfull/underfull
    if log_path and os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            log = f.read()
        over = len(re.findall(r"Overfull \\hbox", log))
        under = len(re.findall(r"Underfull \\hbox.*badness (?:10000|9\d{4})", log))
        erros = len(re.findall(r"^! ", log, re.MULTILINE))
        paginas = "?"
        m = re.search(r"Output written on .*?\((\d+) pages?", log)
        if m:
            paginas = m.group(1)
        print(f"  Qualidade: {over} overfulls, {under} underfulls, {erros} erros, {paginas}p")

    # 4. Último TDD
    if os.path.exists(reports_dir):
        reports = sorted(Path(reports_dir).glob("report_*.json"), reverse=True)
        if reports:
            ultimo = _ler_json(str(reports[0]))
            if ultimo:
                st = "PASS" if ultimo.get("all_passed") else "FAIL"
                ts = ultimo.get("timestamp", "?")
                print(f"  Último TDD: {st} ({ts})")

    # 5. Histórico
    hist = _ler_json(fix_history_path)
    if hist:
        sessoes = len(hist.get("sessions", []))
        manuais = len(hist.get("manual_fixes", []))
        print(f"  Histórico: {sessoes} sessões, {manuais} correções manuais")

    # 6. Componentes
    print(f"  Componentes: {len(catalog.test_suites)} testes, "
          f"{len(catalog.pipelines)} pipelines, "
          f"{len(catalog.backups)} backups, "
          f"{len(catalog.insights)} insights")

    print()
    return 0


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Ponto de entrada principal."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # ── HELP ────────────────────────────────────────────────
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return 0

    # ── SCAN: descobrir tudo ───────────────────────────────
    engine = DiscoveryEngine(base_dir)
    catalog = engine.scan()

    # ── LIST ────────────────────────────────────────────────
    if "--list" in sys.argv:
        _cabecalho("Itens Descobertos")
        print(f"  {_c('AZUL', '.tex:')}       {len(catalog.tex_files)}")
        for t in catalog.tex_files:
            print(f"    • {t.nome} ({t.tamanho_kb:.0f} KB, {t.paginas}p)")
        print(f"  {_c('AZUL', 'Testes:')}     {len(catalog.test_suites)}")
        for s in catalog.test_suites:
            print(f"    • {s.nome}  {_c('CINZA', s.descricao[:60])}")
        print(f"  {_c('AZUL', 'Pipelines:')}  {len(catalog.pipelines)}")
        for p in catalog.pipelines:
            print(f"    • {p.nome}  {_c('CINZA', p.descricao[:60])}")
        print(f"  {_c('AZUL', 'Backups:')}    {len(catalog.backups)}")
        for b in catalog.backups:
            print(f"    • {b.nome} ({b.data_hora})")
        print(f"  {_c('AZUL', 'Insights:')}   {len(catalog.insights)}")
        for i in catalog.insights:
            print(f"    • {i.nome}")
        print(f"  {_c('AZUL', 'Registrados:')} {len(catalog.registered)}")
        for r in catalog.registered:
            print(f"    • {r.nome}  {_c('CINZA', r.descricao[:60])}")
        return 0

    # ── QUICK ───────────────────────────────────────────────
    if "--quick" in sys.argv or "-q" in sys.argv:
        return diagnostico_rapido(catalog, base_dir)

    # ── EXECUÇÃO DIRETA (menu.py <número>) ─────────────────
    args_sem_flags = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args_sem_flags:
        try:
            num = int(args_sem_flags[0])
            builder = MenuActionBuilder(catalog, base_dir)
            acoes = builder.construir()
            renderer = MenuRenderer(acoes, base_dir)
            return renderer.executar_por_numero(num)
        except ValueError:
            pass

    # ── MENU INTERATIVO ─────────────────────────────────────
    builder = MenuActionBuilder(catalog, base_dir)
    acoes = builder.construir()
    renderer = MenuRenderer(acoes, base_dir)

    while True:
        renderer.renderizar()
        try:
            esc = input(f"  {_c('CIANO', 'Opção')} {_c('CINZA', '(0=sair)')} {_c('CIANO', '>')} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if esc == "0" or esc == "":
            print(f"\n  {_c('CINZA', 'Até logo!')}")
            break

        if esc == "q":
            diagnostico_rapido(catalog, base_dir)
            _enter()
            continue

        if esc == "l":
            renderer.listar_descobertos()
            continue

        try:
            num = int(esc)
            renderer.executar_por_numero(num)
        except ValueError:
            _warn(f"Opção inválida: '{esc}'. Digite um número, 0, q ou l.")
            _enter()

    return 0


if __name__ == "__main__":
    sys.exit(main())
