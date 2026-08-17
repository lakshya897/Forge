"""
Evaluator Agent for AutonomousAI.
Impartially evaluates acceptance criteria, calculates confidence score (0.00 - 1.00),
and assigns the approval recommendation.
"""

from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import EvaluatorOutput
from models.manager import ModelManager
from prompts.agent_prompts import EVALUATOR_SYSTEM_PROMPT, EVALUATOR_USER_PROMPT
from utils.console import ConsoleDashboard
from utils.db import MetricsDB


class EvaluatorAgent:
    """Independent evaluation node verifying acceptance criteria."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Evaluator", "Assessing acceptance criteria and scoring confidence...")

        acceptance = state.get("acceptance_tests", [])
        build_logs = state.get("devops", {}).get("logs", "Build passed")
        backend_out = str(state.get("backend", {}))
        browser_out = str(state.get("browser", {}))
        security_summary = str(state.get("security", {}))
        review_summary = str(state.get("review", {}))

        prompt = EVALUATOR_USER_PROMPT.format(
            acceptance_criteria="\n- ".join([""] + acceptance),
            build_logs=build_logs[:500],
            backend_output=backend_out[:500],
            browser_output=browser_out[:500],
            security_summary=security_summary[:500],
            review_summary=review_summary[:500],
        )

        llm = ModelManager.get("evaluator")
        output: EvaluatorOutput = llm.generate_structured(
            prompt=prompt,
            schema_cls=EvaluatorOutput,
            system_prompt=EVALUATOR_SYSTEM_PROMPT,
        )

        # Enforce strict criteria: backend pass, security pass, review pass
        backend_pass = state.get("backend", {}).get("passed", True)
        security_pass = state.get("security", {}).get("passed", True)
        review_pass = state.get("review", {}).get("passed", True)

        approved = output.confidence >= 0.90 and output.acceptance_passed and backend_pass and security_pass and review_pass

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "evaluator", duration_ms)

        ConsoleDashboard.show_iteration_summary(
            iteration=state.get("iteration", 1),
            confidence=output.confidence,
            tests_passed=backend_pass,
            review_passed=review_pass,
            security_passed=security_pass,
        )

        if approved:
            ConsoleDashboard.agent_success("Evaluator", f"Acceptance criteria satisfied with confidence {output.confidence:.2f}.")
        else:
            ConsoleDashboard.agent_warning("Evaluator", f"Confidence {output.confidence:.2f} < 0.90. Iteration required.")

        return {
            "evaluator": output.model_dump(),
            "approved": approved,
            "confidence_score": output.confidence,
        }
