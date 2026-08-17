"""
Plugin Manifest Loader for AutonomousAI Framework Plugins.
Dynamically discovers all frameworks with plugin.json manifests and sorts by priority.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import importlib.util
from .base import BaseFrameworkPlugin


class FrameworkPluginLoader:
    """Discovers and registers framework plugins dynamically."""

    _plugins: List[BaseFrameworkPlugin] = []
    _initialized: bool = False

    @classmethod
    def load_plugins(cls) -> List[BaseFrameworkPlugin]:
        """Scan the frameworks directory for plugins."""
        if cls._initialized and cls._plugins:
            return cls._plugins

        frameworks_dir = Path(__file__).resolve().parent
        discovered: List[BaseFrameworkPlugin] = []

        for folder in frameworks_dir.iterdir():
            if not folder.is_dir() or folder.name.startswith("__"):
                continue

            manifest_file = folder / "plugin.json"
            py_file = folder / "plugin.py"

            if manifest_file.exists() and py_file.exists():
                try:
                    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                    # Dynamic import
                    spec = importlib.util.spec_from_file_location(f"frameworks.{folder.name}", py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        # Find subclass of BaseFrameworkPlugin
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (
                                isinstance(attr, type)
                                and issubclass(attr, BaseFrameworkPlugin)
                                and attr is not BaseFrameworkPlugin
                            ):
                                plugin_instance = attr()
                                plugin_instance.priority = manifest.get("priority", plugin_instance.priority)
                                discovered.append(plugin_instance)
                                break
                except Exception:
                    continue

        # Sort by priority (higher priority first)
        cls._plugins = sorted(discovered, key=lambda p: p.priority, reverse=True)
        cls._initialized = True
        return cls._plugins

    @classmethod
    def detect_framework(cls, project_path: Path) -> Optional[BaseFrameworkPlugin]:
        """Detect the highest priority matching framework for a project path."""
        plugins = cls.load_plugins()
        for plugin in plugins:
            if plugin.detect(project_path):
                return plugin
        return None
