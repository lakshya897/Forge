"""
Unit Tests for ModelManager, Mock Provider, and JSON Repair Engine.
"""

import pytest
from models.manager import ModelManager
from tools.json.json_repair import JSONRepairEngine
from schemas.outputs import ProductOwnerOutput, PlannerOutput, EvaluatorOutput


def test_model_manager_fallback():
    """Verify that ModelManager provides a functional model wrapper even when Ollama is offline."""
    ModelManager.set_mock_mode(True)
    model = ModelManager.get("planner")
    assert model is not None

    output = model.generate_structured("Plan tasks", PlannerOutput)
    assert isinstance(output, PlannerOutput)
    assert len(output.tasks) > 0


def test_json_repair_valid_json():
    raw = '{"goal": "Add login feature", "constraints": ["No paid APIs"], "acceptance_tests": ["Passes pytest"]}'
    repaired = JSONRepairEngine.repair(raw)
    assert repaired["goal"] == "Add login feature"


def test_json_repair_markdown_fences():
    raw = """```json
{
  "goal": "Refactor router",
  "constraints": [],
  "acceptance_tests": ["Build passes"]
}
```"""
    repaired = JSONRepairEngine.repair(raw)
    assert repaired["goal"] == "Refactor router"


def test_json_repair_trailing_commas():
    raw = '{"goal": "Fix bug", "acceptance_tests": ["Test 1", "Test 2",],}'
    repaired = JSONRepairEngine.repair(raw)
    assert repaired["goal"] == "Fix bug"
    assert len(repaired["acceptance_tests"]) == 2


def test_json_repair_unbalanced_braces():
    raw = '{"goal": "Incomplete output", "acceptance_tests": ["Test 1"'
    repaired = JSONRepairEngine.repair(raw)
    assert "goal" in repaired


def test_parse_to_pydantic_schema():
    raw = """Here is the plan:
```json
{
  "confidence": 0.95,
  "acceptance_passed": true,
  "passed_criteria": ["All tests green"],
  "failed_criteria": [],
  "remaining_issues": [],
  "recommendation": "approve"
}
```
Hope this helps!"""
    result = JSONRepairEngine.parse_to_schema(raw, EvaluatorOutput)
    assert isinstance(result, EvaluatorOutput)
    assert result.confidence == 0.95
    assert result.acceptance_passed is True
