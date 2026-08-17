"""
Security Agent for AutonomousAI.
Scans code modifications for vulnerabilities (SQLi, XSS, hardcoded secrets, unsafe eval/exec).
"""

from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import SecurityReport
from models.manager import ModelManager
from prompts.agent_prompts import SECURITY_SYSTEM_PROMPT, SECURITY_USER_PROMPT
from utils.console import ConsoleDashboard
from utils.db import MetricsDB


class SecurityAgent:
    """Security scanner node in LangGraph workflow (runs in parallel with Reviewer)."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Security", "Running vulnerability scan (SQLi, XSS, secret leaks, unsafe eval)...")

        modified_files = state.get("modified_files", [])

        prompt = SECURITY_USER_PROMPT.format(
            modified_files=", ".join(modified_files) or "None",
            diff_content="Scanning codebase files for security vulnerabilities.",
        )

        llm = ModelManager.get("security")
        output: SecurityReport = llm.generate_structured(
            prompt=prompt,
            schema_cls=SecurityReport,
            system_prompt=SECURITY_SYSTEM_PROMPT,
        )

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "security", duration_ms)

        if output.passed:
            ConsoleDashboard.agent_success("Security", "Security audit PASSED (0 critical vulnerabilities).")
        else:
            ConsoleDashboard.agent_failure("Security", f"Found {output.critical_count} critical and {output.high_count} high vulnerabilities!")

        return {
            "security": output.model_dump(),
        }
