"""
Centralized Model Manager for AutonomousAI.
Provides singleton model instance resolution, graceful fallback, and mock support.
"""

from typing import Dict, Optional
import httpx
from .base import BaseModelWrapper
from .qwen7b import Qwen7BModel
from .qwen14b import Qwen14BCoderModel
from .mock_model import MockModelWrapper
from .registry import ROLE_MODEL_MAPPING
from utils.config import settings


class ModelManager:
    """Central singleton manager for obtaining role-specific LLM wrappers."""

    _instances: Dict[str, BaseModelWrapper] = {}
    _force_mock: bool = False

    @classmethod
    def set_mock_mode(cls, enabled: bool) -> None:
        """Enable or disable global mock mode for testing."""
        cls._force_mock = enabled
        cls._instances.clear()  # Clear cache so new mode takes effect

    @classmethod
    def is_ollama_alive(cls) -> bool:
        """Check if local Ollama daemon is reachable."""
        if cls._force_mock:
            return False
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{settings.ollama_host.rstrip('/')}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    @classmethod
    def get(cls, role: str) -> BaseModelWrapper:
        """
        Retrieve configured model wrapper for a given agent role.
        Automatically falls back to MockModelWrapper if Ollama is unreachable.
        """
        role = role.lower()
        if role in cls._instances:
            return cls._instances[role]

        # Check if mock mode is forced or Ollama is offline
        if cls._force_mock or not cls.is_ollama_alive():
            instance = MockModelWrapper(model_name=f"mock-{role}")
            cls._instances[role] = instance
            return instance

        config = ROLE_MODEL_MAPPING.get(role, {"type": "14b", "temperature": 0.1})
        model_type = config.get("type", "14b")
        temp = config.get("temperature", 0.1)

        if model_type == "7b":
            instance = Qwen7BModel(model_name=settings.model_reasoning, temperature=temp)
        else:
            instance = Qwen14BCoderModel(model_name=settings.model_coding, temperature=temp)

        cls._instances[role] = instance
        return instance
