"""
Server configuration.
All values can be overridden with environment variables:
  MCP_HOST, MCP_PORT, MCP_LOG_LEVEL
"""

import os

HOST = os.environ.get("MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCP_PORT", "8000"))
LOG_LEVEL = os.environ.get("MCP_LOG_LEVEL", "info")

# FastMCP mounts the MCP endpoint here. The .mcp.json url must end with this path.
MCP_PATH = "/mcp"
