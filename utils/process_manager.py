"""
Process Manager for AutonomousAI.
Tracks all spawned development servers and background tasks, frees occupied ports,
and guarantees clean teardown on system exit.
"""

from typing import Dict, List, Optional
import subprocess
import atexit
import signal
import sys
import psutil
from tools.terminal.term_tools import PortCheckTool, KillPortTool
from schemas.state import ProcessRecord


class ProcessManager:
    """Singleton process lifecycle coordinator."""

    _active_processes: Dict[int, subprocess.Popen] = {}
    _tracked_ports: Dict[int, int] = {}  # port -> pid
    _port_tool = PortCheckTool()
    _kill_tool = KillPortTool()

    @classmethod
    def start_background_process(
        cls,
        command: str,
        cwd: str,
        port: Optional[int] = None,
    ) -> Optional[ProcessRecord]:
        """
        Start a background development server or daemon command.
        If a port is specified, frees the port first.
        """
        if port:
            cls.free_port(port)

        try:
            # On Windows, create new process group
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith("win") else 0
            proc = subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-Command", command],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creationflags,
            )

            cls._active_processes[proc.pid] = proc
            if port:
                cls._tracked_ports[port] = proc.pid

            return ProcessRecord(
                pid=proc.pid,
                command=command,
                port=port,
                status="running",
            )
        except Exception:
            return None

    @classmethod
    def free_port(cls, port: int) -> bool:
        """Terminate any existing process using the port."""
        res = cls._kill_tool.execute(port=port)
        if port in cls._tracked_ports:
            del cls._tracked_ports[port]
        return res.get("success", False)

    @classmethod
    def stop_process(cls, pid: int) -> None:
        """Gracefully terminate a specific PID and its children."""
        if pid in cls._active_processes:
            proc = cls._active_processes.pop(pid)
            try:
                # Terminate children first using psutil if available
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    @classmethod
    def cleanup_all(cls) -> None:
        """Teardown all spawned servers and background tasks."""
        pids = list(cls._active_processes.keys())
        for pid in pids:
            cls.stop_process(pid)

        # Free all tracked ports
        ports = list(cls._tracked_ports.keys())
        for port in ports:
            cls.free_port(port)


# Register automatic shutdown hooks
atexit.register(ProcessManager.cleanup_all)
