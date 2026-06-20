# Phase 1: Data Pipeline - Dual Ingestion

## Objective
Build two parallel data ingestion pipelines:
1. **Land Records (AnyROR Gujarat)** — Unstructured PDF parsing → BigQuery Vector Store
2. **Macro Statistics (e-Sankhyiki)** — Live MCP client for MoSPI data

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Land Records Pipeline                │
│                                                      │
│  PDF (7/12 Utara) ─► Document AI OCR ─► Chunking    │
│       │                        (LangChain)           │
│       ▼                                              │
│  Cloud Storage ─► BigQuery ─► BQML Embeddings       │
│   (raw docs)       (table)    (multilingual-002)     │
│                                      │               │
│                                      ▼               │
│                              Vector Index (IVF)      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              e-Sankhyiki MCP Pipeline                │
│                                                      │
│  MoSPI Server ─► FastMCP ─► ADK Tool Client          │
│   (live data)      (proxy)    (4-step protocol)      │
│                                                      │
│  Protocols: list_datasets → get_indicators           │
│             → get_metadata → get_data                │
└─────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `ingestion/land-records/ingest.py` | Main PDF→BigQuery pipeline |
| `ingestion/land-records/document_ai_parser.py` | Gujarati OCR via Document AI |
| `ingestion/land-records/config.py` | Centralized config |
| `ingestion/land-records/bigquery_setup.sql` | SQL for tables, models, indexes |
| `ingestion/land-records/requirements.txt` | Python deps |
| `ingestion/mcp/mcp_client.py` | MoSPI MCP client (4-step protocol) |
| `ingestion/mcp/run_mcp_server.py` | MCP server runner |
| `ingestion/mcp/requirements.txt` | Python deps |

## How to Run

### 1. BigQuery Setup
Open the BigQuery console and run `bigquery_setup.sql` sequentially.

### 2. Land Records Ingestion
```bash
cd ingestion/land-records
pip install -r requirements.txt

# Single PDF
python ingest.py --pdf sample_7_12.pdf

# Batch from GCS bucket
python ingest.py --bucket

# Parse with Document AI OCR
python document_ai_parser.py sample_7_12.pdf
```

### 3. MCP Server
```bash
cd ingestion/mcp
pip install -r requirements.txt
python run_mcp_server.py
```

## Manual Steps Required
- [ ] Run `bigquery_setup.sql` in BigQuery console (Steps 1-4)
- [ ] Download a sample 7/12 PDF from AnyROR Gujarat for testing
- [ ] Verify vector index is created (check in BigQuery console)
