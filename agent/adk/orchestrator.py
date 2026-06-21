"""
Arth-Sutradhar Agent Orchestrator

Implements the 5-phase Sufficient Context Agent loop:
   1. Orchestration (Planner)
   2. Search (Data Fanout)
   3. Context Check (Sufficient Context Agent)
   4. Iteration (Query Rewriter)
   5. Synthesis (Report generation via Gemini 2.5 Flash)
"""


import logging
from dataclasses import dataclass, field
from typing import Any

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from agent.tools.bigquery_tool import BigQueryVectorSearchTool
from agent.tools.mcp_tool import MCPTool
from agent.tools import config as agent_config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Arth-Sutradhar, an expert agricultural and economic analyst for India.
Your role is to synthesize retrieved data from land records and macroeconomic sources into a clear, accurate, and narrative response.

Guidelines:
- Ground every claim in the retrieved data — do not fabricate numbers or facts.
- If the data has gaps, state what is known and what is missing honestly.
- Write in plain text with clear sections. Use short paragraphs.
- Keep the response concise (under 500 words unless the query demands depth).
- If the agent needed multiple iterations to find data, mention the self-correction briefly.
- Do NOT use markdown formatting like **bold** or bullet lists. Use plain text with line breaks."""


@dataclass
class AgentState:
    user_query: str
    plan: list[str] = field(default_factory=list)
    retrieved_context: dict[str, Any] = field(default_factory=dict)
    feedback_log: list[str] = field(default_factory=list)
    iteration_count: int = 0
    final_response: str | None = None
    is_complete: bool = False

MAX_ITERATIONS = 3


class ArthSutradharAgent:
    """
    Multi-agent orchestrator implementing the Sufficient Context Agent pattern.

    The agent autonomously decides which tools to invoke, checks if the
    retrieved context is sufficient, iterates if needed, and synthesizes
    the final response using Gemini 2.5 Flash.
    """

    def __init__(self, project_id: str | None = None):
        self.project_id = project_id or agent_config.PROJECT_ID
        vertexai.init(project=self.project_id, location=agent_config.GEMINI_LOCATION)
        self.llm = GenerativeModel(
            agent_config.GEMINI_MODEL,
            system_instruction=[SYSTEM_PROMPT],
        )
        self.bq_tool = BigQueryVectorSearchTool()
        self.mcp_tool = MCPTool()
        self.state = AgentState(user_query="")

    def run(self, user_query: str) -> str:
        self.state = AgentState(user_query=user_query)
        logger.info("Agent started for query: %s", user_query)

        self._phase_1_orchestrate()
        while not self.state.is_complete and self.state.iteration_count < MAX_ITERATIONS:
            self._phase_2_search()
            self._phase_3_context_check()
            if not self.state.is_complete:
                self._phase_4_iterate()
        self._phase_5_synthesize()
        return self.state.final_response

    def _phase_1_orchestrate(self):
        """Phase 1: Decompose query into actionable sub-tasks."""
        query = self.state.user_query.lower()
        tasks = []

        needs_land_records = any(kw in query for kw in [
            "land", "crop", "farmer", "irrigation", "khata", "survey",
            "cotton", "wheat", "groundnut", "hectare", "village",
        ])
        needs_macro_data = any(kw in query for kw in [
            "inflation", "cpi", "price", "wage", "economy", "gdp",
            "labour", "employment", "index", "rate", "cost",
        ])
        needs_cross_analysis = needs_land_records and needs_macro_data

        if needs_cross_analysis:
            tasks = ["query_land_records", "query_macro_data", "cross_analyze"]
        elif needs_land_records:
            tasks = ["query_land_records"]
        elif needs_macro_data:
            tasks = ["query_macro_data"]
        else:
            tasks = ["query_land_records", "query_macro_data"]

        self.state.plan = tasks
        self.state.feedback_log.append(f"Plan created: {tasks}")
        logger.info("Phase 1 - Plan: %s", tasks)

    def _phase_2_search(self):
        """Phase 2: Execute search fanout across tools."""
        logger.info("Phase 2 - Search iteration %d", self.state.iteration_count)

        for task in self.state.plan:
            if task == "query_land_records":
                try:
                    results = self.bq_tool.search(self.state.user_query)
                    self.state.retrieved_context["land_records"] = results
                    self.state.feedback_log.append(
                        f"BigQuery returned {len(results)} land records"
                    )
                except Exception as e:
                    logger.error("BQ search failed: %s", e)
                    self.state.retrieved_context["land_records"] = []
                    self.state.feedback_log.append(
                        f"BigQuery search failed: {e}"
                    )

            elif task == "query_macro_data":
                try:
                    datasets = self.mcp_tool.list_datasets()
                    data_points = []
                    for ds in datasets:
                        indicators = self.mcp_tool.get_indicators(ds["id"])
                        for ind in indicators[:2]:
                            data = self.mcp_tool.get_data(
                                ds["id"], ind["id"],
                                state_code=agent_config.STATE_CODE,
                                financial_year=agent_config.FINANCIAL_YEAR,
                            )
                            data_points.extend(data)
                    self.state.retrieved_context["macro_data"] = data_points
                    self.state.feedback_log.append(
                        f"MCP returned {len(data_points)} data points"
                    )
                except Exception as e:
                    logger.error("MCP fetch failed: %s", e)
                    self.state.retrieved_context["macro_data"] = []
                    self.state.feedback_log.append(
                        f"MCP data fetch failed: {e}"
                    )

    def _phase_3_context_check(self):
        """Phase 3: Check if retrieved context is sufficient."""
        logger.info("Phase 3 - Context check")
        missing = []

        if "query_land_records" in self.state.plan:
            records = self.state.retrieved_context.get("land_records", [])
            if not records:
                missing.append("land_records")

        if "query_macro_data" in self.state.plan:
            macro = self.state.retrieved_context.get("macro_data", [])
            if not macro:
                missing.append("macro_data")

        if missing:
            self.state.feedback_log.append(f"Missing context: {missing}")
            self.state.is_complete = False
            logger.info("Phase 3 - Missing: %s", missing)
        else:
            self.state.feedback_log.append("Context is sufficient")
            self.state.is_complete = True
            logger.info("Phase 3 - Context sufficient")

    def _phase_4_iterate(self):
        """Phase 4: Rewrite query and re-search."""
        self.state.iteration_count += 1
        logger.info("Phase 4 - Iteration %d", self.state.iteration_count)

        feedback = self.state.feedback_log[-1] if self.state.feedback_log else ""
        if "land_records" in feedback.lower():
            self.state.user_query = f"{self.state.user_query} (Gujarat land records)"
        if "macro_data" in feedback.lower():
            self.state.user_query = f"{self.state.user_query} (India stats latest year)"

        self.state.feedback_log.append(
            f"Rewritten query: {self.state.user_query[:100]}..."
        )

    def _phase_5_synthesize(self):
        """Phase 5: Synthesize final response using Gemini 2.5 Flash."""
        logger.info("Phase 5 - Synthesis with Gemini")

        land_records = self.state.retrieved_context.get("land_records", [])
        macro_data = self.state.retrieved_context.get("macro_data", [])

        context_parts = [f"User Query: {self.state.user_query}", ""]

        if land_records:
            context_parts.append("Retrieved Land Records:")
            for r in land_records:
                context_parts.append(f"  - [{r.source_file}] {r.content[:300]}")
            context_parts.append("")

        if macro_data:
            context_parts.append("Retrieved Macroeconomic Data:")
            for d in macro_data:
                context_parts.append(f"  - {d.dataset}/{d.indicator}: {d.value} {d.unit}")
            context_parts.append("")

        context_parts.append("Agent Reasoning Log:")
        for log in self.state.feedback_log:
            context_parts.append(f"  > {log}")
        context_parts.append("")
        context_parts.append(
            "Produce a well-structured narrative analysis report based on the above data. "
            "Start directly with the analysis — do not preface it."
        )

        prompt = "\n".join(context_parts)

        try:
            response = self.llm.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=4096,
                ),
            )
            synthesized = response.text
            self.state.feedback_log.append(
                "Phase 5: Gemini 2.5 Flash synthesis complete"
            )
            logger.info("Gemini synthesis successful (%d chars)", len(synthesized))
        except Exception as e:
            logger.error("Gemini synthesis failed: %s", e)
            self.state.feedback_log.append(
                f"Gemini synthesis failed, using fallback: {e}"
            )
            synthesized = self._fallback_synthesis(land_records, macro_data)

        self.state.final_response = synthesized

    def _fallback_synthesis(
        self,
        land_records: list,
        macro_data: list,
    ) -> str:
        """Fallback when Gemini API is unavailable."""
        parts = ["Arth-Sutradhar Analysis Report (Fallback)", "=" * 40, ""]
        parts.append(f"Query: {self.state.user_query}")
        parts.append(f"Iterations: {self.state.iteration_count}")
        parts.append("")

        if land_records:
            parts.append("--- Land Records ---")
            parts.append(self.bq_tool.format_results(land_records))
            parts.append("")

        if macro_data:
            parts.append("--- Macroeconomic Data ---")
            parts.append(self.mcp_tool.format_data(macro_data))
            parts.append("")

        parts.append("--- Agent Reasoning Log ---")
        for log in self.state.feedback_log:
            parts.append(f"  > {log}")

        return "\n".join(parts)
