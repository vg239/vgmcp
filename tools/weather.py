"""Current conditions tools."""

from mcp.server.fastmcp import FastMCP

from data.static import CURRENT, SUPPORTED_CITIES


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_cities() -> str:
        """List all cities that have weather data available."""
        lines = [f"  • {city.title()}" for city in SUPPORTED_CITIES]
        return "Supported cities:\n" + "\n".join(lines)

    @mcp.tool()
    def get_weather(city: str) -> str:
        """
        Get current weather conditions for a city.

        Args:
            city: City name in lowercase (e.g. 'bangalore', 'mumbai').
                  Call list_cities to see all supported cities.
        """
        key = city.lower().strip()
        if key not in CURRENT:
            available = ", ".join(SUPPORTED_CITIES)
            return f"No data for '{city}'. Supported cities: {available}."

        w = CURRENT[key]
        return (
            f"Current weather in {key.title()}\n"
            f"  Temperature : {w['temperature_c']}°C  (feels like {w['feels_like_c']}°C)\n"
            f"  Condition   : {w['condition']}\n"
            f"  Humidity    : {w['humidity_pct']}%\n"
            f"  Wind        : {w['wind_kmh']} km/h {w['wind_dir']}\n"
            f"  UV Index    : {w['uv_index']}\n"
            f"  Visibility  : {w['visibility_km']} km\n"
            f"  Pressure    : {w['pressure_hpa']} hPa"
        )
