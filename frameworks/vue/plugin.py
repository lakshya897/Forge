"""Vue.js Framework Plugin for AutonomousAI."""

from pathlib import Path
from typing import Any, Dict
import json
import subprocess
from frameworks.base import BaseFrameworkPlugin


class VueFrameworkPlugin(BaseFrameworkPlugin):
    name = "vue"
    priority = 80
    default_port = 5173

    def detect(self, project_path: Path) -> bool:
        if (project_path / "src" / "App.vue").exists() or (project_path / "vue.config.js").exists():
            return True
        pkg = project_path / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = data.get("dependencies", {})
                return "vue" in deps
            except Exception:
                pass
        return False

    def get_framework_info(self, project_path: Path) -> Dict[str, Any]:
        return {
            "framework": "Vue.js",
            "package_manager": "npm",
            "build_command": "npm run build",
            "test_command": "npm test",
            "dev_command": "npm run dev",
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
