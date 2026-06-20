# Phase 1 Build Log: Data Pipeline - Dual Ingestion

## [2026-06-20 21:55] Land Records Pipeline
- Created `ingestion/land-records/ingest.py` - Main ingestion script
  - PDF text extraction (PyPDF2)
  - LangChain chunking (1500 chars, 200 overlap)
  - GCS upload and BigQuery insert
  - Supports single file and batch bucket processing
- Created `ingestion/land-records/config.py` - Centralized configuration
- Created `ingestion/land-records/document_ai_parser.py` - Document AI OCR for Gujarati
  - Creates/manages OCR_PROCESSOR
  - Extracts: khata, landholder, survey, crop, irrigation, area
  - Layout-preserved text extraction
- Created `ingestion/land-records/bigquery_setup.sql` - Full BigQuery setup
  - Table creation (land_records_chunks)
  - Remote embedding model (text-multilingual-embedding-002)
  - Embedding generation via ML.GENERATE_TEXT_EMBEDDING
  - VECTOR INDEX creation (IVF, COSINE)
  - VECTOR_SEARCH example queries
- Created `ingestion/land-records/requirements.txt` - Python dependencies

## [2026-06-20 21:56] MCP Pipeline
- Created `ingestion/mcp/mcp_client.py` - MoSPI MCP client
  - 4-step protocol: list_datasets → get_indicators → get_metadata → get_data
  - Mock mode for development without live server
  - Convenience methods for CPIALRL and PLFS data
  - ADK-ready interface
- Created `ingestion/mcp/run_mcp_server.py` - Server runner script
- Created `ingestion/mcp/requirements.txt` - MCP dependencies

## Files Created (Phase 1)
```
ingestion/
├── land-records/
│   ├── requirements.txt
│   ├── config.py
│   ├── ingest.py              # Main ingestion pipeline
│   ├── document_ai_parser.py   # Gujarati OCR via Document AI
│   └── bigquery_setup.sql      # BigQuery schema + models
└── mcp/
    ├── requirements.txt
    ├── mcp_client.py           # MoSPI MCP client
    └── run_mcp_server.py       # MCP server runner
```

## Next Steps
- [ ] User runs bigquery_setup.sql in BigQuery console
- [ ] User downloads sample 7/12 PDF and runs ingest.py
- [ ] User clones esankhyiki-mcp repo for live MCP server
- [ ] Proceed to Phase 2: Agentic RAG Core
