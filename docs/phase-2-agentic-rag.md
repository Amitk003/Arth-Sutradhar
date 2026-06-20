# Phase 2: Agentic RAG Core

## Objective
Build the 5-phase Sufficient Context Agent loop that powers Arth-Sutradhar's reasoning engine.

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Phase 1: Orchestration (Planner Agent)               │
│   - Decompose query into sub-tasks                    │
│   - Determine cross-corpus retrieval needs            │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ Phase 2: Search (Data Fanout Agent)                  │
│   - BigQuery VECTOR_SEARCH for land records          │
│   - e-Sankhyiki MCP for live macroeconomic data      │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ Phase 3: Context Check (Sufficient Context Agent)    │
│   - Evaluates retrieved data against query needs     │
│   - Generates "Reason and Feedback" logs             │
└─────────────────────┬───────────────────────────────┘
        ┌────────────┘ │ ────────────┐ (if insufficient)
        ▼                            ▼
┌─────────────────┐       ┌──────────────────────────┐
│ Phase 5:        │       │ Phase 4: Iteration        │
│ Synthesis       │       │ (Query Rewriter Agent)    │
│ - Gemini 1.5    │       │ - Rewrites query params   │
│ - Generate      │       │ - Re-runs Phase 2         │
│   response      │       └──────────────────────────┘
└─────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `agent/adk/orchestrator.py` | 5-phase Sufficient Context Agent loop |
| `agent/tools/bigquery_tool.py` | BigQuery VECTOR_SEARCH tool |
| `agent/tools/mcp_tool.py` | e-Sankhyiki MCP tool |
| `agent/tools/config.py` | Agent configuration |
| `frontend/api/main.py` | FastAPI backend |
| `frontend/api/Dockerfile` | Cloud Run deployment |

## How to Run

### 1. Local API
```bash
pip install -r frontend/api/requirements.txt
uvicorn frontend.api.main:app --reload --port 8080
```

### 2. Test Query
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"text": "How will inflation affect cotton farmers in Gujarat?"}'
```

### 3. Docker Build & Deploy to Cloud Run
```bash
gcloud builds submit --tag asia-south1-docker.pkg.dev/arth-sutradhar/arth-sutradhar/agent-api:latest
gcloud run deploy arth-sutradhar-api \
  --image asia-south1-docker.pkg.dev/arth-sutradhar/arth-sutradhar/agent-api:latest \
  --region asia-south1 \
  --allow-unauthenticated
```

## Agent Loop Behavior
- **Multi-hop queries**: Agent auto-detects if query needs land records + macro data
- **Self-correction**: If context is missing, agent rewrites query and re-searches
- **Max 3 iterations**: Prevents infinite loops
- **Full reasoning log**: Every decision is logged for transparency
