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

import subprocess
from pathlib import Path
from utils.config import settings
from utils.console import console

ROOT_DIR = Path(__file__).resolve().parent


def step_1_check_python() -> bool:
    console.print("\n[bold cyan]Step 1: Checking Python Version...[/bold cyan]")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        console.print("[bold red]Python 3.12+ is required.[/bold red]")
        console.print("Download from: [link=https://python.org]https://python.org[/link]")
        return False
    console.print(f"[bold green]✓ Python {version.major}.{version.minor}.{version.micro} detected.[/bold green]")
    return True


def step_2_check_venv() -> bool:
    console.print("\n[bold cyan]Step 2: Checking Virtual Environment...[/bold cyan]")
    venv_dir = ROOT_DIR / ".venv"
    if not venv_dir.exists():
        console.print("[yellow]Creating .venv virtual environment...[/yellow]")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            console.print("[bold green]✓ Virtual environment created at .venv[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to create virtual environment: {e}[/bold red]")
            return False
    else:
        console.print("[bold green]✓ Virtual environment exists at .venv[/bold green]")
    return True


def step_3_install_requirements() -> bool:
    console.print("\n[bold cyan]Step 3: Installing Requirements...[/bold cyan]")
    req_file = ROOT_DIR / "requirements.txt"
    if req_file.exists():
        try:
            console.print("[dim]Running pip install -r requirements.txt...[/dim]")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)
            console.print("[bold green]✓ Requirements installed successfully.[/bold green]")
            return True
        except Exception as e:
            console.print(f"[bold red]Failed to install requirements: {e}[/bold red]")
            return False
    return False


def step_4_check_playwright() -> bool:
    console.print("\n[bold cyan]Step 4: Checking Playwright & Browser Binaries...[/bold cyan]")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(settings.playwright_browsers_path)
    console.print(f"[dim]Playwright browser path set strictly to: {settings.playwright_browsers_path}[/dim]")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        console.print("[bold green]✓ Playwright Chromium browser installed on D: drive.[/bold green]")
        return True
    except Exception as e:
        console.print(f"[yellow]Note: Run 'python -m playwright install chromium' after pip setup.[/yellow]")
        return True


def step_5_check_ollama() -> bool:
    console.print("\n[bold cyan]Step 5: Checking Ollama Installation...[/bold cyan]")
    ollama_exe = settings.get_ollama_executable()
    try:
        res = subprocess.run([ollama_exe, "--version"], capture_output=True, text=True)
        if res.returncode == 0:
            console.print(f"[bold green]✓ Ollama detected: {res.stdout.strip()}[/bold green]")
            return True
    except Exception:
        pass

    console.print("[bold yellow]Ollama not found in system PATH or D:\\Ollama.[/bold yellow]")
    console.print("Please install Ollama from [link=https://ollama.com]https://ollama.com[/link]")
    console.print(f"[bold cyan]IMPORTANT:[/bold cyan] Set environment variable [bold yellow]OLLAMA_MODELS={settings.ollama_models}[/bold yellow] to save models on D: drive.")
    return False


def step_6_check_models(ollama_installed: bool) -> bool:
    console.print("\n[bold cyan]Step 6: Checking Ollama Models...[/bold cyan]")
    if not ollama_installed:
        console.print("[yellow]Skipping model download since Ollama is not installed yet.[/yellow]")
        return True

    target_coder = settings.model_coding
    target_reasoner = settings.model_reasoning
    ollama_exe = settings.get_ollama_executable()

    try:
        res = subprocess.run([ollama_exe, "list"], capture_output=True, text=True)
        models_str = res.stdout

        for model in [target_reasoner, target_coder]:
            model_base = model.split(":")[0]
            if model_base in models_str:
                console.print(f"[bold green]✓ Model '{model}' found.[/bold green]")
            else:
                console.print(f"[yellow]Model '{model}' is not pulled yet.[/yellow]")
                try:
                    ans = input(f"Would you like to pull '{model}' to {settings.ollama_models} now? (y/N): ").strip().lower()
                except (EOFError, OSError):
                    ans = "n"
                if ans == "y" or os.getenv("AUTO_PULL") == "1":
                    console.print(f"[dim]Running: {ollama_exe} pull {model}...[/dim]")
                    subprocess.run([ollama_exe, "pull", model], check=True)
                    console.print(f"[bold green]✓ Model '{model}' pulled successfully.[/bold green]")
        return True
    except Exception as e:
        console.print(f"[yellow]Model check note: {e}[/yellow]")
        return True


def main():
    console.print("[bold cyan]======================================================[/bold cyan]")
    console.print("[bold white]            AutonomousAI Setup Installer             [/bold white]")
    console.print("[bold cyan]======================================================[/bold cyan]")
    console.print(f"[bold green]All models & browsers configured on D: drive strictly.[/bold green]\n")

    if not step_1_check_python():
        sys.exit(1)

    step_2_check_venv()
    step_3_install_requirements()
    step_4_check_playwright()
    ollama_ok = step_5_check_ollama()
    step_6_check_models(ollama_ok)

    console.print("\n[bold green]======================================================[/bold green]")
    console.print("[bold green]  Installation Complete! Run: python verify.py        [/bold green]")
    console.print("[bold green]======================================================[/bold green]\n")


if __name__ == "__main__":
    main()
