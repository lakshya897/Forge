"""
Pydantic Structured Output Models for all AutonomousAI Agents.
Guarantees strict schema adherence and zero plain-text parsing crashes.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from .state import Task


class ProductOwnerOutput(BaseModel):
    """Output from Product Owner Agent."""
    goal: str = Field(..., description="Refined, unambiguous specification of the goal")
    constraints: List[str] = Field(default_factory=list, description="Explicit technical and operational constraints")
    acceptance_tests: List[str] = Field(..., description="List of concrete, testable acceptance criteria")
    notes: Optional[str] = Field(default=None, description="Additional context or background memory")


class PlannerOutput(BaseModel):
    """Output from Planner Agent."""
    tasks: List[Task] = Field(..., description="Ordered list of atomic tasks")
    estimated_files: List[str] = Field(default_factory=list, description="List of all files expected to be touched")
    risk_level: Literal["low", "medium", "high"] = Field(default="medium", description="Estimated risk of modifications")
    execution_order: List[str] = Field(default_factory=list, description="Ordered list of task IDs")


class ArchitectOutput(BaseModel):
    """Output from Architect Agent."""
    routing_map: Dict[str, str] = Field(default_factory=dict, description="URL path to component/handler mapping")
    component_tree: Dict[str, List[str]] = Field(default_factory=dict, description="Parent to child component hierarchy")
    backend_endpoints: List[Dict[str, str]] = Field(default_factory=list, description="HTTP Method, Path, and Handlers")
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict, description="File to imported files mapping")
    notes: str = Field(default="", description="Architectural design observations and constraints")


class ImplementerOutput(BaseModel):
    """Output from Implementer Agent."""
    modified_files: List[str] = Field(default_factory=list, description="Files updated")
    created_files: List[str] = Field(default_factory=list, description="New files created")
    changes_summary: str = Field(..., description="Summary of applied AST and code changes")
    status: Literal["success", "partial", "failed"] = Field(default="success", description="Implementation status")


class ReviewerIssue(BaseModel):
    """Code review finding."""
    file_path: str
    line_number: Optional[int] = None
    severity: Literal["critical", "warning", "info"] = "warning"
    issue_type: Literal["bug", "smell", "duplicate_logic", "performance", "naming", "architecture"]
    description: str
    suggestion: str


class ReviewerOutput(BaseModel):
    """Output from Reviewer Agent."""
    passed: bool = Field(..., description="True if 0 critical issues found")
    critical_count: int = Field(default=0)
    warning_count: int = Field(default=0)
    issues: List[ReviewerIssue] = Field(default_factory=list)
    summary: str = Field(default="")


class SecurityVulnerability(BaseModel):
    """Security scanner finding."""
    vulnerability_type: Literal["sqli", "xss", "secret_leak", "unsafe_eval", "unsafe_subprocess", "insecure_deserialization", "other"]
    severity: Literal["critical", "high", "medium", "low"]
    file_path: str
    line_number: Optional[int] = None
    description: str
    remediation: str


class SecurityReport(BaseModel):
    """Output from Security Agent."""
    passed: bool = Field(..., description="True if 0 critical and 0 high vulnerabilities found")
    critical_count: int = Field(default=0)
    high_count: int = Field(default=0)
    vulnerabilities: List[SecurityVulnerability] = Field(default_factory=list)
    summary: str = Field(default="")


class DevOpsOutput(BaseModel):
    """Output from DevOps Agent."""
    build_passed: bool
    missing_dependencies: List[str] = Field(default_factory=list)
    install_commands: List[str] = Field(default_factory=list)
    logs: str = Field(default="")
    server_port: Optional[int] = None
    server_pid: Optional[int] = None


class BackendTestOutput(BaseModel):
    """Output from Backend Tester Agent."""
    passed: bool
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_log: str = Field(default="")
    api_endpoints_tested: List[str] = Field(default_factory=list)


class BrowserTestOutput(BaseModel):
    """Output from Browser Tester Agent."""
    passed: bool
    localhost_url: Optional[str] = None
    console_errors: List[str] = Field(default_factory=list)
    network_errors: List[str] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    dom_assertions_passed: List[str] = Field(default_factory=list)
    dom_assertions_failed: List[str] = Field(default_factory=list)
    failure_report_path: Optional[str] = None


class EvaluatorOutput(BaseModel):
    """Output from Evaluator Agent."""
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    acceptance_passed: bool = Field(..., description="True if all acceptance criteria are validated")
    passed_criteria: List[str] = Field(default_factory=list)
    failed_criteria: List[str] = Field(default_factory=list)
    remaining_issues: List[str] = Field(default_factory=list)
    recommendation: Literal["approve", "revise", "abort"] = "revise"


class FeedbackOutput(BaseModel):
    """Output from Feedback Agent for the next iteration loop."""
    root_causes: List[str] = Field(default_factory=list, description="Identified root causes of failure")
    targeted_fixes: List[str] = Field(default_factory=list, description="Specific instructions for Implementer")
    prioritized_tasks: List[str] = Field(default_factory=list, description="Ordered list of fix priorities")
    loop_decision: Literal["retry", "abort", "approve"] = "retry"
