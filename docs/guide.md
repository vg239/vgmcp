# vgmcp — Project Structure & Developer Guide

This document covers every file in the repo, why it exists, what it does, and exactly how to extend the server with new tools, new data sources, or new transports.

---

## Directory layout

```
vgmcp/
├── server.py            ← entry point; builds and runs the FastMCP app
├── config.py            ← all tuneable values (host, port, path) in one place
├── requirements.txt     ← Python dependencies
├── .gitignore
│
├── tools/               ← one module per logical tool group
│   ├── __init__.py
│   ├── weather.py       ← list_cities, get_weather
│   ├── forecast.py      ← get_forecast
│   └── alerts.py        ← get_alerts, get_cities_with_alerts
│
├── data/                ← data layer (static now, API-backed later)
│   ├── __init__.py
│   └── static.py        ← TypedDicts + CURRENT / FORECAST / ALERTS dicts
│
└── docs/
    ├── guide.md         ← this file
    └── connection.md    ← Streamable HTTP lifecycle & client integration
```

---

## File-by-file breakdown

### `server.py`

The only runnable entry point. Does three things:

1. Adds the project root to `sys.path` so `from data.xxx` and `from tools.xxx` resolve without installing the package.
2. Calls `build_server()`, which creates a `FastMCP` instance and calls each tool module's `register()` function.
3. Calls `mcp.run(transport="streamable-http")`, which starts an uvicorn ASGI server on the configured host/port.

**Why a `build_server()` function instead of top-level code?**
Separating construction from startup lets tests, other scripts, or a future ASGI deployment import `mcp` without side-effects.

```python
mcp = build_server()          # importable — no server started yet
mcp.run(transport="...")      # only runs when you call this
```

The `mcp` module-level name is also needed by ASGI runners (gunicorn, uvicorn programmatic API):
```bash
uvicorn server:mcp --host 0.0.0.0 --port 8000
```

---

### `config.py`

Centralises every value that might change between environments. All three are overridable via environment variables, so you never need to edit code to change the port:

```bash
MCP_PORT=9000 python server.py
MCP_HOST=0.0.0.0 MCP_LOG_LEVEL=debug python server.py
```

`MCP_PATH` is not an env-var because it must match the `.mcp.json` URL suffix and changing it at runtime without updating the client config would break the connection.

---

### `tools/` — Tool modules

Each file in `tools/` follows the same contract:

```python
from mcp.server.fastmcp import FastMCP

def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def my_tool(arg: str) -> str:
        """Docstring becomes the tool description shown to the model."""
        ...
```

`register(mcp)` is called once at startup by `server.py`. The `@mcp.tool()` decorator registers the function as an MCP tool: name = function name, description = docstring, input schema = inferred from type annotations.

**`tools/weather.py`** — `list_cities`, `get_weather`
Reads from `data.static.CURRENT`. `list_cities` takes no arguments and returns a bullet list. `get_weather(city)` normalises the city name to lowercase and returns a formatted conditions string.

**`tools/forecast.py`** — `get_forecast`
`get_forecast(city, days=3)` slices up to 5 days from `data.static.FORECAST`. The `days` parameter has a default, so the model can call it with just a city name.

**`tools/alerts.py`** — `get_alerts`, `get_cities_with_alerts`
`get_alerts(city)` returns all active alerts for a city with severity icons. `get_cities_with_alerts()` takes no arguments and scans the whole `ALERTS` dict — useful for "which cities should I warn about?" queries.

---

### `data/static.py`

Three TypedDicts define the shape of each record:

- `CityWeather` — current conditions (temperature, humidity, wind, …)
- `ForecastDay` — one day of forecast data
- `Alert` — a single advisory with severity, title, description, valid_until

Three top-level dicts hold the actual data:

- `CURRENT: dict[str, CityWeather]` — keyed by lowercase city name
- `FORECAST: dict[str, list[ForecastDay]]` — up to 5 entries per city
- `ALERTS: dict[str, list[Alert]]` — empty list = no alerts

`SUPPORTED_CITIES = sorted(CURRENT.keys())` is derived, not manually maintained, so adding a city to `CURRENT` automatically makes it available everywhere.

