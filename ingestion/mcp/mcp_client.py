"""
e-Sankhyiki MCP Client for Arth-Sutradhar.

Wraps the four-step MCP protocol from MoSPI's e-Sankhyiki portal:
  1. list_datasets()    - Discover available economic indicators
  2. get_indicators()   - Identify specific metrics
  3. get_metadata()     - Retrieve valid filter values
  4. get_data()         - Fetch precise numerical rows

Usage:
    client = MoSPIClient()
    datasets = client.list_datasets()
    indicators = client.get_indicators("CPIALRL")
    metadata = client.get_metadata("CPIALRL", indicator_id="...")
    data = client.get_data("CPIALRL", indicator_id="...", state_code="...")
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MCPResponse:
    success: bool
    data: list[dict[str, Any]] | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class MoSPIClient:
    """
    Client for the MoSPI e-Sankhyiki MCP server.

    Connects to a running FastMCP server instance that wraps the
    official MoSPI MCP endpoint. The server URL is configurable.
    """

    def __init__(self, server_url: str = "http://localhost:8000/mcp"):
        self.server_url = server_url
        self._session_token: str | None = None

    def _call_tool(self, tool_name: str, params: dict[str, Any] | None = None) -> MCPResponse:
        """
        Simulates an MCP tool invocation against the e-Sankhyiki server.

        In production, this sends a JSON-RPC request to the FastMCP server.
        For now, returns the expected interface contract.
        """
        logger.info("MCP call: %s with params=%s", tool_name, params)
        try:
            import httpx
            payload = {
                "jsonrpc": "2.0",
                "method": f"tools/{tool_name}",
                "params": params or {},
                "id": 1,
            }
            headers = {"Content-Type": "application/json"}
            if self._session_token:
                headers["Authorization"] = f"Bearer {self._session_token}"

            response = httpx.post(
                self.server_url,
                content=json.dumps(payload),
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return MCPResponse(success=True, data=result.get("result"))
        except ImportError:
            logger.warning("httpx not installed; using mock mode")
            return self._mock_call(tool_name, params)
        except Exception as e:
            logger.error("MCP call failed: %s", e)
            return MCPResponse(success=False, error=str(e))

    def _mock_call(self, tool_name: str, params: dict[str, Any] | None) -> MCPResponse:
        """Mock responses when the MCP server is not available."""
        mocks = {
            "list_datasets": {
                "datasets": [
                    {"id": "PLFS", "name": "Periodic Labour Force Survey", "type": "employment"},
                    {"id": "CPIALRL", "name": "CPI for Agricultural/Rural Labourers", "type": "inflation"},
                    {"id": "ASUSE", "name": "Annual Survey of Unincorporated Enterprises", "type": "enterprise"},
                ]
            },
            "get_indicators": {
                "indicators": [
                    {"id": "IND_001", "name": "Rural Wage Rate", "dataset": "PLFS"},
                    {"id": "IND_002", "name": "CPI-Rural General Index", "dataset": "CPIALRL"},
                    {"id": "IND_003", "name": "CPI-Agricultural Labourers Index", "dataset": "CPIALRL"},
                    {"id": "IND_004", "name": "Informal Sector Employment", "dataset": "ASUSE"},
                ]
            },
            "get_metadata": {
                "filters": {
                    "state_code": {"type": "string", "description": "2-digit state code", "example": "24"},
                    "financial_year": {"type": "string", "description": "Format: YYYY-YY", "example": "2024-25"},
                    "sector": {"type": "string", "enum": ["Rural", "Urban", "Combined"]},
                }
            },
            "get_data": {
                "rows": [
                    {"state_code": "24", "financial_year": "2024-25", "sector": "Rural", "value": 198.5, "unit": "index"},
                ]
            },
        }
        result = mocks.get(tool_name, {"error": f"Unknown tool: {tool_name}"})
        return MCPResponse(success=True, data=[result])

    # Public API — mirrors the 4-step MCP protocol

    def list_datasets(self) -> MCPResponse:
        """Step 1: Discover available datasets."""
        return self._call_tool("list_datasets")

    def get_indicators(self, dataset_id: str) -> MCPResponse:
        """Step 2: Get indicators for a specific dataset."""
        return self._call_tool("get_indicators", {"dataset_id": dataset_id})

    def get_metadata(self, dataset_id: str, indicator_id: str) -> MCPResponse:
        """Step 3: Get valid filter params for a specific indicator."""
        return self._call_tool("get_metadata", {
            "dataset_id": dataset_id,
            "indicator_id": indicator_id,
        })

    def get_data(self, dataset_id: str, indicator_id: str, **filters) -> MCPResponse:
        """Step 4: Fetch actual data with applied filters."""
        params = {"dataset_id": dataset_id, "indicator_id": indicator_id, **filters}
        return self._call_tool("get_data", params)

    # Convenience queries for the ADK agent

    def get_cpialrl_data(self, state_code: str, financial_year: str = "2024-25") -> MCPResponse:
        """Quick access to CPI for Agricultural Labourers data."""
        return self.get_data(
            "CPIALRL", "IND_003",
            state_code=state_code,
            financial_year=financial_year,
        )

    def get_plfs_wage_data(self, state_code: str, financial_year: str = "2024-25") -> MCPResponse:
        """Quick access to rural wage data."""
        return self.get_data(
            "PLFS", "IND_001",
            state_code=state_code,
            financial_year=financial_year,
        )
