"""
Document AI parser for Gujarati 7/12 Satbara Utara land records.

Uses Google Cloud Document AI to OCR and extract structured data
from scanned PDFs of Gujarat land records.

Extracted fields:
  - Khata number (account number)
  - Landholder name(s)
  - Survey number
  - Crop type(s)
  - Irrigation source
  - Land area (cultivable vs non-cultivable)
"""

import logging
from pathlib import Path
from typing import Any

from google.cloud import documentai
from google.cloud.documentai import Document

from ingestion.land_records.config import PROJECT_ID, REGION

logger = logging.getLogger(__name__)

PROCESSOR_DISPLAY_NAME = "arth-sutradhar-land-records"


def get_or_create_processor(client: documentai.DocumentProcessorServiceClient) -> str:
    """Get existing processor or create a new one for land records parsing."""
    parent = client.common_location_path(PROJECT_ID, REGION)
    processors = client.list_processors(parent=parent)

    for proc in processors:
        if proc.display_name == PROCESSOR_DISPLAY_NAME:
            logger.info("Using existing processor: %s", proc.name)
            return proc.name

    logger.info("Creating new processor: %s", PROCESSOR_DISPLAY_NAME)
    processor = client.create_processor(
        parent=parent,
        processor={
            "display_name": PROCESSOR_DISPLAY_NAME,
            "type_": "OCR_PROCESSOR",
        },
    )
    return processor.name


def parse_document(pdf_path: str | Path) -> Document:
    """
    Parse a PDF land record through Document AI OCR.

    Handles Gujarati script documents and returns structured text
    with layout information preserved.
    """
    client = documentai.DocumentProcessorServiceClient()
    processor_name = get_or_create_processor(client)

    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    raw_document = documentai.RawDocument(
        content=pdf_content,
        mime_type="application/pdf",
    )

    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document,
    )

    result = client.process_document(request=request)
    document = result.document

    logger.info(
        "Document parsed: %s pages, %d entities",
        document.page_count,
        len(document.entities) if document.entities else 0,
    )

    return document


def extract_entities(document: Document) -> dict[str, Any]:
    """
    Extract key entities from a parsed land record document.

    Returns a dict with structured fields from the 7/12 extract.
    """
    entities = {}
    for entity in (document.entities or []):
        entities[entity.type_] = entity.mention_text

    return {
        "khata_number": entities.get("khata_number", ""),
        "landholder_name": entities.get("landholder_name", ""),
        "survey_number": entities.get("survey_number", ""),
        "crop_type": entities.get("crop_type", ""),
        "irrigation_source": entities.get("irrigation_source", ""),
        "total_area": entities.get("total_area", ""),
        "cultivable_area": entities.get("cultivable_area", ""),
        "village": entities.get("village", ""),
        "taluka": entities.get("taluka", ""),
        "district": entities.get("district", ""),
    }


def parse_and_extract(pdf_path: str | Path) -> tuple[Document, dict[str, Any]]:
    """Convenience: parse PDF and extract entities in one call."""
    document = parse_document(pdf_path)
    entities = extract_entities(document)
    return document, entities


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse a 7/12 land record PDF")
    parser.add_argument("pdf", help="Path to the PDF file")
    args = parser.parse_args()

    doc, entities = parse_and_extract(args.pdf)
    print(f"Pages: {doc.page_count}")
    print(f"Text length: {len(doc.text)}")
    print(f"Entities: {entities}")


if __name__ == "__main__":
    main()
