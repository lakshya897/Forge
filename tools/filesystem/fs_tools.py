"""
Filesystem Tools for AutonomousAI.
Provides safe, deterministic file I/O operations with UTF-8 encoding.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from tools.base import BaseTool


class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="Absolute or relative file path to read")
    start_line: Optional[int] = Field(default=None, description="Optional 1-indexed start line")
    end_line: Optional[int] = Field(default=None, description="Optional 1-indexed end line")


class ReadFileTool(BaseTool):
    """Tool to safely read text files."""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="Reads file contents with optional line slice bounds.",
            args_schema=ReadFileInput,
        )

    def execute(self, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines(keepends=True)
            total_lines = len(lines)

            if start_line is not None or end_line is not None:
                start = max(1, start_line or 1) - 1
                end = min(total_lines, end_line or total_lines)
                sliced = "".join(lines[start:end])
                return {
                    "success": True,
                    "content": sliced,
                    "total_lines": total_lines,
                    "lines_returned": f"{start + 1}-{end}",
                }

            return {"success": True, "content": content, "total_lines": total_lines}
        except Exception as e:
            return {"success": False, "error": str(e)}


class WriteFileInput(BaseModel):
    file_path: str = Field(..., description="Target file path to write")
    content: str = Field(..., description="Full text content to write")
    overwrite: bool = Field(default=True, description="Whether to overwrite existing file")


class WriteFileTool(BaseTool):
    """Tool to create or overwrite text files."""

    def __init__(self):
        super().__init__(
            name="write_file",
            description="Writes full text content to a target file path.",
            args_schema=WriteFileInput,
        )

    def execute(self, file_path: str, content: str, overwrite: bool = True, **kwargs: Any) -> Dict[str, Any]:
        p = Path(file_path)
        if p.exists() and not overwrite:
            return {"success": False, "error": f"File already exists and overwrite=False: {file_path}"}

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return {"success": True, "file_path": str(p), "bytes_written": len(content.encode("utf-8"))}
        except Exception as e:
            return {"success": False, "error": str(e)}


class PatchFileInput(BaseModel):
    file_path: str = Field(..., description="Target file path to patch")
    search_block: str = Field(..., description="Exact string block to find and replace")
    replacement_block: str = Field(..., description="Exact string block to insert")


class PatchFileTool(BaseTool):
    """Tool to replace exact code blocks within a file."""

    def __init__(self):
        super().__init__(
            name="patch_file",
            description="Replaces an exact block of code with new content.",
            args_schema=PatchFileInput,
        )

    def execute(self, file_path: str, search_block: str, replacement_block: str, **kwargs: Any) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            content = p.read_text(encoding="utf-8")
            if search_block not in content:
                return {"success": False, "error": "Search block not found in file."}

            occurrences = content.count(search_block)
            if occurrences > 1:
                return {"success": False, "error": f"Search block matched multiple ({occurrences}) locations."}

            new_content = content.replace(search_block, replacement_block, 1)
            p.write_text(new_content, encoding="utf-8")
            return {"success": True, "file_path": str(p), "status": "patched"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ListDirInput(BaseModel):
    dir_path: str = Field(..., description="Directory path to inspect")
    recursive: bool = Field(default=False, description="Whether to recurse subdirectories")
    max_items: int = Field(default=100, description="Max entries to return")


class ListDirTool(BaseTool):
    """Tool to list directory items."""

    def __init__(self):
        super().__init__(
            name="list_directory",
            description="Lists files and subdirectories in a directory path.",
            args_schema=ListDirInput,
        )

    def execute(self, dir_path: str, recursive: bool = False, max_items: int = 100, **kwargs: Any) -> Dict[str, Any]:
        p = Path(dir_path)
        if not p.exists() or not p.is_dir():
            return {"success": False, "error": f"Directory not found: {dir_path}"}

        try:
            items: List[Dict[str, Any]] = []
            iterator = p.rglob("*") if recursive else p.iterdir()

            # Ignore common bloated dirs
            ignore = {".git", "node_modules", ".venv", "__pycache__", ".cache", "dist", "build"}

            count = 0
            for item in iterator:
                if any(part in ignore for part in item.parts):
                    continue
                items.append({
                    "name": item.name,
                    "rel_path": str(item.relative_to(p)),
                    "is_dir": item.is_dir(),
                    "size_bytes": item.stat().st_size if item.is_file() else 0,
                })
                count += 1
                if count >= max_items:
                    break

            return {"success": True, "items": items, "total_returned": len(items)}
        except Exception as e:
            return {"success": False, "error": str(e)}
