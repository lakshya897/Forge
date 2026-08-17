"""
Conditional Routing Functions for AutonomousAI LangGraph Workflow.
Evaluates approval status and iteration budget limits.
"""

from typing import Literal
import time
from schemas.state import ProjectState
from utils.config import settings


def should_continue_iteration(state: ProjectState) -> Literal["approved", "feedback_loop", "budget_exceeded"]:
    """
    Evaluate if the workflow should terminate on success, loop back for fixes, or abort on timeout.
    """
    # Check approval
    if state.get("approved", False):
        return "approved"

    # Check budget limits
    current_iter = state.get("iteration", 1)
    max_iter = state.get("max_iterations", settings.max_iterations)
    start_time = state.get("start_time", time.time())
    elapsed_min = (time.time() - start_time) / 60.0
    budget_min = settings.time_budget_minutes

    if current_iter > max_iter or elapsed_min >= budget_min:
        return "budget_exceeded"

    return "feedback_loop"
