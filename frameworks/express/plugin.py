"""Express.js Framework Plugin for AutonomousAI."""

from pathlib import Path
from typing import Any, Dict
import json
import subprocess
from frameworks.base import BaseFrameworkPlugin


class ExpressFrameworkPlugin(BaseFrameworkPlugin):
    name = "express"
    priority = 70
    default_port = 3000

    def detect(self, project_path: Path) -> bool:
        pkg = project_path / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = data.get("dependencies", {})
                return "express" in deps
            except Exception:
                pass
        return False

    def get_framework_info(self, project_path: Path) -> Dict[str, Any]:
        return {
            "framework": "Express.js",
            "package_manager": "npm",
            "build_command": None,
            "test_command": "npm test",
            "dev_command": "npm start",
            "dev_port": self.default_port,
        }

    def get_run_command(self, project_path: Path) -> str:
        return "npm start"
