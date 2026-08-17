"""
Product Owner Agent for AutonomousAI.
Translates user requirements into structured technical goals, constraints, and acceptance criteria.
"""

from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import ProductOwnerOutput
from models.manager import ModelManager
from prompts.agent_prompts import PRODUCT_OWNER_SYSTEM_PROMPT, PRODUCT_OWNER_USER_PROMPT
from utils.console import ConsoleDashboard
from utils.db import RuntimeDB, MetricsDB


class ProductOwnerAgent:
    """Product Owner node in LangGraph workflow."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Product Owner", "Analyzing user requirement and formulating acceptance criteria...")

        requirement = state.get("goal", "")
        project_path = state.get("workspace_path", state.get("project_path", ""))
        tech_stack = state.get("tech_stack", {})

        prompt = PRODUCT_OWNER_USER_PROMPT.format(
            requirement=requirement,
            project_path=project_path,
            tech_stack=str(tech_stack),
        )

        llm = ModelManager.get("product_owner")
        output: ProductOwnerOutput = llm.generate_structured(
            prompt=prompt,
            schema_cls=ProductOwnerOutput,
            system_prompt=PRODUCT_OWNER_SYSTEM_PROMPT,
        )

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "product_owner", duration_ms)

        ConsoleDashboard.agent_success(
            "Product Owner",
            f"Goal refined. Formulated {len(output.acceptance_tests)} acceptance criteria.",
        )

        # Checkpoint stage
        session_id = state.get("session_id", "default")
        RuntimeDB.save_checkpoint(session_id, "checkpoint_po", {
            "goal": output.goal,
            "constraints": output.constraints,
            "acceptance_tests": output.acceptance_tests,
        })

        return {
            "goal": output.goal,
            "constraints": output.constraints,
            "acceptance_tests": output.acceptance_tests,
        }
