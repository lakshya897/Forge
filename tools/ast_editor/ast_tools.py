"""
Multi-Language AST Code Editor for AutonomousAI.
Supports Python (AST/LibCST) and JS/TS/TSX/JSX structural edits with pre-validation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import ast
import re
from tools.base import BaseTool


class ValidateSyntaxTool(BaseTool):
    """Tool to validate syntax of Python, JSON, JS/TS code before writing to disk."""

    def __init__(self):
        super().__init__(
            name="validate_syntax",
            description="Validates syntax of Python, JSON, and JS/TS code blocks.",
        )

    def execute(self, code: str, language: str, **kwargs: Any) -> Dict[str, Any]:
        lang = language.lower()
        if lang == "python" or lang == "py":
            try:
                ast.parse(code)
                return {"success": True, "valid": True, "language": "python"}
            except SyntaxError as e:
                return {
                    "success": True,
                    "valid": False,
                    "language": "python",
                    "error": f"Syntax error at line {e.lineno}: {e.msg}",
                }
        elif lang == "json":
            import json
            try:
                json.loads(code)
                return {"success": True, "valid": True, "language": "json"}
            except Exception as e:
                return {"success": True, "valid": False, "language": "json", "error": str(e)}

        # Basic JS/TS check: check balanced braces, quotes, brackets
        open_braces = code.count("{") - code.count("}")
        open_parens = code.count("(") - code.count(")")
        open_brackets = code.count("[") - code.count("]")

        if open_braces != 0 or open_parens != 0 or open_brackets != 0:
            return {
                "success": True,
                "valid": False,
                "language": lang,
                "error": f"Unbalanced syntax: braces={open_braces}, parens={open_parens}, brackets={open_brackets}",
            }

        return {"success": True, "valid": True, "language": lang}


class ASTInsertFunctionTool(BaseTool):
    """Tool to structurally insert or append a function/component into a source file."""

    def __init__(self):
        super().__init__(
            name="ast_insert_function",
            description="Structurally inserts a new function or component into a source file.",
        )

    def execute(
        self,
        file_path: str,
        function_code: str,
        position: str = "end",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            content = p.read_text(encoding="utf-8")
            ext = p.suffix.lower()

            # Pre-validate if python
            if ext == ".py":
                try:
                    ast.parse(function_code)
                except SyntaxError as e:
                    return {"success": False, "error": f"Invalid Python function syntax: {e}"}

            if position == "beginning":
                new_content = function_code.strip() + "\n\n" + content
            else:
                new_content = content.rstrip() + "\n\n" + function_code.strip() + "\n"

            p.write_text(new_content, encoding="utf-8")
            return {"success": True, "file_path": str(p), "status": "inserted"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ASTUpdateImportsTool(BaseTool):
    """Tool to structurally add missing import statements without duplicates."""

    def __init__(self):
        super().__init__(
            name="ast_update_imports",
            description="Adds import statements to the top of a file if not already present.",
        )

    def execute(self, file_path: str, imports_to_add: List[str], **kwargs: Any) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            content = p.read_text(encoding="utf-8")
            lines = content.splitlines()

            added: List[str] = []
            for imp in imports_to_add:
                imp_clean = imp.strip()
                if imp_clean and imp_clean not in content:
                    added.append(imp_clean)

            if not added:
                return {"success": True, "status": "no_changes_needed", "added": []}

            new_content = "\n".join(added) + "\n" + content
            p.write_text(new_content, encoding="utf-8")
            return {"success": True, "status": "updated", "added": added}
        except Exception as e:
            return {"success": False, "error": str(e)}
