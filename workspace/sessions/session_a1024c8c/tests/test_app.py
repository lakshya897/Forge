"""Application Entry Point"""
from fastapi import FastAPI

app = FastAPI(title="AutonomousAI App")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Hello from AutonomousAI"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
