# Land Records Ingestion (AnyROR Gujarat)

Pipeline for parsing, chunking, and embedding Gujarat 7/12 Satbara Utara land records.

## Sources
- AnyROR Gujarat: https://anyror.gujarat.gov.in
- Format: Digitized PDFs in Gujarati script
- Content: Form 7 (ownership) + Form 12 (crop/irrigation details)

## Pipeline Steps
1. PDF upload → Cloud Storage bucket
2. Document AI OCR (Gujarati → processed text)
3. LangChain chunking (1500 chars, 200 overlap)
4. BigQuery insert with metadata (Khata, survey, crop)
5. BQML embedding generation (text-multilingual-embedding-002)
6. Vector index creation (IVF, cosine similarity)

## Usage

```bash
# Install deps
pip install -r requirements.txt

# Process a single PDF
python ingest.py --pdf sample_7_12.pdf

# Process all PDFs from GCS bucket
python ingest.py --bucket

# Parse with Document AI OCR
python document_ai_parser.py sample_7_12.pdf
```

## Files

| File | Purpose |
|------|---------|
| `ingest.py` | Main PDF→BigQuery pipeline |
| `document_ai_parser.py` | Gujarati OCR via Document AI |
| `config.py` | Centralized configuration |
| `bigquery_setup.sql` | SQL for tables, models, indexes |

## Prerequisites
- GCP project with BigQuery, Document AI, Vertex AI enabled
- BigQuery connection to Vertex AI created (see Terraform)
- IAM role `roles/aiplatform.user` granted to connection SA
