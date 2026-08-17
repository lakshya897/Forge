"""
Process Runner for Windows Subprocess Execution in AutonomousAI.
Provides async/sync PowerShell and CMD runners with timeout and output capture.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import subprocess
import asyncio
from utils.config import settings


class ProcessRunner:
    """Helper to run synchronous and asynchronous shell commands on Windows."""

    @staticmethod
    def run_command(
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 60,
        use_powershell: bool = True,
    ) -> Dict[str, Any]:
        """Execute command synchronously."""
        target_cwd = cwd or str(settings.workspace_root)
        if use_powershell:
            cmd = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", command]
        else:
            cmd = ["cmd.exe", "/c", command]

        try:
            res = subprocess.run(
                cmd,
                cwd=target_cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "exit_code": -1, "error": f"Execution timed out ({timeout}s)"}
        except Exception as e:
            return {"success": False, "exit_code": -1, "error": str(e)}

    @staticmethod
    async def arun_command(
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Execute command asynchronously."""
        target_cwd = cwd or str(settings.workspace_root)
        cmd = f'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "{command}"'

        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                cwd=target_cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {
                "success": proc.returncode == 0,
                "exit_code": proc.returncode,
                "stdout": stdout.decode("utf-8", errors="replace").strip(),
                "stderr": stderr.decode("utf-8", errors="replace").strip(),
            }
        except asyncio.TimeoutError:
            return {"success": False, "exit_code": -1, "error": f"Execution timed out ({timeout}s)"}
        except Exception as e:
            return {"success": False, "exit_code": -1, "error": str(e)}
