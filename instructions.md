# AutonomousAI — Local Multi-Agent Software Engineering System (PRD + Implementation Spec)

Version: 1.0
Target Runtime: Windows 11
LLM Runtime: Ollama (Local Only)
Framework: LangGraph
Language: Python 3.12+

---

# Objective

Build a fully autonomous multi-agent AI software engineer that accepts an existing project folder, understands a natural-language requirement, modifies the codebase, launches the application, tests it automatically, reviews its own work, and continuously loops until the Product Owner validates that the requested outcome has been achieved.

The entire system must work **locally** using Ollama. No paid APIs are allowed.

---

# Primary Goal

User provides:

- Existing project folder
- Feature request / bug report
- Expected behavior
- Optional constraints

The system should:

1. Analyze the project.
2. Detect framework automatically.
3. Create an execution plan.
4. Modify only required files.
5. Build the project.
6. Run backend tests.
7. Run browser tests with Playwright.
8. Review code quality.
9. Validate against Product Owner acceptance criteria.
10. Repeat until successful.

---

# Windows First Policy

This project is designed only for Windows.

Do NOT generate Docker.

Do NOT require WSL.

Use native PowerShell and CMD compatibility.

---

# Tech Stack

| Purpose | Technology |
|----------|------------|
| Agent orchestration | LangGraph |
| LLM | Ollama |
| Coding Model | Qwen2.5-Coder 14B |
| Secondary Model | Qwen2.5 7B |
| Browser Automation | Playwright |
| Backend Testing | Pytest |
| File Watching | Watchdog |
| Git | GitPython |
| API | FastAPI |
| State | Pydantic |

---

# Required Folder Structure

```text
AutonomousAI/
│
├── agents/
│   ├── product_owner.py
│   ├── analyzer.py
│   ├── planner.py
│   ├── architect.py
│   ├── implementer.py
│   ├── reviewer.py
│   ├── tester.py
│   ├── browser_tester.py
│   ├── backend_tester.py
│   ├── security.py
│   └── devops.py
│
├── graph/
│   ├── state.py
│   ├── workflow.py
│   ├── routing.py
│   └── memory.py
│
├── prompts/
│
├── reports/
│
├── screenshots/
│
├── sandbox/
│
├── utils/
│
├── requirements.txt
│
├── installer.py
│
├── verify.py
│
└── main.py
```

---

# Startup Flow

```text
User

↓

Select Project Folder

↓

Enter Requirement

↓

Product Owner

↓

Project Analyzer

↓

Planner

↓

Architect

↓

Implementer

↓

Reviewer

↓

Backend Test

↓

Browser Test

↓

Security

↓

Acceptance Check

├── Success → Finish

└── Failed → Feedback → Implementer
```

The loop must continue automatically.

---

# Agent Specifications

## 1. Product Owner

### Responsibilities

- Read user requirement
- Convert into structured specification
- Create acceptance criteria
- Maintain project memory
- Decide final approval

### Output

```json
{
  "goal": "",
  "constraints": [],
  "acceptance_tests": []
}
```

Never approve if even one acceptance criterion fails.

---

## 2. Project Analyzer

Automatically detect:

- React
- Next.js
- Angular
- Vue
- Express
- Node
- Django
- Flask
- FastAPI
- Spring Boot

Also detect:

- package manager
- build command
- test framework
- database
- environment files

Generate:

`reports/project_analysis.md`

---

## 3. Planner

Convert the Product Owner goal into executable tasks.

Example:

```text
Task 1
Update Login API

Task 2
Modify React UI

Task 3
Update Validation

Task 4
Create Tests

Task 5
Verify Browser
```

Return ordered tasks.

---

## 4. Architect

Understand existing architecture.

Generate:

- routing map
- component tree
- backend endpoints
- dependency graph

Must NEVER redesign the project unless required.

---

## 5. Implementer

Responsibilities:

- Edit files
- Create files
- Preserve style
- Preserve formatting
- Avoid unnecessary modifications

Return modified file list.

---

## 6. Reviewer

Check:

- Bugs
- Code smell
- Duplicate logic
- Performance
- Naming
- Architecture

Return markdown review.

---

## 7. Backend Tester

Automatically:

- Start backend
- Detect port
- Test APIs
- Verify database
- Validate response schema

Use Pytest where available.

---

## 8. Browser Tester

Using Playwright:

Automatically:

- Launch localhost
- Wait until ready
- Navigate pages
- Click buttons
- Fill forms
- Validate text
- Capture console errors
- Capture screenshots
- Save HTML snapshot

