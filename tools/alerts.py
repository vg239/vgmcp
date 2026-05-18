"""Weather alert tools."""

from mcp.server.fastmcp import FastMCP

from data.static import ALERTS, SUPPORTED_CITIES

SEVERITY_EMOJI = {
    "low": "🟡",
    "moderate": "🟠",
    "high": "🔴",
    "extreme": "🚨",
}


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_alerts(city: str) -> str:
        """
        Get active weather alerts and advisories for a city.

        Args:
            city: City name in lowercase (e.g. 'delhi'). Call list_cities for options.
        """
        key = city.lower().strip()
        if key not in ALERTS:
            available = ", ".join(SUPPORTED_CITIES)
            return f"No alert data for '{city}'. Supported cities: {available}."

        alerts = ALERTS[key]
        if not alerts:
            return f"No active weather alerts for {key.title()}. All clear."

        lines = [f"Active alerts for {key.title()} ({len(alerts)} alert(s)):"]
        for alert in alerts:
            icon = SEVERITY_EMOJI.get(alert["severity"], "⚠️")
            lines.append(
                f"\n  {icon} [{alert['severity'].upper()}] {alert['title']}\n"
                f"     {alert['description']}\n"
                f"     Valid until: {alert['valid_until']}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def get_cities_with_alerts() -> str:
        """List all cities that currently have active weather alerts."""
        cities_with_alerts = [city for city, alerts in ALERTS.items() if alerts]
        if not cities_with_alerts:
            return "No cities have active weather alerts right now."

        lines = ["Cities with active alerts:"]
        for city in sorted(cities_with_alerts):
            count = len(ALERTS[city])
            severities = ", ".join(a["severity"] for a in ALERTS[city])
            lines.append(f"  • {city.title():<14} {count} alert(s)  [{severities}]")
        return "\n".join(lines)
