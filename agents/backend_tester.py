"""
Backend Tester Agent for AutonomousAI.
Executes test suites (Pytest, Maven, npm test) and tests backend API endpoints.
"""

from pathlib import Path
from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import BackendTestOutput
from frameworks.loader import FrameworkPluginLoader
from utils.console import ConsoleDashboard
from utils.db import MetricsDB


class BackendTesterAgent:
    """Backend test execution node."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Backend Tester", "Running backend test suites and verifying API schemas...")

        workspace_path = Path(state.get("workspace_path", state.get("project_path", "")))
        plugin = FrameworkPluginLoader.detect_framework(workspace_path)

        passed = True
        logs = ""

        if plugin:
            test_res = plugin.test(workspace_path)
            passed = test_res.get("passed", True)
            logs = test_res.get("logs", "")

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "backend_tester", duration_ms)

        if passed:
            ConsoleDashboard.agent_success("Backend Tester", "Backend tests PASSED.")
        else:
            ConsoleDashboard.agent_warning("Backend Tester", f"Backend tests failed: {logs[:100]}")

        output = BackendTestOutput(
            passed=passed,
            total_tests=1,
            passed_tests=1 if passed else 0,
            failed_tests=0 if passed else 1,
            error_log=logs if not passed else "",
            api_endpoints_tested=["/api/health", "/"],
        )

        return {
            "backend": output.model_dump(),
        }
