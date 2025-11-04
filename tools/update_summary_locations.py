#!/usr/bin/env python3
"""Regenerate the exact location appendix within logs/summary.md."""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_FILE = REPO_ROOT / "logs" / "summary.md"

TARGET_SYMBOLS = {
    "src/nf_auto_runner/config/model_selection.py": {
        "classes": {
            "ModelSelectionConfig": [
                "get_enabled_models",
                "is_model_enabled",
                "get_disabled_models",
            ]
        }
    },
    "src/nf_auto_runner/config/loader.py": {
        "classes": {
            "ConfigLoader": [],
        }
    },
}


@dataclass(frozen=True)
class SymbolInfo:
    """Represent a discovered symbol and its line span."""

    name: str
    start_line: int
    end_line: int
    kind: str
    parent: str | None = None

    @property
    def display_name(self) -> str:
        if self.kind == "method" and self.parent:
            return f"{self.parent}.{self.name}"
        return self.name


class SymbolCollector(ast.NodeVisitor):
    """Collect classes, functions, and methods from a module AST."""

    def __init__(self, *, lines: list[str]) -> None:
        self._lines = lines
        self.symbols: list[SymbolInfo] = []
        self._class_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.symbols.append(
            SymbolInfo(
                name=node.name,
                start_line=node.lineno,
                end_line=_node_end_lineno(node),
                kind="class",
            )
        )
        self._class_stack.append(node.name)
        for child in node.body:
            # Only inspect direct definitions; avoid ast.walk to keep order predictable.
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.visit(child)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._handle_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._handle_function(node)

    def _handle_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        parent = self._class_stack[-1] if self._class_stack else None
        kind = "method" if parent else "function"
        self.symbols.append(
            SymbolInfo(
                name=node.name,
                start_line=node.lineno,
                end_line=_node_end_lineno(node),
                kind=kind,
                parent=parent,
            )
        )


def _node_end_lineno(node: ast.AST) -> int:
    end_lineno = getattr(node, "end_lineno", None)
    if end_lineno is None:
        raise ValueError(f"Python AST node missing end_lineno for {type(node).__name__}")
    return end_lineno


def _read_symbols(file_path: Path) -> dict[str, SymbolInfo]:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    collector = SymbolCollector(lines=source.splitlines())
    collector.visit(tree)
    return {symbol.display_name: symbol for symbol in collector.symbols}


def _normalise_remote_url(raw: str) -> str | None:
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith("git@github.com:"):
        prefix_len = len("git@github.com:")
        repo_part = raw[prefix_len:]
        if repo_part.endswith(".git"):
            repo_part = repo_part[:-4]
        return f"https://github.com/{repo_part}"
    if raw.startswith("https://") or raw.startswith("http://"):
        url = raw
        if url.endswith(".git"):
            url = url[:-4]
        return url
    return None


def _detect_remote_base() -> tuple[str, str] | None:
    try:
        remote_proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return None

    base_url = _normalise_remote_url(remote_proc.stdout)
    if base_url is None:
        return None

    branch = _detect_default_branch()
    return base_url, branch


def _detect_default_branch() -> str:
    primary = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if primary.returncode == 0:
        ref = primary.stdout.strip()
        if ref.startswith("origin/"):
            return ref.split("/", 1)[1]
        return ref

    remote_show = subprocess.run(
        ["git", "remote", "show", "origin"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if remote_show.returncode == 0:
        for line in remote_show.stdout.splitlines():
            if "HEAD branch:" in line:
                return line.split(":", 1)[1].strip()

    return "main"


def _build_link(base_url: str, branch: str, relative_path: Path, symbol: SymbolInfo) -> str:
    anchor = f"#L{symbol.start_line}"
    if symbol.end_line != symbol.start_line:
        anchor = f"{anchor}-L{symbol.end_line}"
    return f"{base_url}/blob/{branch}/{relative_path.as_posix()}{anchor}"


def _format_span(symbol: SymbolInfo) -> str:
    if symbol.start_line == symbol.end_line:
        return f"L{symbol.start_line}"
    return f"L{symbol.start_line}-L{symbol.end_line}"


def _render_appendix(remote_ctx: tuple[str, str] | None) -> list[str]:
    lines: list[str] = ["### Appendix: exact locations", ""]
    for relative_path_str, config in TARGET_SYMBOLS.items():
        relative_path = Path(relative_path_str)
        file_path = REPO_ROOT / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Target file not found: {relative_path}")

        symbols_by_name = _read_symbols(file_path)
        total_lines = len(file_path.read_text(encoding="utf-8").splitlines())
        lines.append(f"- `{relative_path.as_posix()}` (total {total_lines} lines)")

        for class_name, methods in config.get("classes", {}).items():
            symbol = symbols_by_name.get(class_name)
            if symbol is None:
                lines.append(f"  - {class_name}: not found")
            else:
                link = (
                    _build_link(remote_ctx[0], remote_ctx[1], relative_path, symbol)
                    if remote_ctx
                    else None
                )
                class_line = f"  - {symbol.display_name}: {_format_span(symbol)}"
                if link:
                    class_line += f" ([link]({link}))"
                lines.append(class_line)

            for method_name in methods:
                key = f"{class_name}.{method_name}"
                symbol = symbols_by_name.get(key)
                if symbol is None:
                    lines.append(f"  - {class_name}.{method_name}: not found")
                    continue
                link = (
                    _build_link(remote_ctx[0], remote_ctx[1], relative_path, symbol)
                    if remote_ctx
                    else None
                )
                method_line = f"  - {symbol.display_name}: {_format_span(symbol)}"
                if link:
                    method_line += f" ([link]({link}))"
                lines.append(method_line)

        lines.append("")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"_generated at {timestamp}_")
    return lines


def _replace_appendix(existing_lines: list[str], new_section: list[str]) -> list[str]:
    try:
        header_index = existing_lines.index("### Appendix: exact locations")
    except ValueError as exc:
        raise ValueError("Appendix header not found in summary.md") from exc

    end_index = None
    for idx in range(header_index + 1, len(existing_lines)):
        if existing_lines[idx].startswith("_generated at "):
            end_index = idx + 1
            break
    if end_index is None:
        end_index = len(existing_lines)

    return existing_lines[:header_index] + new_section + existing_lines[end_index:]


def main() -> None:
    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(f"Summary file not found: {SUMMARY_FILE}")

    remote_ctx = _detect_remote_base()
    appendix_lines = _render_appendix(remote_ctx)

    existing_content = SUMMARY_FILE.read_text(encoding="utf-8").splitlines()
    updated_lines = _replace_appendix(existing_content, appendix_lines)
    SUMMARY_FILE.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
