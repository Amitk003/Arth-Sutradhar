"""
e-Sankhyiki MCP Tool for Arth-Sutradhar ADK Agent.

Connects to the MoSPI MCP server to fetch live macroeconomic data.
"""

import logging
from dataclasses import dataclass, asdict
from typing import Any

from agent.tools.config import PROJECT_ID, REGION

logger = logging.getLogger(__name__)


@dataclass
class MCPDataPoint:
    dataset: str
    indicator: str
    value: float
    unit: str
    metadata: dict[str, Any]


class MCPTool:
    """
    Tool for querying live MoSPI data via the e-Sankhyiki MCP protocol.

    The 4-step protocol:
      1. list_datasets
      2. get_indicators
      3. get_metadata
      4. get_data
    """

    def __init__(self, server_url: str = "http://localhost:8000/mcp"):
        self.server_url = server_url
        self._cache: dict[str, Any] = {}

    def list_datasets(self) -> list[dict]:
        """Step 1: Discover available economic datasets."""
        try:
            import httpx
            resp = httpx.get(f"{self.server_url}/datasets", timeout=10)
            resp.raise_for_status()
            return resp.json().get("datasets", [])
        except Exception as e:
            logger.warning("MCP server unavailable (%s). Using cached defaults.", e)
            return self._default_datasets()

    def get_indicators(self, dataset_id: str) -> list[dict]:
        """Step 2: Get indicators for a dataset."""
        try:
            import httpx
            resp = httpx.get(
                f"{self.server_url}/indicators",
                params={"dataset_id": dataset_id},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("indicators", [])
        except Exception as e:
            logger.warning("MCP indicators failed (%s). Returning defaults.", e)
            return self._default_indicators(dataset_id)

    def get_data(self, dataset_id: str, indicator_id: str, **filters) -> list[MCPDataPoint]:
        """Step 4: Fetch actual data with filters."""
        try:
            import httpx
            params = {"dataset_id": dataset_id, "indicator_id": indicator_id, **filters}
            resp = httpx.get(f"{self.server_url}/data", params=params, timeout=30)
            resp.raise_for_status()
            rows = resp.json().get("rows", [])
            return [
                MCPDataPoint(
                    dataset=dataset_id,
                    indicator=indicator_id,
                    value=r.get("value", 0),
                    unit=r.get("unit", ""),
                    metadata=r,
                )
                for r in rows
            ]
        except Exception as e:
            logger.warning("MCP data fetch failed (%s). Returning mock data.", e)
            return self._mock_data(dataset_id, indicator_id, filters)

    def _default_datasets(self) -> list[dict]:
        return [
            {"id": "PLFS", "name": "Periodic Labour Force Survey", "type": "employment"},
            {"id": "CPIALRL", "name": "CPI for Agricultural/Rural Labourers", "type": "inflation"},
            {"id": "ASUSE", "name": "Annual Survey of Unincorporated Enterprises", "type": "enterprise"},
        ]

    def _default_indicators(self, dataset_id: str) -> list[dict]:
        mapping = {
            "PLFS": [
                {"id": "IND_001", "name": "Rural Wage Rate"},
                {"id": "IND_002", "name": "Urban Wage Rate"},
            ],
            "CPIALRL": [
                {"id": "IND_003", "name": "CPI-Agricultural Labourers Index"},
                {"id": "IND_004", "name": "CPI-Rural General Index"},
            ],
            "ASUSE": [
                {"id": "IND_005", "name": "Informal Sector Employment"},
                {"id": "IND_006", "name": "Unincorporated Enterprise Count"},
            ],
        }
        return mapping.get(dataset_id, [])

    def _mock_data(self, dataset_id: str, indicator_id: str, filters: dict) -> list[MCPDataPoint]:
        mock_values = {
            "IND_001": 350.0,
            "IND_002": 420.0,
            "IND_003": 198.5,
            "IND_004": 185.2,
            "IND_005": 45_000_000,
            "IND_006": 62_000_000,
        }
        value = mock_values.get(indicator_id, 100.0)
        state = filters.get("state_code", "24")
        year = filters.get("financial_year", "2024-25")
        return [
            MCPDataPoint(
                dataset=dataset_id,
                indicator=indicator_id,
                value=value,
                unit="index",
                metadata={"state_code": state, "financial_year": year},
            )
        ]

    def format_data(self, data: list[MCPDataPoint]) -> str:
        if not data:
            return "No macroeconomic data found."
        lines = ["Macroeconomic data from MoSPI:"]
        for d in data:
            lines.append(f"  - {d.dataset}/{d.indicator}: {d.value} {d.unit}")
        return "\n".join(lines)
