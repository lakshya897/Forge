"""
Git Safety Tools for AutonomousAI.
Manages repository branches, diff snapshots, safe restores, and atomic commits.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import subprocess
from pydantic import BaseModel, Field
from tools.base import BaseTool


class GitStatusTool(BaseTool):
    """Tool to inspect Git status."""

    def __init__(self):
        super().__init__(
            name="git_status",
            description="Checks current Git branch, modified files, and untracked files.",
        )

    def execute(self, repo_path: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["git", "status", "--short", "--branch"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return {
                "success": res.returncode == 0,
                "output": res.stdout.strip(),
                "error": res.stderr.strip() if res.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class GitBranchTool(BaseTool):
    """Tool to create and switch to an autonomous safety branch."""

    def __init__(self):
        super().__init__(
            name="git_create_branch",
            description="Creates and checks out a safe isolated branch for autonomous AI work.",
        )

    def execute(self, repo_path: str, branch_name: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["git", "checkout", "-B", branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return {
                "success": res.returncode == 0,
                "branch": branch_name,
                "output": res.stdout.strip() or res.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class GitRestoreTool(BaseTool):
    """Tool to cleanly restore modified files without destructive hard reset."""

    def __init__(self):
        super().__init__(
            name="git_restore",
            description="Safely restores modified files in working tree (git restore .).",
        )

    def execute(self, repo_path: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["git", "restore", "."],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return {
                "success": res.returncode == 0,
                "output": "Working tree restored to baseline cleanly.",
                "error": res.stderr.strip() if res.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class GitDiffTool(BaseTool):
    """Tool to generate unified diff of changes."""

    def __init__(self):
        super().__init__(
            name="git_diff",
            description="Generates unified diff between working tree and HEAD.",
        )

    def execute(self, repo_path: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["git", "diff"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return {
                "success": res.returncode == 0,
                "diff": res.stdout,
                "has_changes": len(res.stdout.strip()) > 0,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class GitSnapshotTool(BaseTool):
    """Tool to export a unified patch snapshot."""

    def __init__(self):
        super().__init__(
            name="git_create_snapshot",
            description="Saves a unified diff patch snapshot to disk for rollback.",
        )

    def execute(self, repo_path: str, snapshot_path: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["git", "diff"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            diff_text = res.stdout
            out = Path(snapshot_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(diff_text, encoding="utf-8")
            return {
                "success": True,
                "snapshot_path": str(out),
                "patch_size": len(diff_text),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
