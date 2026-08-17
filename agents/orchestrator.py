"""
Orchestrator Agent for AutonomousAI.
Manages workspace sandbox isolation, session checkpoints, SQLite state persistence, and process lifecycle.
"""

from pathlib import Path
from typing import Any, Dict
import shutil
import uuid
import time
from schemas.state import ProjectState
from utils.config import settings
from utils.db import RuntimeDB
from utils.console import ConsoleDashboard
from tools.git.git_tools import GitStatusTool, GitBranchTool


class OrchestratorAgent:
    """Coordinates session startup, workspace cloning, and recovery."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        session_id = state.get("session_id") or str(uuid.uuid4())[:8]
        project_path = Path(state.get("project_path", str(settings.workspace_root)))
        workspace_base = settings.workspace_root / "sessions" / f"session_{session_id}"
        workspace_base.mkdir(parents=True, exist_ok=True)

        ConsoleDashboard.agent_start("Orchestrator", f"Initializing workspace session '{session_id}'...")

        # 1. Create isolated copy in workspace if not already created
        if not (workspace_base / ".initialized").exists():
            if project_path.exists() and project_path != workspace_base:
                for item in project_path.iterdir():
                    if item.name in {".git", ".venv", "node_modules", "__pycache__", ".cache", "workspace", "runtime"}:
                        continue
                    dest = workspace_base / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)
            (workspace_base / ".initialized").write_text("1", encoding="utf-8")

        # 2. Setup safe Git working branch
        branch_tool = GitBranchTool()
        branch_name = f"autonomous/feature-{session_id}"
        branch_tool.execute(repo_path=str(workspace_base), branch_name=branch_name)

        # 3. Initialize SQLite state
        goal = state.get("goal", "")
        RuntimeDB.save_session(
            session_id=session_id,
            project_path=str(project_path),
            goal=goal,
            status="running",
            state_dict=dict(state),
        )
        RuntimeDB.save_checkpoint(session_id, "orchestrator", dict(state))

        ConsoleDashboard.agent_success("Orchestrator", f"Session ready at: {workspace_base}")

        return {
            "session_id": session_id,
            "workspace_path": str(workspace_base),
            "status": "running",
            "iteration": state.get("iteration", 1),
            "start_time": state.get("start_time", time.time()),
            "reports": state.get("reports", []),
        }
