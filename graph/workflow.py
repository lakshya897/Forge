"""
LangGraph StateGraph Workflow Orchestrator for AutonomousAI.
Connects 14 specialized agents with parallel quality/security validation and feedback looping.
"""

from typing import Any, Dict
from pathlib import Path
import time
from langgraph.graph import StateGraph, START, END
from schemas.state import ProjectState
from agents import (
    OrchestratorAgent,
    ProductOwnerAgent,
    AnalyzerAgent,
    ContextManagerAgent,
    PlannerAgent,
    ArchitectAgent,
    ImplementerAgent,
    DevOpsAgent,
    ReviewerAgent,
    SecurityAgent,
    BackendTesterAgent,
    BrowserTesterAgent,
    EvaluatorAgent,
    FeedbackAgent,
)
from graph.routing import should_continue_iteration
from graph.memory import ProjectMemory
from utils.config import settings
from utils.console import ConsoleDashboard
from utils.db import RuntimeDB


def node_orchestrator(state: ProjectState) -> Dict[str, Any]:
    return OrchestratorAgent.run(state)


def node_product_owner(state: ProjectState) -> Dict[str, Any]:
    return ProductOwnerAgent.run(state)


def node_analyzer(state: ProjectState) -> Dict[str, Any]:
    return AnalyzerAgent.run(state)


def node_context_manager(state: ProjectState) -> Dict[str, Any]:
    return ContextManagerAgent.run(state)


def node_planner(state: ProjectState) -> Dict[str, Any]:
    return PlannerAgent.run(state)


def node_architect(state: ProjectState) -> Dict[str, Any]:
    return ArchitectAgent.run(state)


def node_implementer(state: ProjectState) -> Dict[str, Any]:
    return ImplementerAgent.run(state)


def node_devops(state: ProjectState) -> Dict[str, Any]:
    return DevOpsAgent.run(state)


def node_reviewer(state: ProjectState) -> Dict[str, Any]:
    return ReviewerAgent.run(state)


def node_security(state: ProjectState) -> Dict[str, Any]:
    return SecurityAgent.run(state)


def node_backend_tester(state: ProjectState) -> Dict[str, Any]:
    return BackendTesterAgent.run(state)


def node_browser_tester(state: ProjectState) -> Dict[str, Any]:
    return BrowserTesterAgent.run(state)


def node_evaluator(state: ProjectState) -> Dict[str, Any]:
    return EvaluatorAgent.run(state)


def node_feedback(state: ProjectState) -> Dict[str, Any]:
    return FeedbackAgent.run(state)


def node_finalizer(state: ProjectState) -> Dict[str, Any]:
    """Generates final report and finishes session."""
    session_id = state.get("session_id", "default")
    approved = state.get("approved", False)
    confidence = state.get("confidence_score", 0.0)
    modified_files = state.get("modified_files", [])

    reports_dir = settings.reports_dir
    reports_dir.mkdir(parents=True, exist_ok=True)
    final_report_file = reports_dir / "final_report.md"

    report_content = f"""# AutonomousAI — Final Execution Report

**Session ID:** `{session_id}`
**Status:** {'SUCCESS / APPROVED' if approved else 'INCOMPLETE / TIMEOUT'}
**Confidence Score:** {confidence:.2f} / 1.00
**Total Iterations:** {state.get('iteration', 1)}
**Modified Files:**
{chr(10).join(f"- `{f}`" for f in modified_files)}

## Acceptance Criteria Summary
{chr(10).join(f"- {c}" for c in state.get('acceptance_tests', []))}

---
*AutonomousAI local engineering runtime completed.*
"""
    final_report_file.write_text(report_content, encoding="utf-8")

    if approved:
        ProjectMemory.record_success(state.get("goal", ""), modified_files)
        ConsoleDashboard.agent_success("Workflow", f"Goal achieved with confidence {confidence:.2f}! Final report saved to {final_report_file}")
    else:
        ConsoleDashboard.agent_warning("Workflow", f"Execution budget reached. Summary saved to {final_report_file}")

    RuntimeDB.save_session(
        session_id=session_id,
        project_path=state.get("project_path", ""),
        goal=state.get("goal", ""),
        status="completed" if approved else "timeout",
        state_dict=dict(state),
    )

    return {
        "status": "completed" if approved else "timeout",
        "reports": state.get("reports", []) + [str(final_report_file)],
    }


def create_graph() -> Any:
    """Construct and compile the LangGraph state graph."""
    workflow = StateGraph(ProjectState)

    # Register Nodes
    workflow.add_node("orchestrator", node_orchestrator)
    workflow.add_node("product_owner", node_product_owner)
    workflow.add_node("analyzer", node_analyzer)
    workflow.add_node("context_manager", node_context_manager)
    workflow.add_node("planner", node_planner)
    workflow.add_node("architect", node_architect)
    workflow.add_node("implementer", node_implementer)
    workflow.add_node("devops", node_devops)
    workflow.add_node("reviewer", node_reviewer)
    workflow.add_node("security", node_security)
    workflow.add_node("backend_tester", node_backend_tester)
    workflow.add_node("browser_tester", node_browser_tester)
    workflow.add_node("evaluator", node_evaluator)
    workflow.add_node("feedback", node_feedback)
    workflow.add_node("finalizer", node_finalizer)

    # Core Sequential Flow
    workflow.add_edge(START, "orchestrator")
    workflow.add_edge("orchestrator", "product_owner")
    workflow.add_edge("product_owner", "analyzer")
    workflow.add_edge("analyzer", "context_manager")
    workflow.add_edge("context_manager", "planner")
    workflow.add_edge("planner", "architect")
    workflow.add_edge("architect", "implementer")
    workflow.add_edge("implementer", "devops")

    # Parallel Reviewer and Security Branches
    workflow.add_edge("devops", "reviewer")
    workflow.add_edge("devops", "security")
    workflow.add_edge("reviewer", "backend_tester")
    workflow.add_edge("security", "backend_tester")

    # Testing & Evaluation Flow
    workflow.add_edge("backend_tester", "browser_tester")
    workflow.add_edge("browser_tester", "evaluator")

    # Conditional Routing Loop
    workflow.add_conditional_edges(
        "evaluator",
        should_continue_iteration,
        {
            "approved": "finalizer",
            "budget_exceeded": "finalizer",
            "feedback_loop": "feedback",
        },
    )

    # Feedback loop connects back to implementer
    workflow.add_edge("feedback", "implementer")
    workflow.add_edge("finalizer", END)

    return workflow.compile()
