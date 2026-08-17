"""
JSON Repair and Parsing Utilities for AutonomousAI.
Robustly repairs malformed, truncated, or markdown-wrapped LLM JSON outputs.
"""

from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel
import json
import re
import ast

T = TypeVar("T", bound=BaseModel)


class JSONRepairEngine:
    """Deterministic JSON extraction, repair, and Pydantic validation."""

    @staticmethod
    def extract_raw_json(text: str) -> str:
        """Extract the most likely JSON substring from text containing markdown or preambles."""
        if not text:
            return "{}"

        text = text.strip()

        # Check for ```json ... ``` blocks
        json_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if json_block_match:
            candidate = json_block_match.group(1).strip()
            if (candidate.startswith("{") and candidate.endswith("}")) or (
                candidate.startswith("[") and candidate.endswith("]")
            ):
                return candidate

        # Find first { or [ and matching last } or ]
        first_brace = text.find("{")
        first_bracket = text.find("[")

        start_idx = -1
        is_object = True

        if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
            start_idx = first_brace
            is_object = True
        elif first_bracket != -1:
            start_idx = first_bracket
            is_object = False

        if start_idx == -1:
            return text

        if is_object:
            end_idx = text.rfind("}")
        else:
            end_idx = text.rfind("]")

        if end_idx != -1 and end_idx >= start_idx:
            return text[start_idx : end_idx + 1]

        return text[start_idx:]

    @classmethod
    def repair(cls, raw_text: str) -> Dict[str, Any]:
        """
        Attempt to parse and repair broken JSON strings using multi-stage heuristics.
        """
        cleaned = cls.extract_raw_json(raw_text)

        # Stage 1: Standard JSON parse
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Stage 2: Remove trailing commas
        cleaned_no_trailing = re.sub(r",\s*([\]}])", r"\1", cleaned)
        try:
            return json.loads(cleaned_no_trailing)
        except Exception:
            pass

        # Stage 3: Replace single quotes with double quotes safely using python AST literal eval
        try:
            val = ast.literal_eval(cleaned)
            if isinstance(val, (dict, list)):
                return val if isinstance(val, dict) else {"items": val}
        except Exception:
            pass

        # Stage 4: Fix unescaped newlines inside strings
        fixed_newlines = re.sub(r'(?<!\\)\n', r'\\n', cleaned)
        try:
            return json.loads(fixed_newlines)
        except Exception:
            pass

        # Stage 5: Balance braces / brackets if truncated
        open_braces = cleaned.count("{") - cleaned.count("}")
        open_brackets = cleaned.count("[") - cleaned.count("]")

        balanced = cleaned
        if open_brackets > 0:
            balanced += "]" * open_brackets
        if open_braces > 0:
            balanced += "}" * open_braces

        balanced = re.sub(r",\s*([\]}])", r"\1", balanced)
        try:
            return json.loads(balanced)
        except Exception:
            pass

        # Stage 6: Fallback empty dict
        return {}

    @classmethod
    def parse_to_schema(cls, raw_text: str, schema_cls: Type[T]) -> T:
        """
        Parse raw LLM output directly into a validated Pydantic model.
        Falls back to model defaults if parsing fails completely.
        """
        data = cls.repair(raw_text)
        try:
            return schema_cls.model_validate(data)
        except Exception:
            # Fallback instantiation
            try:
                return schema_cls.model_validate({})
            except Exception:
                # If required fields exist, return minimally constructed instance
                return schema_cls.model_construct(**data)
