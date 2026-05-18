"""
Static weather data for all supported cities.
In a real server, this layer would call an external API (OpenWeatherMap, etc.).
"""

from typing import TypedDict


class CityWeather(TypedDict):
    temperature_c: float
    feels_like_c: float
    condition: str
    humidity_pct: int
    wind_kmh: float
    wind_dir: str
    uv_index: int
    visibility_km: float
    pressure_hpa: int


class ForecastDay(TypedDict):
    date: str
    high_c: float
    low_c: float
    condition: str
    rain_chance_pct: int


class Alert(TypedDict):
    severity: str   # "low" | "moderate" | "high" | "extreme"
    title: str
    description: str
    valid_until: str


CURRENT: dict[str, CityWeather] = {
    "bangalore": {
        "temperature_c": 28.0,
        "feels_like_c": 31.0,
        "condition": "Partly Cloudy",
        "humidity_pct": 65,
        "wind_kmh": 12.0,
        "wind_dir": "NE",
        "uv_index": 7,
        "visibility_km": 10.0,
        "pressure_hpa": 1013,
    },
    "mumbai": {
        "temperature_c": 32.0,
        "feels_like_c": 38.0,
        "condition": "Hot and Humid",
        "humidity_pct": 82,
        "wind_kmh": 18.0,
        "wind_dir": "SW",
        "uv_index": 9,
        "visibility_km": 8.0,
        "pressure_hpa": 1008,
    },
    "delhi": {
        "temperature_c": 41.0,
        "feels_like_c": 44.0,
        "condition": "Sunny, Very Hot",
        "humidity_pct": 30,
        "wind_kmh": 8.0,
        "wind_dir": "NW",
        "uv_index": 10,
        "visibility_km": 7.0,
        "pressure_hpa": 1000,
    },
    "chennai": {
        "temperature_c": 35.0,
        "feels_like_c": 40.0,
        "condition": "Humid and Sunny",
        "humidity_pct": 78,
        "wind_kmh": 15.0,
        "wind_dir": "SE",
        "uv_index": 8,
        "visibility_km": 9.0,
        "pressure_hpa": 1010,
    },
    "hyderabad": {
        "temperature_c": 36.0,
        "feels_like_c": 39.0,
        "condition": "Clear Sky",
        "humidity_pct": 45,
        "wind_kmh": 10.0,
        "wind_dir": "W",
        "uv_index": 9,
        "visibility_km": 12.0,
        "pressure_hpa": 1005,
    },
    "kolkata": {
        "temperature_c": 33.0,
        "feels_like_c": 37.0,
        "condition": "Hazy",
        "humidity_pct": 72,
        "wind_kmh": 14.0,
        "wind_dir": "S",
        "uv_index": 7,
        "visibility_km": 6.0,
        "pressure_hpa": 1009,
    },
    "pune": {
        "temperature_c": 29.0,
        "feels_like_c": 32.0,
        "condition": "Light Rain",
        "humidity_pct": 70,
        "wind_kmh": 16.0,
        "wind_dir": "W",
        "uv_index": 4,
        "visibility_km": 8.0,
        "pressure_hpa": 1012,
    },
}

