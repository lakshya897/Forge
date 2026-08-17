"""
Planner Agent for AutonomousAI.
Breaks down Product Owner specifications into ordered atomic development tasks.
"""

from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import PlannerOutput
from models.manager import ModelManager
from prompts.agent_prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_PROMPT
from utils.console import ConsoleDashboard
from utils.db import RuntimeDB, MetricsDB


class PlannerAgent:
    """Planner node in LangGraph workflow."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Planner", "Generating atomic execution plan...")

        goal = state.get("goal", "")
        acceptance = state.get("acceptance_tests", [])
        tech_stack = state.get("tech_stack", {})
        relevant_files = [f.get("path") for f in state.get("ranked_context_files", [])]

        prompt = PLANNER_USER_PROMPT.format(
            goal=goal,
            acceptance_criteria="\n- ".join([""] + acceptance),
            tech_stack=str(tech_stack),
            relevant_files=", ".join(relevant_files) or "None detected",
        )

        llm = ModelManager.get("planner")
        output: PlannerOutput = llm.generate_structured(
            prompt=prompt,
            schema_cls=PlannerOutput,
            system_prompt=PLANNER_SYSTEM_PROMPT,
        )

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "planner", duration_ms)

        ConsoleDashboard.show_tasks(output.tasks)
        ConsoleDashboard.agent_success("Planner", f"Created {len(output.tasks)} tasks. Risk level: {output.risk_level}.")

        # Checkpoint stage
        session_id = state.get("session_id", "default")
        RuntimeDB.save_checkpoint(session_id, "checkpoint_plan", {
            "tasks": [t.model_dump() for t in output.tasks],
            "estimated_files": output.estimated_files,
        })

        return {
            "plan": [t.model_dump() for t in output.tasks],
        }
