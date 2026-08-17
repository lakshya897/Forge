import sys
import os

# Ensure Windows stdout supports UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text

console = Console(highlight=False)


class ConsoleDashboard:
    """Rich UI manager for streaming logs, agent status cards, and iteration summaries."""

    @staticmethod
    def banner() -> None:
        """Display the AutonomousAI startup banner."""
        banner_text = """
 [bold cyan]============================================================[/bold cyan]
 [bold white]         AutonomousAI — Local Multi-Agent Engineer         [/bold white]
 [bold cyan]============================================================[/bold cyan]
  [green]Runtime:[/green] Windows 11 Native       [green]LLM:[/green] Ollama (Local)
  [green]Storage:[/green] D:\\ Drive Strictly     [green]Framework:[/green] LangGraph
"""
        console.print(Panel(banner_text.strip(), border_style="cyan"))

    @staticmethod
    def agent_start(agent_name: str, message: str) -> None:
        """Log the start of an agent's execution."""
        console.print(f"[bold yellow]▶ [{agent_name}][/bold yellow] [dim]{message}[/dim]")

    @staticmethod
    def agent_success(agent_name: str, message: str) -> None:
        """Log successful completion of an agent step."""
        console.print(f"[bold green]✔ [{agent_name}][/bold green] {message}")

    @staticmethod
    def agent_warning(agent_name: str, message: str) -> None:
        """Log a warning or non-critical finding."""
        console.print(f"[bold yellow]⚠ [{agent_name}][/bold yellow] [yellow]{message}[/yellow]")

    @staticmethod
    def agent_failure(agent_name: str, message: str) -> None:
        """Log an agent failure or test break."""
        console.print(f"[bold red]✖ [{agent_name}][/bold red] [red]{message}[/red]")

    @staticmethod
    def show_tasks(tasks: List[Any]) -> None:
        """Render ordered tasks table."""
        table = Table(title="Execution Plan Tasks", border_style="cyan")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Title", style="bold white")
        table.add_column("Target Files", style="cyan")
        table.add_column("Status", style="green")

        for t in tasks:
            if isinstance(t, dict):
                task_id = str(t.get("id", ""))
                title = str(t.get("title", ""))
                t_files = t.get("target_files", [])
                target_files = ", ".join(t_files) if isinstance(t_files, list) else str(t_files)
                status = str(t.get("status", "pending"))
            else:
                task_id = str(getattr(t, "id", ""))
                title = str(getattr(t, "title", ""))
                t_files = getattr(t, "target_files", [])
                target_files = ", ".join(t_files) if isinstance(t_files, list) else str(t_files)
                status = str(getattr(t, "status", "pending"))
            table.add_row(task_id, title, target_files, status)

        console.print(table)

    @staticmethod
    def show_relevance_scores(scored_files: List[Dict[str, Any]]) -> None:
        """Render file relevance scoring table from Context Manager."""
        table = Table(title="Context Manager: Ranked Relevant Files", border_style="blue")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("File Path", style="bold white")
        table.add_column("Score", style="magenta")
        table.add_column("Reason", style="dim")

        for idx, item in enumerate(scored_files[:15], start=1):
            table.add_row(
                str(idx),
                item.get("path", ""),
                f"{item.get('score', 0.0):.2f}",
                item.get("reason", "AST / Keyword match"),
            )

        console.print(table)

    @staticmethod
    def show_iteration_summary(
        iteration: int,
        confidence: float,
        tests_passed: bool,
        review_passed: bool,
        security_passed: bool,
    ) -> None:
        """Display an iteration completion card."""
        status_text = (
            f"[bold]Iteration:[/bold] {iteration}\n"
            f"[bold]Confidence Score:[/bold] {confidence:.2f} / 1.00\n"
            f"[bold]Backend Tests:[/bold] {'[green]PASSED[/green]' if tests_passed else '[red]FAILED[/red]'}\n"
            f"[bold]Code Review:[/bold] {'[green]CLEAN[/green]' if review_passed else '[yellow]ISSUES[/yellow]'}\n"
            f"[bold]Security Audit:[/bold] {'[green]PASSED[/green]' if security_passed else '[red]VULNERABILITIES[/red]'}"
        )
        style = "green" if (confidence >= 0.90 and tests_passed and review_passed and security_passed) else "yellow"
        console.print(Panel(status_text, title=f"Iteration {iteration} Result", border_style=style))

    @staticmethod
    def show_diff(diff_text: str, filename: str = "changes.diff") -> None:
        """Display colorized unified diff."""
        if not diff_text.strip():
            return
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title=f"Diff: {filename}", border_style="dim"))

    @staticmethod
    def show_benchmark_table(results: List[Dict[str, Any]]) -> None:
        """Display benchmark results table."""
        table = Table(title="AutonomousAI Benchmark Report", border_style="magenta")
        table.add_column("Benchmark Target", style="bold white")
        table.add_column("Planning Time", style="cyan")
        table.add_column("Implementation", style="cyan")
        table.add_column("Tests Time", style="cyan")
        table.add_column("Total Time", style="yellow")
        table.add_column("Status", style="bold green")

        for r in results:
            table.add_row(
                r.get("target", ""),
                f"{r.get('plan_s', 0.0):.1f}s",
                f"{r.get('impl_s', 0.0):.1f}s",
                f"{r.get('test_s', 0.0):.1f}s",
                f"{r.get('total_s', 0.0):.1f}s",
                "[green]PASSED[/green]" if r.get("passed", False) else "[red]FAILED[/red]",
            )

        console.print(table)
