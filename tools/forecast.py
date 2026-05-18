"""Multi-day forecast tools."""

from mcp.server.fastmcp import FastMCP

from data.static import FORECAST, SUPPORTED_CITIES


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_forecast(city: str, days: int = 3) -> str:
        """
        Get a multi-day weather forecast for a city.

        Args:
            city: City name in lowercase (e.g. 'bangalore'). Call list_cities for options.
            days: Number of days to forecast (1–5). Defaults to 3.
        """
        key = city.lower().strip()
        if key not in FORECAST:
            available = ", ".join(SUPPORTED_CITIES)
            return f"No forecast data for '{city}'. Supported cities: {available}."

        days = max(1, min(days, 5))
        entries = FORECAST[key][:days]

        lines = [f"{key.title()} — {days}-Day Forecast"]
        for day in entries:
            rain = day["rain_chance_pct"]
            lines.append(
                f"  {day['date']:6s}  {day['high_c']}°C / {day['low_c']}°C  "
                f"{day['condition']:<22}  Rain: {rain}%"
            )
        return "\n".join(lines)
