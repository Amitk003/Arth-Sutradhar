import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "arth-sutradhar")
REGION = os.getenv("REGION", "asia-south1")
DATASET_ID = os.getenv("BQ_DATASET", "arth_sutradhar")
TABLE_ID = os.getenv("BQ_TABLE", "land_records_chunks")
RAW_BUCKET = os.getenv("RAW_BUCKET", f"{PROJECT_ID}-raw-documents")
PROCESSED_BUCKET = os.getenv("PROCESSED_BUCKET", f"{PROJECT_ID}-processed-data")

# Embedding config
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "text-multilingual-embedding-002")
EMBEDDING_MODEL_ENDPOINT = f"publishers/google/models/{EMBEDDING_MODEL_NAME}"
EMBEDDING_CONNECTION = os.getenv("EMBEDDING_CONNECTION", "vertex-ai-embedding")
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "land_records_embedding_model")
VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "land_records_vector_index")

# Chunking config
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Document AI config
DOCUMENT_AI_PROCESSOR_DISPLAY_NAME = os.getenv("DOCAI_PROCESSOR", "arth-sutradhar-land-records")