Failure should generate:

```text
screenshots/
error.png

reports/browser_failure.md
```

---

## 9. Security Agent

Check:

- SQL Injection
- XSS
- Hardcoded secrets
- API keys
- Unsafe eval
- Unsafe subprocess

Generate security report.

---

## 10. DevOps Agent

Responsibilities:

- Install dependencies
- Build project
- Restart server
- Detect missing packages
- Generate build logs

If dependency missing:

Generate PowerShell command instead of crashing.

Example:

```powershell
npm install axios
```

---

# Shared State

Create Pydantic state.

```python
class ProjectState(BaseModel):
    project_path: str
    goal: str
    acceptance: list
    tech_stack: dict
    plan: list
    modified_files: list
    review: dict
    backend: dict
    browser: dict
    security: dict
    approved: bool = False
    iteration: int = 0
```

Every agent updates this.

---

# Persistent Memory

Create:

```text
memory/
project_memory.json
```

Store:

- previous failures
- successful fixes
- architecture summary
- user constraints

Reuse every iteration.

---

# Automatic Framework Detection

Detect using files.

| File | Framework |
|------|-----------|
| package.json | React / Node |
| next.config.js | Next |
| angular.json | Angular |
| manage.py | Django |
| pom.xml | Spring |
| requirements.txt | Python |
| vite.config.ts | Vite |

No hardcoded selection.

---

# Browser Detection

Automatically detect localhost.

Check ports:

```text
3000
5173
4173
8000
8080
4200
```

Wait until HTTP 200.

Only then start Playwright.

---

# Reports

Every iteration generate:

```text
reports/

iteration_001.md

iteration_002.md

final_report.md
```

Each report includes:

- Files changed
- Tests passed
- Tests failed
- Review issues
- Browser screenshots
- Remaining problems

---

# Installer Requirements

Create `installer.py`.

Its job:

## Step 1

Check Python.

If missing:

Display:

```text
Python 3.12+ required.
Download:
https://python.org
```

Do not continue.

## Step 2

Check virtual environment.

If missing:

```powershell
python -m venv .venv
```

## Step 3

Activate environment.

PowerShell:

```powershell
.venv\Scripts\activate
```

## Step 4

Install requirements.

```powershell
pip install -r requirements.txt
```

## Step 5

Check Playwright.

If missing:

```powershell
playwright install
```

## Step 6

Check Ollama.

Run:

```powershell
ollama --version
```

If unavailable:

Display installation message.

## Step 7

Check Model.

Run:

```powershell
ollama list
```

If model missing:

```powershell
ollama pull qwen2.5-coder:14b-instruct-q4_K_M
```

Do not download automatically without confirmation.

---

# Verify Script

Create `verify.py`.

It should verify:

- Python
- Pip
- Ollama
- Model
- Playwright
- Git
- Node (optional)
- npm (optional)

Display:

```text
Python         ✓

Ollama         ✓

Model          ✓

Playwright     ✓

Git            ✓
```

If anything missing, print exact installation command.

---

# Requirements.txt

Include:

```text
langgraph

langchain

langchain-ollama

playwright

watchdog

gitpython

pytest

fastapi

uvicorn

pydantic

rich

typer

python-dotenv
```

---

# Main Entry

Running:

```powershell
python main.py
```

Should open CLI.

Example:

```text
AutonomousAI

Select Project Folder

D:\Projects\TodoApp

Describe your requirement

Add dark mode and improve login validation
```

Then workflow begins.

---

# Acceptance Rules

The workflow finishes ONLY IF:

- Product Owner approves
- Backend tests pass
- Browser tests pass
- No critical reviewer issue
- Security critical count = 0

Otherwise:

Return to Implementer.

Unlimited retry loop.

---

# Coding Standards

- Use type hints everywhere.
- Use Pydantic models.
- Use Rich for CLI.
- Use Typer for commands.
- Use async where appropriate.
- Every agent must be independently testable.
- Every module must contain docstrings.
- Avoid global variables.

---

# Deliverables

Generate a complete runnable project containing:

- LangGraph workflow
- 10 autonomous agents
- Shared state
- Persistent memory
- Ollama integration
- Playwright browser automation
- Backend testing
- Security scanning
- Installer
- Verification tool
- Rich CLI
- Reports
- One-command execution

The generated project must be immediately runnable on Windows after executing:

```powershell
python installer.py

python verify.py

python main.py
```

End of specification.