FORECAST: dict[str, list[ForecastDay]] = {
    "bangalore": [
        {"date": "Day 1", "high_c": 29, "low_c": 19, "condition": "Partly Cloudy", "rain_chance_pct": 20},
        {"date": "Day 2", "high_c": 28, "low_c": 18, "condition": "Cloudy",        "rain_chance_pct": 40},
        {"date": "Day 3", "high_c": 26, "low_c": 17, "condition": "Light Rain",    "rain_chance_pct": 70},
        {"date": "Day 4", "high_c": 27, "low_c": 18, "condition": "Partly Cloudy", "rain_chance_pct": 30},
        {"date": "Day 5", "high_c": 30, "low_c": 20, "condition": "Sunny",         "rain_chance_pct": 10},
    ],
    "mumbai": [
        {"date": "Day 1", "high_c": 33, "low_c": 26, "condition": "Hot and Humid", "rain_chance_pct": 15},
        {"date": "Day 2", "high_c": 31, "low_c": 25, "condition": "Thunderstorm",  "rain_chance_pct": 80},
        {"date": "Day 3", "high_c": 29, "low_c": 24, "condition": "Heavy Rain",    "rain_chance_pct": 90},
        {"date": "Day 4", "high_c": 30, "low_c": 25, "condition": "Light Rain",    "rain_chance_pct": 60},
        {"date": "Day 5", "high_c": 32, "low_c": 26, "condition": "Partly Cloudy", "rain_chance_pct": 20},
    ],
    "delhi": [
        {"date": "Day 1", "high_c": 42, "low_c": 28, "condition": "Sunny, Very Hot", "rain_chance_pct": 5},
        {"date": "Day 2", "high_c": 43, "low_c": 29, "condition": "Heatwave",         "rain_chance_pct": 5},
        {"date": "Day 3", "high_c": 41, "low_c": 27, "condition": "Partly Cloudy",   "rain_chance_pct": 15},
        {"date": "Day 4", "high_c": 39, "low_c": 26, "condition": "Dusty Wind",      "rain_chance_pct": 10},
        {"date": "Day 5", "high_c": 38, "low_c": 25, "condition": "Partly Cloudy",   "rain_chance_pct": 20},
    ],
    "chennai": [
        {"date": "Day 1", "high_c": 36, "low_c": 27, "condition": "Humid and Sunny", "rain_chance_pct": 10},
        {"date": "Day 2", "high_c": 35, "low_c": 26, "condition": "Partly Cloudy",   "rain_chance_pct": 25},
        {"date": "Day 3", "high_c": 34, "low_c": 25, "condition": "Light Rain",      "rain_chance_pct": 50},
        {"date": "Day 4", "high_c": 35, "low_c": 26, "condition": "Humid",           "rain_chance_pct": 30},
        {"date": "Day 5", "high_c": 36, "low_c": 27, "condition": "Sunny",           "rain_chance_pct": 10},
    ],
    "hyderabad": [
        {"date": "Day 1", "high_c": 37, "low_c": 24, "condition": "Clear Sky",     "rain_chance_pct": 5},
        {"date": "Day 2", "high_c": 36, "low_c": 23, "condition": "Sunny",         "rain_chance_pct": 5},
        {"date": "Day 3", "high_c": 34, "low_c": 22, "condition": "Partly Cloudy", "rain_chance_pct": 20},
        {"date": "Day 4", "high_c": 33, "low_c": 22, "condition": "Light Rain",    "rain_chance_pct": 45},
        {"date": "Day 5", "high_c": 35, "low_c": 23, "condition": "Clear Sky",     "rain_chance_pct": 10},
    ],
    "kolkata": [
        {"date": "Day 1", "high_c": 34, "low_c": 26, "condition": "Hazy",          "rain_chance_pct": 20},
        {"date": "Day 2", "high_c": 33, "low_c": 25, "condition": "Partly Cloudy", "rain_chance_pct": 35},
        {"date": "Day 3", "high_c": 31, "low_c": 24, "condition": "Thunderstorm",  "rain_chance_pct": 75},
        {"date": "Day 4", "high_c": 30, "low_c": 24, "condition": "Light Rain",    "rain_chance_pct": 60},
        {"date": "Day 5", "high_c": 32, "low_c": 25, "condition": "Cloudy",        "rain_chance_pct": 40},
    ],
    "pune": [
        {"date": "Day 1", "high_c": 30, "low_c": 20, "condition": "Light Rain",    "rain_chance_pct": 65},
        {"date": "Day 2", "high_c": 28, "low_c": 19, "condition": "Heavy Rain",    "rain_chance_pct": 85},
        {"date": "Day 3", "high_c": 27, "low_c": 18, "condition": "Light Rain",    "rain_chance_pct": 70},
        {"date": "Day 4", "high_c": 29, "low_c": 19, "condition": "Partly Cloudy", "rain_chance_pct": 30},
        {"date": "Day 5", "high_c": 31, "low_c": 21, "condition": "Sunny",         "rain_chance_pct": 10},
    ],
}

ALERTS: dict[str, list[Alert]] = {
    "bangalore": [],
    "mumbai": [
        {
            "severity": "high",
            "title": "Thunderstorm Warning",
            "description": "Severe thunderstorms expected in the next 48 hours. Avoid low-lying coastal areas.",
            "valid_until": "Day 3, 06:00 IST",
        }
    ],
    "delhi": [
        {
            "severity": "extreme",
            "title": "Heatwave Alert",
            "description": "Temperatures exceeding 42°C forecast for the next 2 days. Stay indoors, stay hydrated.",
            "valid_until": "Day 2, 20:00 IST",
        },
        {
            "severity": "moderate",
            "title": "Dust Storm Advisory",
            "description": "Strong winds may cause reduced visibility due to dust. Wear protective eyewear.",
            "valid_until": "Day 4, 12:00 IST",
        },
    ],
    "chennai": [],
    "hyderabad": [],
    "kolkata": [
        {
            "severity": "moderate",
            "title": "Pre-Monsoon Thunderstorm Watch",
            "description": "Pre-monsoon convective activity likely. Expect sudden heavy showers on Day 3.",
            "valid_until": "Day 3, 23:59 IST",
        }
    ],
    "pune": [
        {
            "severity": "low",
            "title": "Heavy Rainfall Advisory",
            "description": "Persistent rainfall expected. Waterlogging possible in low-lying areas.",
            "valid_until": "Day 3, 18:00 IST",
        }
    ],
}

SUPPORTED_CITIES = sorted(CURRENT.keys())
