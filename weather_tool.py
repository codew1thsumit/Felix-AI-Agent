import requests
from langchain.tools import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_location(city: str):
    response = requests.get(
        GEOCODING_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("results", [])

    if not results:
        return None

    return results[0]


def weather_description(code: int) -> str:
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return descriptions.get(code, "Unknown weather")


@tool
def get_current_weather(city: str) -> str:
    """Get the current weather for a city."""

    print(f"\n  🌤️ Weather searching: {city}")

    location = get_location(city)

    if not location:
        return f"Could not find the location: {city}"

    latitude = location["latitude"]
    longitude = location["longitude"]

    weather_response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto",
        },
        timeout=10,
    )

    weather_response.raise_for_status()

    data = weather_response.json()
    current = data["current"]

    description = weather_description(
        current["weather_code"]
    )

    print("  🌤️ Weather: results found")

    return (
        f"🌤️ **Weather in {location['name']}, "
        f"{location.get('country', '')}**\n\n"
        f"🌥️ **Condition:** {description}\n"
        f"🌡️ **Temperature:** {current['temperature_2m']}°C\n"
        f"🥵 **Feels like:** {current['apparent_temperature']}°C\n"
        f"💧 **Humidity:** {current['relative_humidity_2m']}%\n"
        f"🌧️ **Precipitation:** {current['precipitation']} mm\n"
        f"💨 **Wind speed:** {current['wind_speed_10m']} km/h\n"
        f"🕐 **Local time:** {current['time']}"
    )