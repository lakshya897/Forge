"""
Ollama Model Implementation for Qwen 2.5 7B (Reasoning & Planning).
"""

from typing import Optional, Type, TypeVar
import json
import httpx
from pydantic import BaseModel
from .base import BaseModelWrapper
from tools.json.json_repair import JSONRepairEngine
from utils.config import settings

T = TypeVar("T", bound=BaseModel)


class Qwen7BModel(BaseModelWrapper):
    """Qwen 2.5 7B model wrapper tailored for reasoning, planning, and evaluation."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        host: Optional[str] = None,
        timeout: int = 120,
    ):
        model_name = model_name or settings.model_reasoning
        super().__init__(model_name, temperature, timeout)
        self.host = (host or settings.ollama_host).rstrip("/")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.host}/api/generate", json=payload)
                res.raise_for_status()
                return res.json().get("response", "")
        except Exception:
            return ""

    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.host}/api/generate", json=payload)
                res.raise_for_status()
                return res.json().get("response", "")
        except Exception:
            return ""

    def generate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None
    ) -> T:
        schema_json = json.dumps(schema_cls.model_json_schema(), indent=2)
        full_system = (
            (system_prompt or "")
            + "\n\nYou MUST respond strictly in valid JSON matching this exact JSON Schema:\n"
            + schema_json
        )
        response_text = self.generate(prompt, full_system)
        return JSONRepairEngine.parse_to_schema(response_text, schema_cls)

    async def agenerate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None
    ) -> T:
        schema_json = json.dumps(schema_cls.model_json_schema(), indent=2)
        full_system = (
            (system_prompt or "")
            + "\n\nYou MUST respond strictly in valid JSON matching this exact JSON Schema:\n"
            + schema_json
        )
        response_text = await self.agenerate(prompt, full_system)
        return JSONRepairEngine.parse_to_schema(response_text, schema_cls)
