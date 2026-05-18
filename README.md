# vgmcp — Weather MCP Server

A production-structured MCP (Model Context Protocol) server that exposes Indian city weather data over **Streamable HTTP** transport. Built with [FastMCP](https://github.com/jlowin/fastmcp) and uvicorn.

## Tools exposed

| Tool | Args | Description |
|------|------|-------------|
| `list_cities` | — | List all supported cities |
| `get_weather` | `city` | Current conditions (temp, humidity, wind, UV, …) |
| `get_forecast` | `city`, `days=3` | Multi-day forecast (1–5 days) |
| `get_alerts` | `city` | Active weather alerts and advisories |
| `get_cities_with_alerts` | — | All cities that have active alerts |

Cities: bangalore, chennai, delhi, hyderabad, kolkata, mumbai, pune.

## Quick start

```bash
pip install -r requirements.txt
python server.py
```

Server starts at `http://127.0.0.1:8000/mcp`.

```bash
# verify it's running
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' \
  | jq .result.serverInfo
```

## Wire to Claude Code

1. In your project root, create `.mcp.json`:

```json
{
  "mcpServers": {
    "weather": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

2. Create `.claude/settings.json`:

```json
{
  "enableAllProjectMcpServers": true
}
```

3. Start the server, then restart Claude Code or run `/mcp`.

## Docs

- [`docs/guide.md`](docs/guide.md) — full project structure, file-by-file breakdown, and how to add tools, cities, or swap the data layer
- [`docs/connection.md`](docs/connection.md) — complete Streamable HTTP lifecycle, annotated wire diagrams, Python/curl integration examples, and production deployment notes

## Environment variables

| Variable | Default | Effect |
|----------|---------|--------|
| `MCP_HOST` | `127.0.0.1` | Bind address |
| `MCP_PORT` | `8000` | Listen port |
| `MCP_LOG_LEVEL` | `info` | uvicorn log level |

## Production

```bash
# bind to all interfaces for remote clients
MCP_HOST=0.0.0.0 python server.py

# multi-worker via uvicorn directly
uvicorn server:mcp --host 0.0.0.0 --port 8000 --workers 4
```

Add TLS termination (nginx/caddy) and API key middleware before exposing publicly. See [`docs/connection.md`](docs/connection.md#connecting-a-remote-client-deploying-beyond-localhost) for the full setup.
