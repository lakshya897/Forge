"""
Persistent Long-Term Memory Manager for AutonomousAI.
Stores cross-iteration and cross-session knowledge in memory/project_memory.json.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from utils.config import settings


class ProjectMemory:
    """Manages persistent project memory JSON."""

    @classmethod
    def _get_memory_file(cls) -> Path:
        mem_dir = settings.memory_dir
        mem_dir.mkdir(parents=True, exist_ok=True)
        return mem_dir / "project_memory.json"

    @classmethod
    def load(cls) -> Dict[str, Any]:
        """Load persistent memory from disk."""
        f = cls._get_memory_file()
        if not f.exists():
            return {
                "previous_failures": [],
                "successful_fixes": [],
                "architecture_summary": {},
                "user_constraints": [],
            }
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @classmethod
    def save(cls, data: Dict[str, Any]) -> None:
        """Save persistent memory to disk."""
        f = cls._get_memory_file()
        try:
            f.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def record_success(cls, goal: str, modified_files: List[str]) -> None:
        """Record successful implementation into memory."""
        mem = cls.load()
        fixes = mem.get("successful_fixes", [])
        fixes.append({"goal": goal, "modified_files": modified_files})
        mem["successful_fixes"] = fixes[-20:]
        cls.save(mem)
