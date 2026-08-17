"""
Windows Terminal & PowerShell Execution Tools for AutonomousAI.
Provides native Windows PowerShell/CMD process execution, port discovery, and process cleanup.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import subprocess
import socket
import httpx
import re
from pydantic import BaseModel, Field
from tools.base import BaseTool
from utils.config import settings


class PowerShellTool(BaseTool):
    """Tool to execute commands in native Windows PowerShell."""

    def __init__(self):
        super().__init__(
            name="run_powershell",
            description="Executes a PowerShell command in the specified working directory.",
        )

    def execute(self, command: str, cwd: Optional[str] = None, timeout: int = 60, **kwargs: Any) -> Dict[str, Any]:
        target_cwd = cwd or str(settings.workspace_root)
        try:
            # Use powershell.exe with NonInteractive mode
            cmd = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", command]
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
            return {"success": False, "exit_code": -1, "error": f"Command timed out after {timeout} seconds."}
        except Exception as e:
            return {"success": False, "exit_code": -1, "error": str(e)}


class PortCheckTool(BaseTool):
    """Tool to check if a TCP port is open and responding."""

    def __init__(self):
        super().__init__(
            name="check_port",
            description="Checks if a local port (e.g. 3000, 5173, 8000) is open and optionally checks HTTP 200.",
        )

    def execute(self, port: int, check_http: bool = True, host: str = "127.0.0.1", timeout: float = 0.5, **kwargs: Any) -> Dict[str, Any]:
        # 1. TCP socket test
        is_open = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                is_open = True

        if not is_open:
            return {"success": True, "is_open": False, "http_status": None, "port": port}

        # 2. HTTP test
        http_status = None
        if check_http:
            url = f"http://{host}:{port}/"
            try:
                with httpx.Client(timeout=timeout) as client:
                    r = client.get(url, follow_redirects=True)
                    http_status = r.status_code
            except Exception:
                pass

        return {
            "success": True,
            "is_open": True,
            "http_status": http_status,
            "port": port,
            "url": f"http://{host}:{port}/",
        }


class KillPortTool(BaseTool):
    """Tool to terminate any Windows process holding a target port."""

    def __init__(self):
        super().__init__(
            name="kill_port",
            description="Terminates any process occupying a target TCP port on Windows.",
        )

    def execute(self, port: int, **kwargs: Any) -> Dict[str, Any]:
        killed_pids = []
        try:
            # Run netstat -ano to find PID
            res = subprocess.run(
                ["netstat", "-ano", "-p", "TCP"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in res.stdout.splitlines():
                if f":{port} " in line and "LISTENING" in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) > 0:
                        subprocess.run(
                            ["taskkill", "/F", "/PID", pid],
                            capture_output=True,
                            timeout=5,
                        )
                        killed_pids.append(int(pid))

            return {"success": True, "port": port, "killed_pids": killed_pids}
        except Exception as e:
            return {"success": False, "error": str(e)}
