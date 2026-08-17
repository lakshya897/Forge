"""
AutonomousAI Configuration Module
Strictly enforces D: drive storage for all AI models, browser binaries, caches, and workspaces.
"""

from pathlib import Path
import os
import sys
import shutil
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=False)

# Root workspace directory
ROOT_DIR = Path(__file__).resolve().parent.parent


class Config(BaseModel):
    """Global configuration settings for AutonomousAI runtime."""

    # Storage paths - strictly configured to D: drive
    ollama_models: Path = Field(
        default_factory=lambda: Path(os.getenv("OLLAMA_MODELS", r"D:\ollama_models"))
    )
    ollama_host: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    )
    playwright_browsers_path: Path = Field(
        default_factory=lambda: Path(os.getenv("PLAYWRIGHT_BROWSERS_PATH", r"D:\playwright_browsers"))
    )
    hf_home: Path = Field(
        default_factory=lambda: Path(os.getenv("HF_HOME", r"D:\hf_cache"))
    )
    torch_home: Path = Field(
        default_factory=lambda: Path(os.getenv("TORCH_HOME", r"D:\torch_cache"))
    )
    tmp_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("TMPDIR", r"D:\tmp"))
    )

    # Local workspace and state paths
    workspace_root: Path = Field(
        default_factory=lambda: Path(os.getenv("WORKSPACE_ROOT", str(ROOT_DIR / "workspace")))
    )
    runtime_db_path: Path = Field(
        default_factory=lambda: Path(os.getenv("RUNTIME_DB_PATH", str(ROOT_DIR / "runtime" / "state.db")))
    )
    metrics_db_path: Path = Field(
        default_factory=lambda: Path(os.getenv("METRICS_DB_PATH", str(ROOT_DIR / "runtime" / "metrics.db")))
    )
    memory_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("MEMORY_DIR", str(ROOT_DIR / "memory")))
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("CACHE_DIR", str(ROOT_DIR / ".cache")))
    )
    reports_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("REPORTS_DIR", str(ROOT_DIR / "reports")))
    )
    screenshots_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("SCREENSHOTS_DIR", str(ROOT_DIR / "screenshots")))
    )

    # Model routing
    model_reasoning: str = Field(
        default_factory=lambda: os.getenv("MODEL_REASONING", "qwen2.5:7b")
    )
    model_coding: str = Field(
        default_factory=lambda: os.getenv("MODEL_CODING", "qwen2.5-coder:14b-instruct-q4_K_M")
    )
    model_fallback: str = Field(
        default_factory=lambda: os.getenv("MODEL_FALLBACK", "qwen2.5-coder:7b")
    )
    model_vision: str = Field(
        default_factory=lambda: os.getenv("MODEL_VISION", "qwen2.5-vl")
    )

    # Budget & Execution limits
    max_iterations: int = Field(
        default_factory=lambda: int(os.getenv("MAX_ITERATIONS", "8"))
    )
    time_budget_minutes: int = Field(
        default_factory=lambda: int(os.getenv("TIME_BUDGET_MINUTES", "45"))
    )
    confidence_threshold: float = Field(
        default_factory=lambda: float(os.getenv("CONFIDENCE_THRESHOLD", "0.90"))
    )
    execution_mode: Literal["auto", "assisted"] = Field(
        default_factory=lambda: os.getenv("EXECUTION_MODE", "auto") # type: ignore
    )

    # System parameters
    timeout_seconds: int = 120
    is_windows: bool = sys.platform.startswith("win")

    def ensure_directories(self) -> None:
        """Ensure all required D: drive and project directories exist."""
        dirs = [
            self.ollama_models,
            self.playwright_browsers_path,
            self.hf_home,
            self.torch_home,
            self.tmp_dir,
            self.workspace_root,
            self.runtime_db_path.parent,
            self.metrics_db_path.parent,
            self.memory_dir,
            self.cache_dir,
            self.reports_dir,
            self.screenshots_dir,
            self.workspace_root / "snapshots",
            self.workspace_root / "sessions",
            self.cache_dir / "embeddings",
        ]
        for directory in dirs:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

    def apply_environment_bindings(self) -> None:
        """Inject D: drive environment variables into the running process."""
        os.environ["OLLAMA_MODELS"] = str(self.ollama_models)
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(self.playwright_browsers_path)
        os.environ["HF_HOME"] = str(self.hf_home)
        os.environ["TORCH_HOME"] = str(self.torch_home)
        os.environ["TRANSFORMERS_CACHE"] = str(self.hf_home)
        os.environ["TMPDIR"] = str(self.tmp_dir)
        os.environ["TEMP"] = str(self.tmp_dir)
        os.environ["TMP"] = str(self.tmp_dir)

    def get_ollama_executable(self) -> str:
        """Find the absolute path of the Ollama executable on D: drive or system PATH."""
        # 1. Check custom D:\Ollama\ollama.exe (highest priority for custom D: install)
        d_path = Path(r"D:\Ollama\ollama.exe")
        if d_path.exists():
            return str(d_path)

        # 2. Check standard Windows AppData folder
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            appdata_path = Path(local_appdata) / "Programs" / "Ollama" / "ollama.exe"
            if appdata_path.exists():
                return str(appdata_path)

        # 3. Check system PATH using shutil.which
        sh = shutil.which("ollama")
        if sh:
            return sh

        # 4. Fallback default
        return "ollama"


# Instantiate global config singleton
settings = Config()
settings.ensure_directories()
settings.apply_environment_bindings()
