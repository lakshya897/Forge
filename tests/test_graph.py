"""
Integration Tests for LangGraph StateGraph Workflow and SQLite Logging.
"""

from pathlib import Path
import pytest
import time
from graph.workflow import create_graph
from models.manager import ModelManager
from utils.db import RuntimeDB, MetricsDB
from utils.config import settings


def test_langgraph_compilation_and_execution(tmp_path: Path):
    ModelManager.set_mock_mode(True)

    # Setup demo workspace
    project_dir = tmp_path / "test_app"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

    session_id = "test_graph_01"

    initial_state = {
        "session_id": session_id,
        "project_path": str(project_dir),
        "goal": "Add health check endpoint and status view",
        "constraints": ["Windows 11 Native", "Local Ollama", "Preserve formatting"],
        "acceptance_tests": [],
        "tech_stack": {},
        "ranked_context_files": [],
        "plan": [],
        "architecture": {},
        "modified_files": [],
        "created_files": [],
        "devops": {},
        "review": {},
        "security": {},
        "backend": {},
        "browser": {},
        "evaluator": {},
        "feedback": {},
        "approved": False,
        "confidence_score": 0.0,
        "iteration": 1,
        "max_iterations": 2,
        "start_time": time.time(),
        "elapsed_minutes": 0.0,
        "execution_mode": "auto",
        "status": "running",
        "error_feedback": [],
        "reports": [],
        "active_processes": [],
    }

    graph = create_graph()
    output = graph.invoke(initial_state)

    assert output is not None
    assert output.get("session_id") == session_id
    assert output.get("status") in {"completed", "timeout"}

    # Verify SQLite Runtime DB records session
    session_rec = RuntimeDB.get_session(session_id)
    assert session_rec is not None
    assert session_rec["goal"] == "Add health check endpoint and status view"

    # Verify SQLite Metrics DB records agent timings
    timings = MetricsDB.get_summary(session_id)
    assert len(timings) > 0
