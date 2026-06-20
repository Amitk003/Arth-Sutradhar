# Phase 0: Foundation

## Objective
Set up the project infrastructure, GCP environment, and development toolchain.

## Tasks Completed

### 1. Repository Setup
- Initialized monorepo structure
- Created branches: `main`, `phase-0-foundation`
- Directory layout:
  ```
  arth-sutradhar/
  ├── infra/terraform/     # Terraform IaC
  ├── infra/scripts/       # GCP setup scripts
  ├── ingestion/
  │   ├── land-records/    # AnyROR PDF parser
  │   └── mcp/             # e-Sankhyiki MCP client
  ├── agent/
  │   ├── adk/             # ADK agent definitions
  │   └── tools/           # Custom ADK tools
  ├── frontend/
  │   ├── mobile/          # React Native app
  │   └── api/             # FastAPI backend
  ├── docs/                # Documentation
  ├── logs/                # Build logs
  └── data/sample/         # Sample data files
  ```

### 2. GCP Infrastructure (Terraform)
- **Provider**: Google Cloud (asia-south1)
- **APIs Enabled**: AI Platform, BigQuery, Cloud Run, Document AI, Speech-to-Text, Artifact Registry, Eventarc
- **Resources**:
  - `arth-sutradhar-raw-documents` — Raw PDF uploads
  - `arth-sutradhar-processed-data` — Chunked/processed data
  - `arth-sutradhar-tfstate` — Terraform state bucket (versioned)
  - `arth_sutradhar` BigQuery dataset — Vector store
  - Vertex AI embedding connection — BigQuery → embeddings
  - Artifact Registry — Docker images
  - Cloud Run service — Agent API placeholder

### 3. GCP Setup Scripts
- `enable-apis.ps1` — Enables all required GCP APIs
- `setup-gcp.ps1` — Full one-time setup (project config, APIs, state bucket, Docker auth)

## Prerequisites
- [ ] GCP project `arth-sutradhar` created (by user)
- [ ] gcloud CLI installed and authenticated
- [ ] Terraform CLI installed (>= 1.5)
- [ ] GitHub repo cloned locally

## Manual Steps Required
1. Run `setup-gcp.ps1 -ProjectId arth-sutradhar` to initialize GCP
2. Create `infra/terraform/terraform.tfvars` with the project ID
3. Run `terraform init` then `terraform apply`
