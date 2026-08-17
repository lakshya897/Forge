"""
Model Registry for AutonomousAI.
Maps agent roles to corresponding LLM configurations and models.
"""

from typing import Dict, Any

ROLE_MODEL_MAPPING: Dict[str, Dict[str, Any]] = {
    # 7B Reasoning Models
    "product_owner": {"type": "7b", "temperature": 0.2},
    "planner": {"type": "7b", "temperature": 0.2},
    "evaluator": {"type": "7b", "temperature": 0.1},
    "feedback": {"type": "7b", "temperature": 0.2},

    # 14B Coder Models
    "architect": {"type": "14b", "temperature": 0.2},
    "implementer": {"type": "14b", "temperature": 0.1},
    "reviewer": {"type": "14b", "temperature": 0.1},
    "security": {"type": "14b", "temperature": 0.1},

    # Deterministic Agents (No LLM directly required, but fallback provided)
    "orchestrator": {"type": "7b", "temperature": 0.0},
    "analyzer": {"type": "7b", "temperature": 0.0},
    "context_manager": {"type": "none", "temperature": 0.0},
    "devops": {"type": "14b", "temperature": 0.0},
    "backend_tester": {"type": "7b", "temperature": 0.0},
    "browser_tester": {"type": "7b", "temperature": 0.0},
}
