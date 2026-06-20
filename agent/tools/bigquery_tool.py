"""
BigQuery Vector Search Tool for Arth-Sutradhar ADK Agent.

Translates natural language queries into BigQuery VECTOR_SEARCH
calls against the land records embeddings.
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import Any

from google.cloud import bigquery

from agent.tools.config import PROJECT_ID, DATASET_ID, TABLE_ID, MODEL_ID, REGION

logger = logging.getLogger(__name__)

PROJECT = PROJECT_ID
DATASET = DATASET_ID
TABLE = TABLE_ID
MODEL = f"{PROJECT}.{DATASET}.{MODEL_ID}"


@dataclass
class SearchResult:
    chunk_id: str
    content: str
    source_file: str
    distance: float


class BigQueryVectorSearchTool:
    def __init__(self):
        self.client = bigquery.Client(project=PROJECT)

    def _generate_embedding(self, text: str) -> list[float]:
        query = f"""
        SELECT text_embedding
        FROM ML.GENERATE_TEXT_EMBEDDING(
            MODEL `{MODEL}`,
            (SELECT @text AS content)
        )
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("text", "STRING", text)
            ]
        )
        results = self.client.query(query, job_config=job_config).result()
        for row in results:
            return row.text_embedding
        return []

    def search(self, query_text: str, top_k: int = 10) -> list[SearchResult]:
        embedding = self._generate_embedding(query_text)
        if not embedding:
            return []

        embedding_json = json.dumps(embedding)

        vector_search_query = f"""
        SELECT base.chunk_id, base.content, base.source_file, distance
        FROM VECTOR_SEARCH(
            TABLE `{PROJECT}.{DATASET}.{TABLE}`,
            'content_embedding',
            (SELECT ARRAY_FLOAT64({embedding_json}) AS embedding),
            top_k => @top_k,
            distance_type => 'COSINE',
            fraction_lists_to_search => 0.01
        )
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("top_k", "INT64", top_k)
            ]
        )
        results = self.client.query(vector_search_query, job_config=job_config).result()

        return [
            SearchResult(
                chunk_id=r.chunk_id,
                content=r.content,
                source_file=r.source_file,
                distance=r.distance,
            )
            for r in results
        ]

    def format_results(self, results: list[SearchResult]) -> str:
        if not results:
            return "No land records found matching your query."
        lines = ["Found land records:"]
        for r in results:
            lines.append(f"  - [{r.chunk_id}] (distance: {r.distance:.4f}) {r.content[:200]}")
        return "\n".join(lines)
