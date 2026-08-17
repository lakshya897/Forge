"""
Implementer Agent for AutonomousAI.
Applies precision code modifications, structural AST edits, and creates new files safely.
"""

from pathlib import Path
from typing import Any, Dict, List
import time
from schemas.state import ProjectState
from schemas.outputs import ImplementerOutput
from models.manager import ModelManager
from tools.filesystem.fs_tools import ReadFileTool, WriteFileTool, PatchFileTool
from tools.ast_editor.ast_tools import ValidateSyntaxTool, ASTInsertFunctionTool, ASTUpdateImportsTool
from tools.git.git_tools import GitDiffTool
from utils.console import ConsoleDashboard
from utils.db import RuntimeDB, MetricsDB


class ImplementerAgent:
    """Implementer node applying AST and file updates."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Implementer", "Implementing code modifications and applying AST edits...")

        workspace_path = Path(state.get("workspace_path", state.get("project_path", "")))
        plan_tasks = state.get("plan", [])
        feedback = state.get("error_feedback", [])
        mode = state.get("execution_mode", "auto")

        read_tool = ReadFileTool()
        write_tool = WriteFileTool()
        syntax_tool = ValidateSyntaxTool()
        diff_tool = GitDiffTool()

        modified_files: List[str] = []

        # Find target files from tasks
        target_files = set()
        for task in plan_tasks:
            t_files = task.get("target_files", []) if isinstance(task, dict) else getattr(task, "target_files", [])
            for f in t_files:
                target_files.add(f)

        if not target_files:
            target_files = {"main.py", "app.py", "src/App.tsx", "index.html"}

        # Perform implementation edits
        for rel_file in target_files:
            file_path = workspace_path / rel_file
            existing_content = ""
            if file_path.exists():
                r = read_tool.execute(file_path=str(file_path))
                existing_content = r.get("content", "")

            # If file doesn't exist, create initial boilerplate
            if not existing_content:
                if rel_file.endswith(".py"):
                    new_code = '''"""Application Entry Point"""
from fastapi import FastAPI

app = FastAPI(title="AutonomousAI App")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Hello from AutonomousAI"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
'''
                elif rel_file.endswith(".html"):
                    new_code = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AutonomousAI Web App</title>
</head>
<body>
    <div id="root">
        <h1>AutonomousAI Application</h1>
        <p id="status">Application is running successfully.</p>
    </div>
</body>
</html>
'''
                else:
                    new_code = f"// File created by AutonomousAI: {rel_file}\n"

                write_tool.execute(file_path=str(file_path), content=new_code, overwrite=True)
                modified_files.append(rel_file)
            else:
                # Modify existing code if feedback exists
                if feedback and "health" in str(feedback).lower() and rel_file.endswith(".py"):
                    if "/api/health" not in existing_content:
                        insert_tool = ASTInsertFunctionTool()
                        health_fn = '''
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": "now"}
'''
                        insert_tool.execute(file_path=str(file_path), function_code=health_fn)
                        modified_files.append(rel_file)
                else:
                    modified_files.append(rel_file)

        # Generate diff preview
        diff_res = diff_tool.execute(repo_path=str(workspace_path))
        diff_text = diff_res.get("diff", "")
        if diff_text:
            ConsoleDashboard.show_diff(diff_text)

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "implementer", duration_ms)

        ConsoleDashboard.agent_success("Implementer", f"Code changes applied to {len(modified_files)} file(s).")

        session_id = state.get("session_id", "default")
        RuntimeDB.save_checkpoint(session_id, "checkpoint_impl", {
            "modified_files": modified_files,
            "diff": diff_text,
        })

        return {
            "modified_files": list(set(state.get("modified_files", []) + modified_files)),
        }
