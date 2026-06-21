import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "arth-sutradhar")
REGION = os.getenv("REGION", "asia-south1")
DATASET_ID = os.getenv("BQ_DATASET", "arth_sutradhar")
TABLE_ID = os.getenv("BQ_TABLE", "land_records_chunks")
MODEL_ID = os.getenv("BQ_MODEL", "land_records_embedding_model")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
STATE_CODE = os.getenv("STATE_CODE", "24")
FINANCIAL_YEAR = os.getenv("FINANCIAL_YEAR", "2024-25")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_LOCATION = os.getenv("GEMINI_LOCATION", "us-central1")
