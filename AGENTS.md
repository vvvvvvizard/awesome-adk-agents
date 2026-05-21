# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a monorepo of independent Google ADK (Agent Development Kit) Python agent projects under `my-adk-agents/`. There is no unified build system or root-level package manager — each agent has its own `requirements.txt` (or `pyproject.toml` for `education-path-advisor`).

### Required Environment Variable

All agents (except `data-analyst` which uses Ollama) require `GOOGLE_API_KEY` to be set for Gemini API access. Without it, agents load but API calls fail with `API_KEY_INVALID`.

### Virtual Environment

A shared venv at `/workspace/.venv` contains all agent dependencies. Activate with:
```bash
source /workspace/.venv/bin/activate
```

### Running Agents

| Agent | Directory | Run Command | Type |
|-------|-----------|-------------|------|
| Job Interview Agent | `my-adk-agents/job-interview-agent/app/` | `python main.py` | FastAPI web server on port 8000 |
| Project Manager Agent | `my-adk-agents/project-manager-agent/` | `python main.py` | Interactive CLI (requires stdin) |
| Education Path Advisor | `my-adk-agents/education-path-advisor/` | `adk web` or `adk run` | ADK CLI |
| Academic Research Assistant | `my-adk-agents/academic-research-assistant/` | `adk web` or `adk run` | ADK CLI |
| Data Analyst | `my-adk-agents/data-analyst/` | `adk run` | Requires local Ollama server |

### Lint & Test

- **Lint**: `flake8 my-adk-agents/ --max-line-length=120 --exclude='.venv,__pycache__'`
- **Test**: `cd my-adk-agents/education-path-advisor && python -m pytest tests/ -v` (requires `GOOGLE_API_KEY`)

### Key Gotchas

1. **ADK version conflicts**: The agents pin different versions of `google-adk` (0.5.0, 1.0.0, 1.1.1). Version 1.1.1 is installed in the shared venv and works for all except `data-analyst` (which uses a removed import `built_in_code_execution`).
2. **learning-content-system(WIP)**: Its `requirements.txt` lists `json`, `typing`, `dataclasses` which are stdlib modules; skip those when pip-installing.
3. **data-analyst agent**: Requires a local Ollama server with the `qwen3:8b` model pulled. Not functional without Ollama running.
4. **Job Interview Agent**: The FastAPI server starts immediately without needing `GOOGLE_API_KEY` — the key is only needed when a WebSocket session makes LLM calls.
5. **Project Manager Agent**: Uses `input()` for interactive chat. For non-interactive testing, verify the agent imports correctly: `python -c "from project_management_agent.agent import project_management_agent"`.
