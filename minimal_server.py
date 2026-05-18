"""
Minimal MCP weather server — single file demo.
Run: python minimal_server.py
Endpoint: http://127.0.0.1:8000/mcp
"""

from mcp.server.fastmcp import FastMCP

WEATHER = {
    "bangalore": {"temp": 28, "condition": "Partly Cloudy", "humidity": 65},
    "mumbai":    {"temp": 32, "condition": "Hot and Humid",  "humidity": 82},
    "delhi":     {"temp": 41, "condition": "Sunny, Very Hot","humidity": 30},
    "chennai":   {"temp": 35, "condition": "Humid and Sunny","humidity": 78},
    "pune":      {"temp": 29, "condition": "Light Rain",     "humidity": 70},
}

mcp = FastMCP("minimal-weather", host="127.0.0.1", port=8000, streamable_http_path="/mcp")


@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city (bangalore/mumbai/delhi/chennai/pune)."""
    data = WEATHER.get(city.lower().strip())
    if not data:
        return f"No data for '{city}'. Try: {', '.join(WEATHER)}"
    return f"{city.title()}: {data['temp']}°C, {data['condition']}, humidity {data['humidity']}%"


if __name__ == "__main__":
    print("Minimal MCP server → http://127.0.0.1:8000/mcp")
    mcp.run(transport="streamable-http")
