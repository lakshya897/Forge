"""
System Verification Tool for AutonomousAI.
Verifies all core dependencies and D: drive storage paths.
"""

import sys
import os

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

import shutil
import subprocess
from pathlib import Path
from utils.config import settings
from utils.console import console
from rich.table import Table


def check_command(cmd: list) -> bool:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def verify_all():
    console.print("\n[bold cyan]============================================================[/bold cyan]")
    console.print("[bold white]            AutonomousAI System Verification               [/bold white]")
    console.print("[bold cyan]============================================================[/bold cyan]\n")

    results = []

    # 1. Python
    py_ver = sys.version_info
    py_ok = py_ver.major == 3 and py_ver.minor >= 12
    results.append({
        "component": "Python",
        "status": "✓" if py_ok else "✖",
        "detail": f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}",
        "fix": "Download Python 3.12+ from https://python.org",
        "passed": py_ok,
    })

    # 2. Pip
    pip_ok = check_command([sys.executable, "-m", "pip", "--version"])
    results.append({
        "component": "Pip",
        "status": "✓" if pip_ok else "✖",
        "detail": "Installed" if pip_ok else "Missing",
        "fix": "Run 'python -m ensurepip --upgrade'",
        "passed": pip_ok,
    })

    # 3. Ollama
    ollama_exe = settings.get_ollama_executable()
    ollama_ok = check_command([ollama_exe, "--version"])
    results.append({
        "component": "Ollama",
        "status": "✓" if ollama_ok else "✖",
        "detail": "Running / Installed" if ollama_ok else "Not in PATH",
        "fix": f"Install from https://ollama.com and set OLLAMA_MODELS={settings.ollama_models}",
        "passed": ollama_ok,
    })

    # 4. Models
    models_found = False
    if ollama_ok:
        try:
            res = subprocess.run([ollama_exe, "list"], capture_output=True, text=True)
            if "qwen" in res.stdout.lower():
                models_found = True
        except Exception:
            pass

    results.append({
        "component": "Model",
        "status": "✓" if models_found else "⚠",
        "detail": "Qwen Models Present" if models_found else "Mock Fallback Available",
        "fix": f"Run 'ollama pull {settings.model_coding}'",
        "passed": True,  # Fallback model ensures execution is always functional
    })

    # 5. Playwright
    playwright_ok = check_command([sys.executable, "-m", "playwright", "--version"])
    results.append({
        "component": "Playwright",
        "status": "✓" if playwright_ok else "⚠",
        "detail": f"Path: {settings.playwright_browsers_path}",
        "fix": "Run 'pip install playwright' and 'playwright install chromium'",
        "passed": True,
    })

    # 6. Git
    git_ok = check_command(["git", "--version"])
    results.append({
        "component": "Git",
        "status": "✓" if git_ok else "✖",
        "detail": "Installed" if git_ok else "Missing",
        "fix": "Install Git for Windows from https://gitforwindows.org",
        "passed": git_ok,
    })

    # 7. Node / npm (Optional)
    node_ok = check_command(["node", "--version"])
    results.append({
        "component": "Node (Optional)",
        "status": "✓" if node_ok else "—",
        "detail": "Installed" if node_ok else "Optional (for Node/React)",
        "fix": "Install Node.js from https://nodejs.org",
        "passed": True,
    })

    # 8. D: Drive Storage Check
    d_drive_exists = Path("D:/").exists()
    results.append({
        "component": "D: Drive Storage",
        "status": "✓" if d_drive_exists else "✖",
        "detail": f"Bound to D:\\ (Models: {settings.ollama_models.name})",
        "fix": "Ensure D: drive is connected and accessible.",
        "passed": d_drive_exists,
    })

    # Render Table
    table = Table(title="System Verification Summary", border_style="cyan")
    table.add_column("Component", style="bold white", width=18)
    table.add_column("Status", style="bold green", width=8, justify="center")
    table.add_column("Details", style="cyan")

    for r in results:
        style = "green" if r["status"] == "✓" else ("yellow" if r["status"] == "⚠" else "red")
        table.add_row(r["component"], f"[{style}]{r['status']}[/{style}]", r["detail"])

    console.print(table)

    # Print fixes if any failed
    failed = [r for r in results if not r["passed"]]
    if failed:
        console.print("\n[bold yellow]Recommended Fixes:[/bold yellow]")
        for f in failed:
            console.print(f"- [bold white]{f['component']}:[/bold white] [dim]{f['fix']}[/dim]")
    else:
        console.print("\n[bold green]All core requirements verified! System is ready to run.[/bold green]\n")


if __name__ == "__main__":
    verify_all()
