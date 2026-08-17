"""React Framework Plugin for AutonomousAI."""

from pathlib import Path
from typing import Any, Dict
import json
import subprocess
from frameworks.base import BaseFrameworkPlugin


class ReactFrameworkPlugin(BaseFrameworkPlugin):
    name = "react"
    priority = 80
    default_port = 5173

    def detect(self, project_path: Path) -> bool:
        pkg = project_path / "package.json"
        if not pkg.exists():
            return False
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            # Must not be Next.js (Next has higher priority)
            if "next" in deps:
                return False
            return "react" in deps or "react-dom" in deps or "react" in dev_deps
        except Exception:
            return False

    def get_framework_info(self, project_path: Path) -> Dict[str, Any]:
        pkg = project_path / "package.json"
        scripts = {}
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                scripts = data.get("scripts", {})
            except Exception:
                pass
        return {
            "framework": "React",
            "package_manager": "npm",
            "build_command": "npm run build" if "build" in scripts else None,
            "test_command": "npm test" if "test" in scripts else None,
            "dev_command": "npm run dev" if "dev" in scripts else "npm start",
            "dev_port": self.default_port,
        }

    def build(self, project_path: Path) -> Dict[str, Any]:
        try:
            res = subprocess.run(
                ["npm.cmd", "run", "build"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {"success": res.returncode == 0, "logs": res.stdout + "\n" + res.stderr}
        except Exception as e:
            return {"success": False, "logs": str(e)}

    def get_run_command(self, project_path: Path) -> str:
        return "npm run dev"
