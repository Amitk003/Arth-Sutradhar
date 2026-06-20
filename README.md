# Arth-Sutradhar (The Economic Narrator)

A multi-agent, multimodal RAG system that bridges micro-level rural land records with macro-level government statistics for the "RAG Over Bharat" track.

## Architecture

```
User Input (Voice/Text/Image)
    │
    ▼
┌──────────────────────────────────────────────┐
│         ADK Agent Orchestrator                │
│  Planner → Search Fanout → Context Check      │
│  → Query Rewriter → Synthesis Agent           │
└────┬─────────────────────────┬────────────────┘
     │                         │
     ▼                         ▼
┌──────────────┐    ┌──────────────────────┐
│ BigQuery     │    │ e-Sankhyiki MCP      │
│ Vector Store │    │ (Live Gov Stats)     │
└──────────────┘    └──────────────────────┘
```

## Project Structure

```
├── infra/              # Terraform + GCP scripts
│   ├── terraform/      # IaC (all GCP resources)
│   └── scripts/        # GCP automation scripts
├── ingestion/          # Data pipelines
│   ├── land-records/   # AnyROR PDF parser
│   └── mcp/            # e-Sankhyiki MCP client
├── agent/              # AI agent layer
│   ├── adk/            # ADK agent definitions
│   └── tools/          # Custom tools (BigQuery, MCP)
├── frontend/           # User interfaces
│   ├── mobile/         # React Native app (voice, vision, text)
│   │   ├── App.tsx
│   │   └── src/
│   │       ├── screens/   # HomeScreen, QueryScreen
│   │       ├── services/  # API client
│   │       └── types/
│   └── api/            # FastAPI backend
├── docs/               # Architecture & phase docs
├── logs/               # Build logs
└── data/sample/        # Sample data files
```

## Tech Stack

- **Cloud**: Google Cloud Platform (asia-south1)
- **AI**: Gemini 1.5 Pro, Vertex AI, Document AI
- **Data**: BigQuery Vector Search, e-Sankhyiki MCP
- **Orchestration**: Vertex AI ADK (Agent Development Kit)
- **Infrastructure**: Terraform
- **Frontend**: React Native

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Foundation - GCP, Terraform, Repo | ✅ Complete |
| 1 | Data Pipeline - Dual Ingestion | ✅ Complete |
| 2 | Agentic RAG Core - 5-Phase Loop | ✅ Complete |
| 3 | Multimodal Frontend (React Native) | ✅ Complete |
| 4 | Polish, Pitch & Deployment | ✅ Complete |

## Prerequisites

- GCP project `arth-sutradhar` created
- gcloud CLI installed and authenticated
- Terraform >= 1.5 installed

## Getting Started

```bash
# 1. Initialize GCP
./infra/scripts/setup-gcp.ps1 -ProjectId arth-sutradhar

# 2. Deploy infrastructure
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project ID
terraform init
terraform plan
terraform apply
```
