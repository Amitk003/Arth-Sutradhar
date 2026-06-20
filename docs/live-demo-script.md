# Live Demo Script for Judging

## Setup (Before Demo)
- [ ] API running on Cloud Run (or localhost with ngrok)
- [ ] React Native app loaded
- [ ] BigQuery vector index active (check: `SELECT COUNT(*) FROM land_records_chunks`)
- [ ] MCP server running
- [ ] Backend logs visible on second monitor

## Demo Flow (~5 minutes)

### 1. The Problem Hook (30s)
**Narrator**: *"Indian public data is fragmented. Land records in Gujarat, inflation data in Delhi — siloed. Standard RAG can't answer cross-domain questions. Let me show you what can."*

### 2. Simple Land Query (45s)
**Action**: Type: *"Show me cotton farmers in Gandhinagar with less than 2 hectares"*
**Expected**: VECTOR_SEARCH returns land records from BigQuery
**Point out**: "Semantic search across Gujarati land records — no keyword matching"

### 3. Simple Macro Query (30s)
**Action**: Type: *"What is the current CPI inflation for agricultural labourers in Gujarat?"*
**Expected**: MCP fetches live CPIALRL data from MoSPI
**Point out**: "Live government data — not a cached CSV"

### 4. The Killer Query — Cross-Domain (90s)
**Action**: Type: *"How will the recent CPI inflation increase impact the profitability of cotton farmers holding less than 2 hectares of irrigated land in Gandhinagar taluka?"*

**Expected output**:
1. Agent shows **"Plan created: query_land_records, query_macro_data, cross_analyze"**
2. Returns land records for small cotton farmers
3. Returns CPIALRL inflation data
4. Synthesizes: *"Cotton farmers with <2 hectares in Gandhinagar face X% input cost increase based on CPIALRL rise of Y%"*

**Point out**: "This is **impossible** for standard RAG — the agent had to fetch from two completely different systems and synthesize"

### 5. The "Wow Factor" — Self-Correction (60s)
**Action**: Type an obscure query, e.g.: *"Compare sesame seed farmers in Kutch district with ASUSE enterprise data for the informal sector"*

**Expected**:
1. First pass: insufficient context
2. Agent shows: **"Missing context: macro_data"** 
3. Agent rewrites query and re-runs MCP
4. Second pass succeeds
5. Synthesized comparison

**Action**: Show the backend logs side-by-side
**Point out**: *"The Sufficient Context Agent detected it had incomplete information, rewrote its query, and corrected itself — autonomously. This is Google's research-grade Agentic RAG in action."*

### 6. Voice + Vision (45s)
**Action**: Switch to React Native app
1. Tap **Voice** button, speak in Gujarati: *"ખેડૂતો પર ફુગાવાની શું અસર?"*
2. Tap **Camera**, take photo of printed land record
**Point out**: "Built for rural India — voice in 86 languages, document OCR"

### 7. Closing (30s)
**Narrator**: *"Arth-Sutradhar isn't just a RAG system — it's an autonomous economic analyst that bridges India's data silos. Pure GCP stack. No third-party dependencies. Self-correcting AI."*

## Defensive Engineering

### If BigQuery fails:
```bash
# Quick check
gcloud bigquery query --project=arth-sutradhar \
  "SELECT COUNT(*) FROM arth_sutradhar.land_records_chunks"
```

### If MCP server fails:
- Agent gracefully falls back to mock data
- Still shows full pipeline working

### If Voice fails:
- Fall back to text input
- "Voice requires physical device — works on Android/iOS"

### If Vision fails:
- Fall back to text description
- "Document AI processor may need 5 min to initialize"

## Backup Plan
- Pre-recorded video of the full demo as fallback
- All queries saved in a script file for copy-paste
- Screenshots of backend logs as backup

## Key Talking Points Under Pressure
- **"It's Agentic RAG, not vanilla RAG"** — Always lead with this
- **"Live MCP integration with MoSPI"** — Second differentiator
- **"Pure GCP stack"** — Third differentiator
- **"Built for Bharat"** — Fourth differentiator
