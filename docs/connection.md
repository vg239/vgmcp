# MCP Streamable HTTP — Connection Lifecycle & Client Integration

This document describes exactly what happens on the wire when a client connects to this server. It covers the full lifecycle from TCP handshake to tool result, and shows how to integrate from any client — Claude Code, a Python script, or a raw curl session.

---

## Transport overview

This server uses **Streamable HTTP** (MCP spec 2025-03-26), not the older SSE transport and not stdio.

| Transport | How it works | When to use |
|-----------|-------------|-------------|
| **stdio** | Client spawns server as a subprocess; JSON-RPC over stdin/stdout | Local-only, single client |
| **SSE (legacy)** | Two HTTP connections: POST for client→server, GET /sse for server→client | Older MCP clients |
| **Streamable HTTP** | Single POST endpoint; server replies inline (JSON) or as SSE stream | Multi-client, deployable |

Streamable HTTP is the current standard. One endpoint (`POST /mcp`) handles everything. The server may respond with `Content-Type: application/json` for short replies or `Content-Type: text/event-stream` for long-running operations.

---

## Full lifecycle — annotated

```
CLIENT                                  SERVER (vgmcp)
  │                                         │
  │  ── TCP connect → 127.0.0.1:8000 ──→   │  (kernel accepts, uvicorn accepts)
  │                                         │
  │  POST /mcp                              │
  │  Content-Type: application/json         │
  │  {                                      │
  │    "jsonrpc": "2.0",                    │
  │    "id": 1,                             │
  │    "method": "initialize",              │
  │    "params": {                          │
  │      "protocolVersion": "2024-11-05",   │
  │      "capabilities": {},               │
  │      "clientInfo": {                    │
  │        "name": "claude-code",           │
  │        "version": "1.x"                 │
  │      }                                  │
  │    }                                    │
  │  }                                      │
  │                                         │  FastMCP validates protocol version,
  │                                         │  creates a session, returns session ID
  │  ←─── HTTP 200 ────────────────────────  │
  │  mcp-session-id: abc123def456           │  ← MUST save this header
  │  {                                      │
  │    "jsonrpc": "2.0",                    │
  │    "id": 1,                             │
  │    "result": {                          │
  │      "protocolVersion": "2024-11-05",   │
  │      "capabilities": {                  │
  │        "tools": {}                      │
  │      },                                 │
  │      "serverInfo": {                    │
  │        "name": "weather-server",        │
  │        "version": "1.0.0"               │
  │      }                                  │
  │    }                                    │
  │  }                                      │
  │                                         │
  │  POST /mcp                              │
  │  mcp-session-id: abc123def456           │  ← required on ALL subsequent requests
  │  { "method": "tools/list", ... }        │
  │                                         │
  │  ←─── HTTP 200 ────────────────────────  │
  │  {                                      │
  │    "result": {                          │
  │      "tools": [                         │
  │        { "name": "list_cities",         │
  │          "description": "List all ...", │
  │          "inputSchema": { ... } },      │
  │        { "name": "get_weather", ... },  │
  │        { "name": "get_forecast", ... }, │
  │        { "name": "get_alerts", ... },   │
  │        { "name": "get_cities_with_alerts", ... }
  │      ]                                  │
  │    }                                    │
  │  }                                      │
  │                                         │
  │  POST /mcp                              │
  │  mcp-session-id: abc123def456           │
  │  {                                      │
  │    "method": "tools/call",              │
  │    "params": {                          │
  │      "name": "get_weather",             │
  │      "arguments": { "city": "mumbai" } │
  │    }                                    │
  │  }                                      │
  │                                         │  FastMCP dispatches to get_weather()
  │                                         │  in tools/weather.py, executes it,
  │                                         │  wraps result in JSON-RPC envelope
  │  ←─── HTTP 200 ────────────────────────  │
  │  {                                      │
  │    "result": {                          │
  │      "content": [                       │
  │        {                                │
  │          "type": "text",                │
  │          "text": "Current weather in Mumbai\n  Temperature : 32°C..."
  │        }                                │
  │      ]                                  │
  │    }                                    │
  │  }                                      │
  │                                         │
  │  (repeat tools/call for more tools)     │
  │                                         │
  │  POST /mcp                              │
  │  mcp-session-id: abc123def456           │
  │  { "method": "shutdown" }              │  ← optional; client may just close TCP
  │                                         │
  │  ←─── HTTP 200 ────────────────────────  │
  │  TCP FIN / close                        │
```

---

## Key protocol rules

**Session ID is mandatory after initialize.**
Every request after the `initialize` call must include the `mcp-session-id` header. The server will reject requests with a 4xx error if it is missing (when `stateless_http=False`).

**`initialize` must be the first call.**
The server rejects `tools/list` or `tools/call` before initialization completes.

**Each POST is a full HTTP round-trip.**
Unlike SSE (which keeps a long-lived GET connection open), Streamable HTTP opens a new TCP connection (or reuses one from the keep-alive pool) per request. The session is tracked by the header, not the TCP connection.

