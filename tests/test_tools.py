"""
Unit Tests for Tool Registry, Filesystem, Git Safety, and AST Editor Tools.
"""

from pathlib import Path
import pytest
from tools.registry import ToolRegistry
from tools.filesystem.fs_tools import ReadFileTool, WriteFileTool, PatchFileTool, ListDirTool
from tools.ast_editor.ast_tools import ValidateSyntaxTool, ASTInsertFunctionTool, ASTUpdateImportsTool
from tools.search.search_tools import RipgrepSearchTool, DependencyGraphTool


def test_tool_registry_discovery():
    tools = ToolRegistry.list_tools()
    assert len(tools) >= 10
    names = [t["name"] for t in tools]
    assert "read_file" in names
    assert "write_file" in names
    assert "patch_file" in names
    assert "validate_syntax" in names
    assert "git_status" in names


def test_filesystem_tools(tmp_path: Path):
    test_file = tmp_path / "sample.txt"
    write_tool = WriteFileTool()
    read_tool = ReadFileTool()
    patch_tool = PatchFileTool()

    # 1. Write
    w_res = write_tool.execute(file_path=str(test_file), content="Line 1\nLine 2\nLine 3\n")
    assert w_res["success"] is True

    # 2. Read
    r_res = read_tool.execute(file_path=str(test_file))
    assert r_res["success"] is True
    assert "Line 2" in r_res["content"]

    # 3. Patch
    p_res = patch_tool.execute(
        file_path=str(test_file),
        search_block="Line 2",
        replacement_block="Line 2 Modified",
    )
    assert p_res["success"] is True

    # 4. Verify patch
    r_res2 = read_tool.execute(file_path=str(test_file))
    assert "Line 2 Modified" in r_res2["content"]


def test_ast_tools(tmp_path: Path):
    syntax_tool = ValidateSyntaxTool()
    insert_tool = ASTInsertFunctionTool()
    import_tool = ASTUpdateImportsTool()

    # 1. Syntax validation
    valid_py = "def hello():\n    return 'world'\n"
    invalid_py = "def hello(\nreturn 'world'\n"

    v1 = syntax_tool.execute(code=valid_py, language="python")
    assert v1["valid"] is True

    v2 = syntax_tool.execute(code=invalid_py, language="python")
    assert v2["valid"] is False

    # 2. Insert function
    py_file = tmp_path / "app.py"
    py_file.write_text("a = 1\n", encoding="utf-8")

    ins_res = insert_tool.execute(
        file_path=str(py_file),
        function_code="def new_function():\n    return 42\n",
    )
    assert ins_res["success"] is True
    assert "def new_function" in py_file.read_text(encoding="utf-8")

    # 3. Update imports
    imp_res = import_tool.execute(
        file_path=str(py_file),
        imports_to_add=["import os", "from typing import List"],
    )
    assert imp_res["success"] is True
    assert "import os" in py_file.read_text(encoding="utf-8")


def test_search_and_graph_tools(tmp_path: Path):
    f1 = tmp_path / "module_a.py"
    f2 = tmp_path / "module_b.py"

    f1.write_text("import os\nfrom module_b import helper\n\ndef run():\n    return helper()\n", encoding="utf-8")
    f2.write_text("def helper():\n    return 'sample_keyword'\n", encoding="utf-8")

    search_tool = RipgrepSearchTool()
    res = search_tool.execute(query="sample_keyword", path=str(tmp_path))
    assert res["total_matches"] >= 1

    dep_tool = DependencyGraphTool()
    graph_res = dep_tool.execute(project_path=str(tmp_path))
    assert "module_a.py" in graph_res["graph"]
    assert "os" in graph_res["graph"]["module_a.py"]
