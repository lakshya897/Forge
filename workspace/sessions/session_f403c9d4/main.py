"""Sample FastAPI Project for AutonomousAI Testing."""

from fastapi import FastAPI

app = FastAPI(title="Demo Application")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Demo Application"}

@app.get("/api/items")
def list_items():
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
