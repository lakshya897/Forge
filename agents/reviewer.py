"""
Reviewer Agent for AutonomousAI.
Audits code changes for bugs, smells, performance bottlenecks, and architectural conformance.
"""

from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import ReviewerOutput
from models.manager import ModelManager
from prompts.agent_prompts import REVIEWER_SYSTEM_PROMPT, REVIEWER_USER_PROMPT
from utils.console import ConsoleDashboard
from utils.db import MetricsDB


class ReviewerAgent:
    """Reviewer node in LangGraph workflow (runs in parallel with Security)."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Reviewer", "Auditing code diffs and reviewing code quality...")

        modified_files = state.get("modified_files", [])
        diff_content = str(state.get("devops", {}).get("logs", ""))

        prompt = REVIEWER_USER_PROMPT.format(
            modified_files=", ".join(modified_files) or "None",
            diff_content=diff_content[:1500] or "No diffs available",
        )

        llm = ModelManager.get("reviewer")
        output: ReviewerOutput = llm.generate_structured(
            prompt=prompt,
            schema_cls=ReviewerOutput,
            system_prompt=REVIEWER_SYSTEM_PROMPT,
        )

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "reviewer", duration_ms)

        if output.passed:
            ConsoleDashboard.agent_success("Reviewer", "Code review PASSED (0 critical issues).")
        else:
            ConsoleDashboard.agent_warning("Reviewer", f"Found {output.critical_count} critical issues and {output.warning_count} warnings.")

        return {
            "review": output.model_dump(),
        }
