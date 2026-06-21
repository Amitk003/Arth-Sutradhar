"""
Runner script for the e-Sankhyiki MCP server.

Clones and starts the official MoSPI MCP server locally.
"""

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MCP_REPO_URL = "https://github.com/nso-india/esankhyiki-mcp.git"
MCP_DIR = Path(__file__).parent / "esankhyiki-mcp"


def ensure_repo():
    if MCP_DIR.exists():
        logger.info("MCP repo already exists at %s", MCP_DIR)
        return
    logger.info("Cloning MoSPI MCP repo from %s", MCP_REPO_URL)
    subprocess.run(["git", "clone", MCP_REPO_URL, str(MCP_DIR)], check=True)
    logger.info("Installing Python dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(MCP_DIR / "requirements.txt")],
        check=True,
    )


def start_server():
    ensure_repo()
    logger.info("Starting e-Sankhyiki MCP server...")
    subprocess.run(
        [sys.executable, "-m", "mcp", "run", str(MCP_DIR / "mospi_server.py")],
        check=True,
    )


if __name__ == "__main__":
    start_server()
