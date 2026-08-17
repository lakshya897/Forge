"""
Extensible Tool Registry for AutonomousAI.
Provides centralized registration, discovery, and execution of tools.
"""

from typing import Dict, Any, List, Optional
from .base import BaseTool


class ToolRegistry:
    """Central registry holding all operational tools."""

    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        """Register a tool instance."""
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        """Retrieve tool by name."""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[Dict[str, str]]:
        """List all registered tools with descriptions."""
        return [{"name": t.name, "description": t.description} for t in cls._tools.values()]

    @classmethod
    def execute(cls, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute tool synchronously by name."""
        tool = cls.get(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not found in registry."}
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    async def aexecute(cls, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute tool asynchronously by name."""
        tool = cls.get(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not found in registry."}
        try:
            return await tool.aexecute(**kwargs)
        except Exception as e:
            return {"success": False, "error": str(e)}
