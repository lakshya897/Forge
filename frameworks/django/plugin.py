"""Django Framework Plugin for AutonomousAI."""

from pathlib import Path
from typing import Any, Dict
import subprocess
from frameworks.base import BaseFrameworkPlugin


class DjangoFrameworkPlugin(BaseFrameworkPlugin):
    name = "django"
    priority = 85
    default_port = 8000

    def detect(self, project_path: Path) -> bool:
        return (project_path / "manage.py").exists()

    def get_framework_info(self, project_path: Path) -> Dict[str, Any]:
        return {
            "framework": "Django",
            "package_manager": "pip",
            "build_command": "python manage.py check",
            "test_command": "python manage.py test",
            "dev_command": "python manage.py runserver 8000",
            "dev_port": self.default_port,
        }

    def build(self, project_path: Path) -> Dict[str, Any]:
        import sys
        try:
            res = subprocess.run(
                [sys.executable, "manage.py", "check"],
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
                [sys.executable, "manage.py", "test"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120,
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
        return f"{sys.executable} manage.py runserver 8000"
