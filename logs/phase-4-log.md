# Phase 4 Build Log: Polish, Pitch & Deployment

## [2026-06-20 23:55] Cloud Run Deployment
- Created `infra/scripts/deploy-cloudrun.ps1` - Full deployment script
  - Builds Docker image via Cloud Build
  - Pushes to Artifact Registry
  - Deploys to Cloud Run (2Gi, 2 CPU, auto-scaling)
  - Sets all environment variables
  - Outputs service URL
- Created `frontend/api/gunicorn.conf.py` - Production server config
- Created `frontend/api/.dockerignore` - Efficient Docker builds

## [2026-06-20 23:56] Pitch & Demo Materials
- Created `docs/pitch-deck.md` - 10-slide pitch outline
  - Problem → Solution → Architecture → Data Sources → Agent → Stack → Demo → Why We Win
  - Key differentiators highlighted
- Created `docs/live-demo-script.md` - Complete 5-min judging demo script
  - Step-by-step with expected outputs
  - "Wow factor" trigger for Sufficient Context Agent
  - Defensive engineering for failures
  - Backup plans for each component

## Key Differentiators for Judging
1. **Agentic RAG** — Not vanilla; Sufficient Context with self-correction
2. **Live MCP** — Not static CSVs; real MoSPI data
3. **Pure GCP** — No third-party vector DBs; BigQuery + Vertex AI + ADK
4. **Built for Bharat** — 86 languages, Gujarati OCR, voice/vision

## Files Created (Phase 4)
```
infra/scripts/deploy-cloudrun.ps1
frontend/api/gunicorn.conf.py
frontend/api/.dockerignore
docs/pitch-deck.md
docs/live-demo-script.md
```

## How to Deploy
```powershell
.\infra\scripts\deploy-cloudrun.ps1 -ProjectId arth-sutradhar
```

## Next Steps
- [ ] User deploys to Cloud Run
- [ ] User reviews and merges all PRs
- [ ] User practices live demo with script
- [ ] Hackday submission!
