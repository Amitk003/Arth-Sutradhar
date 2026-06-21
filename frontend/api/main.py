"""
Arth-Sutradhar FastAPI Backend

REST API that bridges the frontend to the ADK agent with multilingual support.
Endpoints:
  - POST /query       Submit text/voice query (auto-translates Hindi/Gujarati to English)
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
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANG_MAP = {
    "hi": "hi", "gu": "gu", "bn": "bn", "ta": "ta", "te": "te",
    "mr": "mr", "pa": "pa", "or": "or", "kn": "kn", "ml": "ml",
}


class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en", pattern=r"^[a-z]{2}(-[a-z]{2})?$")


class QueryResponse(BaseModel):
    response: str
    iteration_count: int
    feedback_log: list[str]
    source_language: str = "en"


class HealthResponse(BaseModel):
    status: str
    project: str


async def _translate(text: str, source: str, target: str) -> str:
    if source == target:
        return text
    try:
        import httpx
        import google.auth
        from google.auth.transport.requests import Request as AuthRequest

        credentials, _ = google.auth.default()
        auth_req = AuthRequest()
        credentials.refresh(auth_req)
        token = credentials.token

        resp = httpx.post(
            "https://translation.googleapis.com/language/translate/v2",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": text, "source": source, "target": target, "format": "text"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["translations"][0]["translatedText"]
    except ImportError:
        logger.warning("httpx/google.auth not available, skipping translation")
        return text
    except Exception as e:
        logger.warning("Translation failed: %s", e)
        return text


async def _detect_language(text: str) -> str:
    try:
        import httpx
        import google.auth
        from google.auth.transport.requests import Request as AuthRequest

        credentials, _ = google.auth.default()
        auth_req = AuthRequest()
        credentials.refresh(auth_req)
        token = credentials.token

        resp = httpx.post(
            "https://translation.googleapis.com/language/translate/v2/detect",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": text},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["detections"][0][0]["language"]
    except Exception:
        return "en"


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", project="arth-sutradhar")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    logger.info("Query received: %s (lang: %s)", request.text[:100], request.language)

    text = request.text
    source_lang = request.language

    if source_lang != "en" and source_lang in LANG_MAP:
        translated = await _translate(text, source_lang, "en")
        logger.info("Translated from %s: %s -> %s", source_lang, text[:50], translated[:50])
        text = translated
    elif source_lang == "auto":
        detected = await _detect_language(text)
        if detected and detected != "en":
            source_lang = detected
            translated = await _translate(text, detected, "en")
            logger.info("Auto-detected %s, translated: %s -> %s", detected, text[:50], translated[:50])
            text = translated

    try:
        agent = ArthSutradharAgent()
        response = agent.run(text)

        if source_lang != "en" and source_lang in LANG_MAP:
            response = await _translate(response, "en", source_lang)

        return QueryResponse(
            response=response,
            iteration_count=agent.state.iteration_count,
            feedback_log=agent.state.feedback_log,
            source_language=source_lang,
        )
    except Exception as e:
        logger.error("Query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/upload")
async def query_with_image(file: UploadFile):
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
        lang = await _detect_language(extracted_text)
        if lang != "en":
            extracted_text = await _translate(extracted_text, lang, "en")

        result = agent.run(extracted_text)
        return QueryResponse(
            response=result,
            iteration_count=agent.state.iteration_count,
            feedback_log=agent.state.feedback_log,
            source_language=lang,
        )
    except ImportError:
        logger.warning("Vision API not available. Falling back to mock OCR.")
        result = agent.run(f"Document image: {file.filename}")
        return QueryResponse(
            response=result,
            iteration_count=agent.state.iteration_count,
            feedback_log=agent.state.feedback_log,
        )
