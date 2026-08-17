"""Unit tests for demo application."""

from pathlib import Path
import sys

# Ensure demo_project directory is on sys.path
demo_dir = Path(__file__).resolve().parent.parent
if str(demo_dir) not in sys.path:
    sys.path.insert(0, str(demo_dir))

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
