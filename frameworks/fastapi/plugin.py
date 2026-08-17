"""FastAPI Framework Plugin for AutonomousAI."""

from pathlib import Path
from typing import Any, Dict
import subprocess
from frameworks.base import BaseFrameworkPlugin


class FastAPIFrameworkPlugin(BaseFrameworkPlugin):
    name = "fastapi"
    priority = 85
    default_port = 8000

    def detect(self, project_path: Path) -> bool:
        # Check requirements.txt or pyproject.toml
        req = project_path / "requirements.txt"
        if req.exists():
            try:
                content = req.read_text(encoding="utf-8")
                if "fastapi" in content.lower():
                    return True
            except Exception:
                pass

        # Check python source files
        for py_file in project_path.glob("*.py"):
            try:
                txt = py_file.read_text(encoding="utf-8")
                if "from fastapi import" in txt or "import fastapi" in txt or "FastAPI()" in txt:
                    return True
            except Exception:
                pass

        return False

    def get_framework_info(self, project_path: Path) -> Dict[str, Any]:
        return {
            "framework": "FastAPI",
            "package_manager": "pip",
            "build_command": "python -m compileall .",
            "test_command": "pytest",
            "dev_command": "uvicorn main:app --reload --port 8000",
            "dev_port": self.default_port,
        }

    def build(self, project_path: Path) -> Dict[str, Any]:
        import sys
        try:
            res = subprocess.run(
                [sys.executable, "-m", "compileall", "."],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {"success": res.returncode == 0, "logs": res.stdout + "\n" + res.stderr}
        except Exception as e:
            return {"success": False, "logs": str(e)}

    def test(self, project_path: Path) -> Dict[str, Any]:
        import sys
        try:
            res = subprocess.run(
                [sys.executable, "-m", "pytest"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {
                "success": res.returncode == 0,
                "passed": res.returncode == 0,
                "logs": res.stdout + "\n" + res.stderr,
            }
        except Exception as e:
            return {"success": False, "passed": False, "logs": str(e)}

    def get_run_command(self, project_path: Path) -> str:
        import sys
        if (project_path / "app.py").exists():
            return f"{sys.executable} -m uvicorn app:app --port 8000"
        return f"{sys.executable} -m uvicorn main:app --port 8000"
