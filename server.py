"""
Weather MCP Server — Streamable HTTP transport
===============================================
Transport: Streamable HTTP (MCP spec 2025-03-26)
  • Single POST /mcp endpoint — bidirectional JSON-RPC
  • Client sends requests via POST body
  • Server replies inline (JSON) or as an SSE stream for long responses
  • No separate GET /sse connection needed (unlike older SSE transport)

Run:
  python server.py
  MCP_PORT=9000 python server.py

Register in .mcp.json (project root):
  {
    "mcpServers": {
      "weather": {
        "type": "http",
        "url": "http://127.0.0.1:8000/mcp"
      }
    }
  }
"""

import sys
import os

# Allow `from data.xxx import ...` and `from tools.xxx import ...`
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from mcp.server.fastmcp import FastMCP

import config
from tools import weather, forecast, alerts


def build_server() -> FastMCP:
    mcp = FastMCP(
        name="weather-server",
        host=config.HOST,
        port=config.PORT,
        streamable_http_path=config.MCP_PATH,
        # stateless_http=True means no session state across requests — simpler
        # and scales horizontally. Set False if you need multi-turn session state.
        stateless_http=False,
    )

    # Register tools from each module
    weather.register(mcp)
    forecast.register(mcp)
    alerts.register(mcp)

    return mcp


mcp = build_server()

if __name__ == "__main__":
    print(f"Starting Weather MCP Server (Streamable HTTP)")
    print(f"  Endpoint : http://{config.HOST}:{config.PORT}{config.MCP_PATH}")
    print(f"  Tools    : list_cities, get_weather, get_forecast, get_alerts, get_cities_with_alerts")
    print()
    mcp.run(transport="streamable-http")
