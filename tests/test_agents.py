"""
Unit Tests for Framework Plugins, Agent Nodes, and Evaluator.
"""

from pathlib import Path
import pytest
from frameworks.loader import FrameworkPluginLoader
from schemas.outputs import ProductOwnerOutput, EvaluatorOutput, ReviewerOutput
from agents.evaluator import EvaluatorAgent
from models.manager import ModelManager


def test_framework_loader_discovery():
    plugins = FrameworkPluginLoader.load_plugins()
    assert len(plugins) >= 5
    names = [p.name for p in plugins]
    assert "react" in names
    assert "fastapi" in names
    assert "django" in names
    assert "next" in names


def test_framework_detection_fastapi(tmp_path: Path):
    (tmp_path / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")
    plugin = FrameworkPluginLoader.detect_framework(tmp_path)
    assert plugin is not None
    assert plugin.name == "fastapi"
    assert plugin.get_dev_port() == 8000


def test_evaluator_approval_logic():
    ModelManager.set_mock_mode(True)
    state = {
        "session_id": "test_sess",
        "acceptance_tests": ["Endpoint works", "No errors"],
        "devops": {"logs": "Build passed"},
        "backend": {"passed": True},
        "browser": {"passed": True},
        "security": {"passed": True},
        "review": {"passed": True},
        "iteration": 1,
    }
    result = EvaluatorAgent.run(state)
    assert result["approved"] is True
    assert result["confidence_score"] >= 0.90
