"""
BigQuery Vector Search Tool for Arth-Sutradhar ADK Agent.

Translates natural language queries into BigQuery VECTOR_SEARCH
calls against the land records embeddings.
"""

import logging
from dataclasses import dataclass

from google.cloud import bigquery

from agent.tools.config import PROJECT_ID, DATASET_ID, TABLE_ID, MODEL_ID

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

    def search(self, query_text: str, top_k: int = 10) -> list[SearchResult]:
        vector_search_query = f"""
        SELECT base.chunk_id, base.content, base.source_file, distance
        FROM VECTOR_SEARCH(
            TABLE `{PROJECT}.{DATASET}.{TABLE}`,
            'content_embedding',
            (
              SELECT text_embedding
              FROM ML.GENERATE_TEXT_EMBEDDING(
                MODEL `{MODEL}`,
                (SELECT @query_text AS content)
              )
            ),
            top_k => @top_k,
            distance_type => 'COSINE'
        )
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("query_text", "STRING", query_text),
                bigquery.ScalarQueryParameter("top_k", "INT64", top_k),
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
