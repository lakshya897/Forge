"""
Base Framework Plugin Interface for AutonomousAI.
Defines lifecycle hooks for detecting, building, testing, and running any tech stack.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess


class BaseFrameworkPlugin(ABC):
    """Abstract base class for all framework plugins."""

    name: str = "base"
    priority: int = 50
    default_port: int = 3000

    @abstractmethod
    def detect(self, project_path: Path) -> bool:
        """Return True if this framework is detected in project_path."""
        pass

    @abstractmethod
    def get_framework_info(self, project_path: Path) -> Dict[str, Any]:
        """Return metadata regarding the framework, dependencies, package managers."""
        pass

    def build(self, project_path: Path) -> Dict[str, Any]:
        """Run framework build/compilation check. Default is no-op success."""
        return {"success": True, "logs": "No build step required."}

    def test(self, project_path: Path) -> Dict[str, Any]:
        """Run backend test suite."""
        return {"success": True, "logs": "No automated test suite configured.", "passed": True}

    def get_run_command(self, project_path: Path) -> str:
        """Return PowerShell command string to start the dev server."""
        return ""

    def get_dev_port(self) -> int:
        """Return default port for browser/API validation."""
        return self.default_port
