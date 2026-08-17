"""
Tools Package for AutonomousAI.
Registers all operational tools into the central ToolRegistry.
"""

from .base import BaseTool
from .registry import ToolRegistry
from .filesystem import ReadFileTool, WriteFileTool, PatchFileTool, ListDirTool
from .git import GitStatusTool, GitBranchTool, GitRestoreTool, GitDiffTool, GitSnapshotTool
from .terminal import PowerShellTool, PortCheckTool, KillPortTool
from .browser import PlaywrightBrowserTool
from .search import RipgrepSearchTool, DependencyGraphTool
from .ast_editor import ValidateSyntaxTool, ASTInsertFunctionTool, ASTUpdateImportsTool

# Register all built-in tools
_BUILTIN_TOOLS = [
    ReadFileTool(),
    WriteFileTool(),
    PatchFileTool(),
    ListDirTool(),
    GitStatusTool(),
    GitBranchTool(),
    GitRestoreTool(),
    GitDiffTool(),
    GitSnapshotTool(),
    PowerShellTool(),
    PortCheckTool(),
    KillPortTool(),
    PlaywrightBrowserTool(),
    RipgrepSearchTool(),
    DependencyGraphTool(),
    ValidateSyntaxTool(),
    ASTInsertFunctionTool(),
    ASTUpdateImportsTool(),
]

for tool in _BUILTIN_TOOLS:
    ToolRegistry.register(tool)

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "ReadFileTool",
    "WriteFileTool",
    "PatchFileTool",
    "ListDirTool",
    "GitStatusTool",
    "GitBranchTool",
    "GitRestoreTool",
    "GitDiffTool",
    "GitSnapshotTool",
    "PowerShellTool",
    "PortCheckTool",
    "KillPortTool",
    "PlaywrightBrowserTool",
    "RipgrepSearchTool",
    "DependencyGraphTool",
    "ValidateSyntaxTool",
    "ASTInsertFunctionTool",
    "ASTUpdateImportsTool",
]
