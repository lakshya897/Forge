"""
AutonomousAI — Local Multi-Agent AI Software Engineer.
Main Entry Point.
"""

import sys
from cli import app

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default to interactive run command
        sys.argv.append("run")
    app()
