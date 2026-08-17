"""
Base Tool Interface for AutonomousAI Extensible Tool Registry.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field


class BaseTool(ABC):
    """Abstract base class for all tools in AutonomousAI."""

    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Human-readable description of what the tool does")
    args_schema: Optional[Type[BaseModel]] = None

    def __init__(self, name: str, description: str, args_schema: Optional[Type[BaseModel]] = None):
        self.name = name
        self.description = description
        self.args_schema = args_schema

    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Synchronously execute tool logic."""
        pass

    async def aexecute(self, **kwargs: Any) -> Dict[str, Any]:
        """Asynchronously execute tool logic (default falls back to sync)."""
        return self.execute(**kwargs)