**The server can stream back SSE for long operations.**
If a tool call takes a long time, FastMCP may respond with `Content-Type: text/event-stream` and send `data:` lines as the result is produced. The client must handle both response types.

---

## Integrating from a Python client

```python
import httpx
import json

BASE = "http://127.0.0.1:8000/mcp"
HEADERS = {"Content-Type": "application/json"}

def rpc(session_id: str | None, method: str, params: dict = {}, id: int = 1) -> dict:
    h = {**HEADERS}
    if session_id:
        h["mcp-session-id"] = session_id
    body = {"jsonrpc": "2.0", "id": id, "method": method, "params": params}
    resp = httpx.post(BASE, headers=h, json=body, timeout=10)
    resp.raise_for_status()
    return resp.headers.get("mcp-session-id"), resp.json()

# 1. Initialize
session_id, init_result = rpc(None, "initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "my-client", "version": "0.1"},
})
print("Session:", session_id)

# 2. List tools
_, tools_result = rpc(session_id, "tools/list", id=2)
for tool in tools_result["result"]["tools"]:
    print(f"  - {tool['name']}: {tool['description'][:60]}")

# 3. Call a tool
_, call_result = rpc(session_id, "tools/call", {
    "name": "get_weather",
    "arguments": {"city": "bangalore"},
}, id=3)
print(call_result["result"]["content"][0]["text"])
```

---

## Integrating from curl (manual testing)

```bash
# Step 1 — initialize and capture the session ID
SESSION=$(curl -si -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0","id":1,"method":"initialize",
    "params":{
      "protocolVersion":"2024-11-05",
      "capabilities":{},
      "clientInfo":{"name":"curl","version":"0"}
    }
  }' | grep -i "mcp-session-id" | awk '{print $2}' | tr -d '\r')

echo "Session ID: $SESSION"

# Step 2 — list tools
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-session-id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | jq '.result.tools[].name'

# Step 3 — call get_weather
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-session-id: $SESSION" \
  -d '{
    "jsonrpc":"2.0","id":3,"method":"tools/call",
    "params":{"name":"get_weather","arguments":{"city":"delhi"}}
  }' | jq -r '.result.content[0].text'
```

---

## Integrating via Claude Code (`.mcp.json`)

Claude Code acts as an MCP client. It reads `.mcp.json` in the project root, connects to registered servers at startup, runs `initialize` + `tools/list`, and then stores tool names as deferred tools. When the model needs a tool, Claude Code sends `tools/call` and returns the result as a tool result block.

```
Claude Code binary
  │
  ├─ reads .mcp.json
  ├─ POST /mcp  initialize  ──────────────────→  vgmcp server
  ├─ POST /mcp  tools/list  ──────────────────→
  │             ← {tools: [{name:"get_weather",...}, ...]}
  │
  │  [model decides to call get_weather("mumbai")]
  │
  ├─ POST /mcp  tools/call get_weather  ──────→
  │             ← {content:[{type:"text",text:"..."}]}
  │
  └─ injects tool result into next API call to Anthropic
```

The server does **not** talk to Anthropic directly. Claude Code is the bridge: it takes tool results from the MCP server and feeds them back into the conversation context sent to the model.

---

## Connecting a remote client (deploying beyond localhost)

Currently `config.py` binds to `127.0.0.1`, which only accepts local connections. To accept external clients:

```bash
# bind to all interfaces
MCP_HOST=0.0.0.0 python server.py
```

For production deployments you should add:

1. **TLS** — put nginx or caddy in front, terminate SSL there, proxy to `127.0.0.1:8000`.
2. **Authentication** — add a shared secret or API key check. FastMCP supports ASGI middleware:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("x-api-key") != os.environ["API_KEY"]:
            from starlette.responses import Response
            return Response("Unauthorized", status_code=401)
        return await call_next(request)

# In build_server(), after creating mcp:
mcp.app.add_middleware(ApiKeyMiddleware)
```

3. **Update the client config** to pass the key:

```json
{
  "mcpServers": {
    "weather": {
      "type": "http",
      "url": "https://your-domain.com/mcp",
      "headers": {
        "x-api-key": "${WEATHER_API_KEY}"
      }
    }
  }
}
```

---

## Troubleshooting connection issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ConnectionRefused` at startup | Server not running | `python server.py` first |
| `Failed to reconnect` in `/mcp` | Server restarted, old session gone | `/mcp` again to re-initialize |
| `406 Not Acceptable` on initialize | Correct — means server is alive | Send correct `Content-Type: application/json` |
| Tools don't appear after `/mcp` | `enableAllProjectMcpServers` not set | Add `.claude/settings.json` with the flag |
| 4xx on `tools/call` | Missing `mcp-session-id` header | Run initialize first, pass the returned header |
| Tool returns error string | Tool function raised an exception | Check server logs (`/tmp/weather_mcp_http.log`) |
