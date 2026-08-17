"""Spring Boot Framework Plugin for AutonomousAI."""

from pathlib import Path
from typing import Any, Dict
import subprocess
from frameworks.base import BaseFrameworkPlugin


class SpringFrameworkPlugin(BaseFrameworkPlugin):
    name = "spring"
    priority = 75
    default_port = 8080

    def detect(self, project_path: Path) -> bool:
        return (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists()

    def get_framework_info(self, project_path: Path) -> Dict[str, Any]:
        is_maven = (project_path / "pom.xml").exists()
        return {
            "framework": "Spring Boot",
            "package_manager": "maven" if is_maven else "gradle",
            "build_command": "mvn compile" if is_maven else "./gradlew build",
            "test_command": "mvn test" if is_maven else "./gradlew test",
            "dev_command": "mvn spring-boot:run" if is_maven else "./gradlew bootRun",
            "dev_port": self.default_port,
        }

    def build(self, project_path: Path) -> Dict[str, Any]:
        is_maven = (project_path / "pom.xml").exists()
        cmd = ["mvn.cmd", "compile"] if is_maven else ["gradlew.bat", "build"]
        try:
            res = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, timeout=180)
            return {"success": res.returncode == 0, "logs": res.stdout + "\n" + res.stderr}
        except Exception as e:
            return {"success": False, "logs": str(e)}

    def get_run_command(self, project_path: Path) -> str:
        if (project_path / "pom.xml").exists():
            return "mvn spring-boot:run"
        return "./gradlew bootRun"
