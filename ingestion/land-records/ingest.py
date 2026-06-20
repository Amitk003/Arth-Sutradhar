import argparse
import logging
import sys
from pathlib import Path

from google.cloud import bigquery, storage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

from config import (
    PROJECT_ID, DATASET_ID, TABLE_ID, RAW_BUCKET,
    CHUNK_SIZE, CHUNK_OVERLAP, REGION,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def chunk_text(text: str, source_file: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_text(text)
    records = []
    for idx, chunk in enumerate(chunks):
        records.append({
            "chunk_id": f"{Path(source_file).stem}_{idx:04d}",
            "source_file": source_file,
            "chunk_index": idx,
            "content": chunk,
        })
    return records


def upload_to_gcs(bucket_name: str, local_path: str, blob_name: str | None = None) -> str:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    if blob_name is None:
        blob_name = Path(local_path).name
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    logger.info("Uploaded %s -> gs://%s/%s", local_path, bucket_name, blob_name)
    return f"gs://{bucket_name}/{blob_name}"


def write_to_bigquery(records: list[dict]) -> None:
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    errors = client.insert_rows_json(table_ref, records)
    if errors:
        logger.error("BigQuery insert errors: %s", errors)
        sys.exit(1)
    logger.info("Inserted %d rows into %s", len(records), table_ref)


def process_pdf(pdf_path: str, upload_gcs: bool = True) -> None:
    logger.info("Processing PDF: %s", pdf_path)

    text = extract_text_from_pdf(pdf_path)
    logger.info("Extracted %d characters", len(text))

    records = chunk_text(text, pdf_path)
    logger.info("Created %d chunks", len(records))

    if upload_gcs:
        upload_to_gcs(RAW_BUCKET, pdf_path)
        logger.info("Uploaded original PDF to GCS")

    write_to_bigquery(records)
    logger.info("PDF processing complete for: %s", pdf_path)


def process_all_in_bucket(prefix: str = "pdfs/") -> None:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(RAW_BUCKET)
    blobs = bucket.list_blobs(prefix=prefix)

    local_tmp = Path("/tmp/arth-sutradhar-ingest")
    local_tmp.mkdir(parents=True, exist_ok=True)

    for blob in blobs:
        if not blob.name.lower().endswith(".pdf"):
            continue
        local_path = local_tmp / Path(blob.name).name
        blob.download_to_filename(str(local_path))
        logger.info("Downloaded gs://%s/%s -> %s", RAW_BUCKET, blob.name, local_path)
        process_pdf(str(local_path), upload_gcs=False)


def main():
    parser = argparse.ArgumentParser(description="Arth-Sutradhar Land Records Ingestion")
    parser.add_argument("--pdf", help="Path to a single PDF file")
    parser.add_argument(
        "--bucket",
        action="store_true",
        help="Process all PDFs from the GCS raw bucket",
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip uploading the original PDF to GCS",
    )

    args = parser.parse_args()

    if args.pdf:
        process_pdf(args.pdf, upload_gcs=not args.no_upload)
    elif args.bucket:
        process_all_in_bucket()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
