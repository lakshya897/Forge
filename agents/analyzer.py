"""
Project Analyzer Agent for AutonomousAI.
Detects frameworks, package managers, build commands, test frameworks, and writes reports/project_analysis.md.
"""

from pathlib import Path
from typing import Any, Dict
import time
from schemas.state import ProjectState
from frameworks.loader import FrameworkPluginLoader
from utils.config import settings
from utils.console import ConsoleDashboard
from utils.db import MetricsDB


class AnalyzerAgent:
    """Project Analyzer node detecting frameworks and tech stacks."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Analyzer", "Detecting project framework, tech stack, and build tooling...")

        workspace_path = Path(state.get("workspace_path", state.get("project_path", str(settings.workspace_root))))

        plugin = FrameworkPluginLoader.detect_framework(workspace_path)
        if plugin:
            info = plugin.get_framework_info(workspace_path)
        else:
            info = {
                "framework": "Generic / Python",
                "package_manager": "pip",
                "build_command": None,
                "test_command": "pytest",
                "dev_command": None,
                "dev_port": 8000,
            }

        # Generate reports/project_analysis.md
        reports_dir = settings.reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / "project_analysis.md"

        report_content = f"""# AutonomousAI — Project Analysis Report

**Workspace Path:** `{workspace_path}`
**Detected Framework:** {info.get('framework')}
**Package Manager:** {info.get('package_manager')}
**Build Command:** `{info.get('build_command') or 'None'}`
**Test Command:** `{info.get('test_command') or 'None'}`
**Development Command:** `{info.get('dev_command') or 'None'}`
**Target Port:** `{info.get('dev_port')}`

---
*Report generated automatically by AutonomousAI Project Analyzer Agent.*
"""
        report_file.write_text(report_content, encoding="utf-8")

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "analyzer", duration_ms)

        ConsoleDashboard.agent_success("Analyzer", f"Detected {info.get('framework')} ({info.get('package_manager')}) on port {info.get('dev_port')}")

        return {
            "tech_stack": info,
        }
