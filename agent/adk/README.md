# ADK Agent Definitions

Agent Development Kit (ADK) multi-agent configuration for the 5-phase Sufficient Context loop.

## Agents

### 1. Planner Agent (Root)
- Deconstructs complex queries into parallel sub-tasks
- Determines cross-corpus retrieval needs (BigQuery vs MCP)

### 2. RAG / Data Fanout Agent
- Executes search fanouts across BigQuery Vector Search + MCP tools
- Parallel execution for low latency

### 3. Sufficient Context Agent
- Quality control inspector
- Missing Pieces Analysis
- Generates Reason + Feedback logs for iteration

### 4. Query Rewriter Agent
- Adapts strategy based on feedback logs
- Corrects API params or generates new search terms

### 5. Synthesis Agent
- Uses Gemini 1.5 Pro's long context window
- Generates grounded, narrative response
