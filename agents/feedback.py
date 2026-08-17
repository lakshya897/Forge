"""
Feedback Agent for AutonomousAI.
Synthesizes failure root causes, saves patch snapshots, and formats targeted fix directives for the loop.
"""

from pathlib import Path
from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import FeedbackOutput
from models.manager import ModelManager
from prompts.agent_prompts import FEEDBACK_SYSTEM_PROMPT, FEEDBACK_USER_PROMPT
from tools.git.git_tools import GitSnapshotTool
from utils.config import settings
from utils.console import ConsoleDashboard
from utils.db import RuntimeDB, MetricsDB


class FeedbackAgent:
    """Feedback node synthesizing fix instructions and managing loop iterations."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Feedback Agent", "Synthesizing iteration report and fix directives...")

        iteration = state.get("iteration", 1)
        workspace_path = state.get("workspace_path", "")
        session_id = state.get("session_id", "default")

        # 1. Save unified diff snapshot to workspace/snapshots/iter_<N>.patch
        snapshot_tool = GitSnapshotTool()
        snapshot_file = settings.workspace_root / "snapshots" / f"iter_{iteration}.patch"
        snapshot_tool.execute(repo_path=workspace_path, snapshot_path=str(snapshot_file))

        # 2. Extract failure information
        remaining_issues = state.get("evaluator", {}).get("remaining_issues", [])
        build_errors = state.get("devops", {}).get("logs", "")
        test_failures = state.get("backend", {}).get("error_log", "")
        review_issues = str(state.get("review", {}).get("issues", []))

        prompt = FEEDBACK_USER_PROMPT.format(
            remaining_issues="\n- ".join([""] + remaining_issues) if remaining_issues else "None",
            build_errors=build_errors[:500] or "None",
            test_failures=test_failures[:500] or "None",
            review_issues=review_issues[:500] or "None",
        )

        llm = ModelManager.get("feedback")
        output: FeedbackOutput = llm.generate_structured(
            prompt=prompt,
            schema_cls=FeedbackOutput,
            system_prompt=FEEDBACK_SYSTEM_PROMPT,
        )

        # 3. Write reports/iteration_00X.md
        reports_dir = settings.reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)
        iter_report = reports_dir / f"iteration_{iteration:03d}.md"

        report_md = f"""# AutonomousAI — Iteration {iteration:03d} Report

**Session ID:** `{session_id}`
**Confidence Score:** {state.get('confidence_score', 0.0):.2f} / 1.00
**Approved:** {state.get('approved', False)}
**Modified Files:** {', '.join(state.get('modified_files', []))}
**Snapshot:** `{snapshot_file}`

## Root Causes
{chr(10).join(f"- {c}" for c in output.root_causes) or "- None detected"}

## Targeted Fixes
{chr(10).join(f"- {f}" for f in output.targeted_fixes) or "- None"}
"""
        iter_report.write_text(report_md, encoding="utf-8")

        # 4. Log iteration in SQLite RuntimeDB
        RuntimeDB.log_iteration(
            session_id=session_id,
            iteration=iteration,
            modified_files=state.get("modified_files", []),
            tests_passed=state.get("backend", {}).get("passed", True),
            confidence=state.get("confidence_score", 0.0),
            summary=f"Iteration {iteration} evaluated. Fix tasks: {len(output.targeted_fixes)}",
        )

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(session_id, "feedback", duration_ms)

        ConsoleDashboard.agent_success("Feedback Agent", f"Iteration {iteration:03d} logged. Fix directives ready.")

        return {
            "feedback": output.model_dump(),
            "error_feedback": output.targeted_fixes,
            "iteration": iteration + 1,
            "reports": state.get("reports", []) + [str(iter_report)],
        }
