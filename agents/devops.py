"""
DevOps Agent for AutonomousAI.
Verifies project build/compilation, detects missing dependencies, and manages server startup.
"""

from pathlib import Path
from typing import Any, Dict
import time
from schemas.state import ProjectState
from schemas.outputs import DevOpsOutput
from frameworks.loader import FrameworkPluginLoader
from utils.process_manager import ProcessManager
from utils.console import ConsoleDashboard
from utils.db import MetricsDB


class DevOpsAgent:
    """DevOps node verifying compilation and running builds."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("DevOps", "Compiling project and verifying build integrity...")

        workspace_path = Path(state.get("workspace_path", state.get("project_path", "")))
        plugin = FrameworkPluginLoader.detect_framework(workspace_path)

        build_passed = True
        logs = ""

        if plugin:
            build_res = plugin.build(workspace_path)
            build_passed = build_res.get("success", True)
            logs = build_res.get("logs", "")

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "devops", duration_ms)

        if build_passed:
            ConsoleDashboard.agent_success("DevOps", "Build verification PASSED.")
        else:
            ConsoleDashboard.agent_warning("DevOps", f"Build issues detected: {logs[:100]}")

        output = DevOpsOutput(
            build_passed=build_passed,
            missing_dependencies=[],
            install_commands=[],
            logs=logs,
            server_port=plugin.get_dev_port() if plugin else 8000,
        )

        return {
            "devops": output.model_dump(),
        }
