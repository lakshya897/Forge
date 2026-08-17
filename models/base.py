"""
Base Model Wrapper Interface for AutonomousAI.
Provides unified sync/async generation and structured schema validation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseModelWrapper(ABC):
    """Abstract base class for all LLM providers in AutonomousAI."""

    def __init__(self, model_name: str, temperature: float = 0.2, timeout: int = 120):
        self.model_name = model_name
        self.temperature = temperature
        self.timeout = timeout

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Synchronously generate text response."""
        pass

    @abstractmethod
    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Asynchronously generate text response."""
        pass

    @abstractmethod
    def generate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None
    ) -> T:
        """Synchronously generate and parse response into validated Pydantic model."""
        pass

    @abstractmethod
    async def agenerate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None
    ) -> T:
        """Asynchronously generate and parse response into validated Pydantic model."""
        pass
