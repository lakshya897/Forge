"""
Mock LLM Provider for offline testing, dry-runs, and instant test verification.
"""

from typing import Optional, Type, TypeVar, Any, Dict
from pydantic import BaseModel
import time
from .base import BaseModelWrapper
from schemas.outputs import (
    ProductOwnerOutput,
    PlannerOutput,
    ArchitectOutput,
    ImplementerOutput,
    ReviewerOutput,
    ReviewerIssue,
    SecurityReport,
    SecurityVulnerability,
    DevOpsOutput,
    BackendTestOutput,
    BrowserTestOutput,
    EvaluatorOutput,
    FeedbackOutput,
)
from schemas.state import Task

T = TypeVar("T", bound=BaseModel)


class MockModelWrapper(BaseModelWrapper):
    """Deterministic offline model simulator for testing and dry-runs."""

    def __init__(self, model_name: str = "mock-model", temperature: float = 0.0):
        super().__init__(model_name, temperature)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"[Mock Response for prompt: {prompt[:50]}...]"

    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self.generate(prompt, system_prompt)

    def generate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None
    ) -> T:
        """Synthesize valid structured mock output based on requested schema."""
        if schema_cls == ProductOwnerOutput:
            return ProductOwnerOutput(
                goal="Implement feature as specified in the requirements.",
                constraints=["Windows native", "No paid APIs", "Clean modular structure"],
                acceptance_tests=[
                    "Application builds successfully without errors",
                    "Required API endpoints respond with HTTP 200",
                    "Frontend UI displays required components",
                ],
                notes="Automated Product Owner specification.",
            ) # type: ignore

        if schema_cls == PlannerOutput:
            return PlannerOutput(
                tasks=[
                    Task(
                        id="task_1",
                        title="Setup core endpoints and components",
                        description="Implement requested routes and state handlers.",
                        target_files=["main.py", "app.py"],
                    ),
                    Task(
                        id="task_2",
                        title="Add UI views and styling",
                        description="Update frontend components and styling.",
                        target_files=["index.html", "src/App.tsx"],
                        dependencies=["task_1"],
                    ),
                    Task(
                        id="task_3",
                        title="Verify and test integration",
                        description="Validate end-to-end functionality.",
                        target_files=["tests/test_app.py"],
                        dependencies=["task_2"],
                    ),
                ],
                estimated_files=["main.py", "src/App.tsx"],
                risk_level="low",
                execution_order=["task_1", "task_2", "task_3"],
            ) # type: ignore

        if schema_cls == ArchitectOutput:
            return ArchitectOutput(
                routing_map={"/": "HomeComponent", "/api/health": "HealthEndpoint"},
                component_tree={"App": ["Header", "MainView", "Footer"]},
                backend_endpoints=[{"method": "GET", "path": "/api/health", "handler": "health_check"}],
                dependency_graph={"main.py": ["fastapi", "uvicorn"]},
                notes="Standard modular architecture.",
            ) # type: ignore

        if schema_cls == ImplementerOutput:
            return ImplementerOutput(
                modified_files=["main.py"],
                created_files=[],
                changes_summary="Applied AST transformations and updated route handlers.",
                status="success",
            ) # type: ignore

        if schema_cls == ReviewerOutput:
            return ReviewerOutput(
                passed=True,
                critical_count=0,
                warning_count=0,
                issues=[],
                summary="Code quality review passed cleanly. No critical smells.",
            ) # type: ignore

        if schema_cls == SecurityReport:
            return SecurityReport(
                passed=True,
                critical_count=0,
                high_count=0,
                vulnerabilities=[],
                summary="Security audit passed with 0 vulnerabilities.",
            ) # type: ignore

        if schema_cls == EvaluatorOutput:
            return EvaluatorOutput(
                confidence=0.95,
                acceptance_passed=True,
                passed_criteria=["Build successful", "APIs healthy", "UI elements rendered"],
                failed_criteria=[],
                remaining_issues=[],
                recommendation="approve",
            ) # type: ignore

        if schema_cls == FeedbackOutput:
            return FeedbackOutput(
                root_causes=[],
                targeted_fixes=[],
                prioritized_tasks=[],
                loop_decision="approve",
            ) # type: ignore

        # Generic fallback
        return schema_cls.model_construct()

    async def agenerate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None
    ) -> T:
        return self.generate_structured(prompt, schema_cls, system_prompt)
