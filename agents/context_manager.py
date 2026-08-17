"""
Context Manager Agent for AutonomousAI.
Deterministic, zero-LLM codebase indexing, import graph traversal, and AST relevance scoring.
"""

from pathlib import Path
from typing import Any, Dict, List
import time
import re
from schemas.state import ProjectState
from tools.search.search_tools import RipgrepSearchTool, DependencyGraphTool
from utils.console import ConsoleDashboard
from utils.db import MetricsDB


class ContextManagerAgent:
    """Retrieves and scores the top relevant codebase files for large repositories."""

    @staticmethod
    def run(state: ProjectState) -> Dict[str, Any]:
        start_t = time.time()
        ConsoleDashboard.agent_start("Context Manager", "Indexing codebase, building import graph, and ranking relevant files...")

        workspace_path = state.get("workspace_path", state.get("project_path", ""))
        goal = state.get("goal", "")

        # 1. Build import graph
        dep_tool = DependencyGraphTool()
        graph_res = dep_tool.execute(project_path=workspace_path)
        import_graph = graph_res.get("graph", {})

        # 2. Extract keywords from goal
        keywords = [w.lower() for w in re.findall(r"\b[a-zA-Z_]{3,}\b", goal)]

        # 3. Ripgrep keyword matches
        search_tool = RipgrepSearchTool()
        file_scores: Dict[str, float] = {}

        for file_key in import_graph.keys():
            file_scores[file_key] = 0.1  # base score

        for kw in keywords[:10]:
            res = search_tool.execute(query=kw, path=workspace_path, max_results=30)
            for match in res.get("matches", []):
                f = match.get("file", "").replace("\\", "/")
                file_scores[f] = file_scores.get(f, 0.0) + 0.25

        # 4. Rank files
        ranked_items = []
        for file_path, score in file_scores.items():
            norm_score = min(1.0, score)
            ranked_items.append({
                "path": file_path,
                "score": round(norm_score, 2),
                "reason": f"Keywords matched ({len(keywords)} terms considered)",
            })

        ranked_items.sort(key=lambda x: x["score"], reverse=True)
        top_files = ranked_items[:15]

        ConsoleDashboard.show_relevance_scores(top_files)

        duration_ms = (time.time() - start_t) * 1000
        MetricsDB.log_timing(state.get("session_id", "default"), "context_manager", duration_ms)

        ConsoleDashboard.agent_success("Context Manager", f"Indexed {len(file_scores)} files. Top {len(top_files)} selected for context.")

        return {
            "ranked_context_files": top_files,
            "architecture": {"import_graph": import_graph},
        }
