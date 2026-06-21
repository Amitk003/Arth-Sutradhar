"""
Arth-Sutradhar FastAPI Backend

REST API that bridges the React Native frontend to the ADK agent.
Endpoints:
  - POST /query       Submit text/voice query
  - POST /query/upload Submit image for OCR-based query
  - GET  /health      Health check
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.adk.orchestrator import ArthSutradharAgent
from agent.tools import config as agent_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Arth-Sutradhar API",
    description="Multi-agent RAG engine for Indian public data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en", pattern=r"^[a-z]{2}(-[a-z]{2})?$")


class QueryResponse(BaseModel):
    response: str
    iteration_count: int
    feedback_log: list[str]


class HealthResponse(BaseModel):
    status: str
    project: str


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", project="arth-sutradhar")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    logger.info("Query received: %s (lang: %s)", request.text[:100], request.language)
    try:
        agent = ArthSutradharAgent()
        text = request.text
        response = agent.run(text)
        return QueryResponse(
            response=response,
            iteration_count=agent.state.iteration_count,
            feedback_log=agent.state.feedback_log,
        )
    except Exception as e:
        logger.error("Query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/upload")
async def query_with_image(file: UploadFile):
    """
    Accept an image upload (e.g., photo of a land record).
    Extracts text via OCR and submits as a query.
    """
    logger.info("Image upload received: %s", file.filename)
    contents = await file.read()
    agent = ArthSutradharAgent()

    try:
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=contents)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            extracted_text = texts[0].description
        else:
            extracted_text = "No text found in image."

        logger.info("OCR extracted: %s", extracted_text[:200])
        result = agent.run(extracted_text)
        return QueryResponse(
            response=result,
            iteration_count=agent.state.iteration_count,
            feedback_log=agent.state.feedback_log,
        )
    except ImportError:
        logger.warning("Vision API not available. Falling back to mock OCR.")
        result = agent.run(f"Document image: {file.filename}")
        return QueryResponse(
            response=result,
            iteration_count=agent.state.iteration_count,
            feedback_log=agent.state.feedback_log,
        )
