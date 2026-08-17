"""
Architect Agent for AutonomousAI.
Maps routes, component hierarchies, backend endpoints, and dependency graphs.
"""

from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import ArchitectOutput
from models.manager import ModelManager
from prompts.agent_prompts import ARCHITECT_SYSTEM_PROMPT, ARCHITECT_USER_PROMPT
from utils.console import ConsoleDashboard
from utils.db import RuntimeDB, MetricsDB


class ArchitectAgent:
    """Architect node in LangGraph workflow."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Architect", "Analyzing system architecture and routing tree...")

        goal = state.get("goal", "")
        tech_stack = state.get("tech_stack", {})
        import_graph = state.get("architecture", {}).get("import_graph", {})

        prompt = ARCHITECT_USER_PROMPT.format(
            goal=goal,
            tech_stack=str(tech_stack),
            import_graph=str(import_graph)[:2000],
        )

        llm = ModelManager.get("architect")
        output: ArchitectOutput = llm.generate_structured(
            prompt=prompt,
            schema_cls=ArchitectOutput,
            system_prompt=ARCHITECT_SYSTEM_PROMPT,
        )

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "architect", duration_ms)

        ConsoleDashboard.agent_success("Architect", f"Mapped {len(output.backend_endpoints)} endpoints and {len(output.component_tree)} components.")

        session_id = state.get("session_id", "default")
        RuntimeDB.save_checkpoint(session_id, "checkpoint_arch", output.model_dump())

        return {
            "architecture": output.model_dump(),
        }
