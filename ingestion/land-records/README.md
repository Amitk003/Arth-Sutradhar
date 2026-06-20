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
