"""
Code Search & Dependency Indexing Tools for AutonomousAI.
Provides keyword search, symbol lookup, import graph extraction, and file relevance ranking.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import re
import ast
from tools.base import BaseTool


class RipgrepSearchTool(BaseTool):
    """Tool to search keywords/regex patterns across codebase."""

    def __init__(self):
        super().__init__(
            name="search_code",
            description="Searches code files for literal text or regex patterns.",
        )

    def execute(
        self,
        query: str,
        path: str,
        extensions: Optional[List[str]] = None,
        max_results: int = 50,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return {"success": False, "error": f"Path not found: {path}"}

        exts = set(extensions) if extensions else {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".html", ".css", ".java"}
        ignore_dirs = {".git", "node_modules", ".venv", "__pycache__", ".cache", "dist", "build"}

        matches: List[Dict[str, Any]] = []
        try:
            pattern = re.compile(query, re.IGNORECASE)
        except Exception:
            pattern = re.compile(re.escape(query), re.IGNORECASE)

        for file_path in p.rglob("*"):
            if any(part in ignore_dirs for part in file_path.parts):
                continue
            if not file_path.is_file() or file_path.suffix.lower() not in exts:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                for line_no, line in enumerate(content.splitlines(), start=1):
                    if pattern.search(line):
                        matches.append({
                            "file": str(file_path.relative_to(p)),
                            "line_number": line_no,
                            "content": line.strip(),
                        })
                        if len(matches) >= max_results:
                            break
                if len(matches) >= max_results:
                    break
            except Exception:
                continue

        return {"success": True, "query": query, "total_matches": len(matches), "matches": matches}


class DependencyGraphTool(BaseTool):
    """Tool to extract file import graphs for Python and JS/TS."""

    def __init__(self):
        super().__init__(
            name="build_import_graph",
            description="Builds an import dependency graph between project source files.",
        )

    def execute(self, project_path: str, **kwargs: Any) -> Dict[str, Any]:
        root = Path(project_path)
        if not root.exists():
            return {"success": False, "error": f"Path not found: {project_path}"}

        graph: Dict[str, List[str]] = {}
        ignore_dirs = {".git", "node_modules", ".venv", "__pycache__", ".cache", "dist", "build"}

        for file_path in root.rglob("*"):
            if any(part in ignore_dirs for part in file_path.parts):
                continue
            if not file_path.is_file():
                continue

            rel_file = str(file_path.relative_to(root)).replace("\\", "/")
            ext = file_path.suffix.lower()

            imports: Set[str] = set()

            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                if ext == ".py":
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.add(alias.name)
                            elif isinstance(node, ast.ImportFrom) and node.module:
                                imports.add(node.module)
                    except Exception:
                        pass
                elif ext in {".js", ".jsx", ".ts", ".tsx"}:
                    # Regex for JS/TS imports
                    for match in re.finditer(r"(?:import|from|require\()\s*['\"]([^'\"]+)['\"]", content):
                        imports.add(match.group(1))

                graph[rel_file] = sorted(list(imports))
            except Exception:
                continue

        return {"success": True, "graph": graph, "total_files_indexed": len(graph)}