---

## How to extend the server

### Add a new tool to an existing module

Open the relevant `tools/*.py` file and add a function inside `register()`:

```python
def register(mcp: FastMCP) -> None:
    # existing tools ...

    @mcp.tool()
    def get_humidity_index(city: str) -> str:
        """Get the perceived humidity comfort level for a city."""
        key = city.lower().strip()
        if key not in CURRENT:
            return f"No data for '{city}'."
        h = CURRENT[key]["humidity_pct"]
        label = "comfortable" if h < 60 else "humid" if h < 80 else "oppressive"
        return f"{key.title()} humidity: {h}% ({label})"
```

No changes needed in `server.py` — `register()` is already called at startup.

---

### Add a new tool module

1. Create `tools/mynewmodule.py` with a `register(mcp: FastMCP) -> None` function.
2. Import and call it in `server.py`:

```python
from tools import weather, forecast, alerts, mynewmodule

def build_server() -> FastMCP:
    mcp = FastMCP(...)
    weather.register(mcp)
    forecast.register(mcp)
    alerts.register(mcp)
    mynewmodule.register(mcp)   # ← add this line
    return mcp
```

---

### Add a new city

Open `data/static.py` and add the city key to `CURRENT`, `FORECAST`, and `ALERTS`:

```python
CURRENT["surat"] = {
    "temperature_c": 34.0,
    "feels_like_c": 38.0,
    "condition": "Hazy Sunshine",
    "humidity_pct": 68,
    "wind_kmh": 13.0,
    "wind_dir": "SW",
    "uv_index": 8,
    "visibility_km": 9.0,
    "pressure_hpa": 1007,
}

FORECAST["surat"] = [
    {"date": "Day 1", "high_c": 35, "low_c": 26, "condition": "Hazy", "rain_chance_pct": 10},
    # ...
]

ALERTS["surat"] = []  # no active alerts
```

`SUPPORTED_CITIES` updates automatically because it is derived from `CURRENT.keys()`.

---

### Replace static data with a live API

The data layer is intentionally isolated in `data/`. To switch to a live API (e.g., OpenWeatherMap):

1. Create `data/api.py` that fetches and returns the same `CityWeather` / `ForecastDay` / `Alert` TypedDicts.
2. Change the imports in the affected tool modules from `data.static` to `data.api`.
3. The tool functions themselves do not change.

```python
# tools/weather.py — only the import changes
from data.api import get_current, SUPPORTED_CITIES   # was: from data.static import CURRENT, SUPPORTED_CITIES
```

---

### Change the transport

The server currently runs Streamable HTTP (`transport="streamable-http"`). To switch:

```python
# stdio — for local Claude Code use via subprocess
mcp.run(transport="stdio")

# SSE — older 2-channel HTTP transport
mcp.run(transport="sse")
```

For stdio you would also update `.mcp.json` from `"type": "http"` to `"type": "stdio"` with a `command` field. See `docs/connection.md` for the full lifecycle comparison.

---

### Make it stateless (horizontal scaling)

In `server.py`, change `stateless_http=False` → `stateless_http=True`. This tells FastMCP not to maintain per-session state, so any replica can handle any request. The trade-off is that multi-turn tool call sequences cannot share state between requests.

```python
mcp = FastMCP(
    ...
    stateless_http=True,   # safe to load-balance across multiple replicas
)
```

---

## Running the server

```bash
# install deps (once)
pip install -r requirements.txt

# start (defaults: 127.0.0.1:8000)
python server.py

# custom port
MCP_PORT=9000 python server.py

# production-grade (multiple workers)
uvicorn server:mcp --host 0.0.0.0 --port 8000 --workers 4
```

Verify it's up:
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}'
# Expect: 200
```

---

## Wiring to Claude Code

Create `.mcp.json` in your project root (one level above `vgmcp/` if that's your working directory):

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

Then create `.claude/settings.json` in the same directory:

```json
{
  "enableAllProjectMcpServers": true
}
```

Start the server, then restart Claude Code (or run `/mcp` to reconnect). The five weather tools will appear as deferred tools in the system reminder.
