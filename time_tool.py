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


@tool
def get_current_time(city: str) -> str:
    """Get the current local time for a city."""

    print(f"\n  🕐 Time searching: {city}")

    location = get_location(city)

    if not location:
        return f"Could not find the location: {city}"

    latitude = location["latitude"]
    longitude = location["longitude"]

    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "timezone": "auto",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    current_time = data["current"]["time"]
    timezone_name = data.get("timezone", "Unknown")

    # Convert API format:
    # 2026-09-22T12:34
    # into:
    # Tuesday, 22 September 2026
    # 12:34 PM
    from datetime import datetime

    parsed_time = datetime.fromisoformat(current_time)

    formatted_date = parsed_time.strftime(
        "%A, %d %B %Y"
    )

    formatted_time = parsed_time.strftime(
        "%I:%M %p"
    )

    print("  🕐 Time: result found")

    return (
        f"🕐 **Current time in {location['name']}, "
        f"{location.get('country', '')}**\n\n"
        f"📅 **Date:** {formatted_date}\n"
        f"⏰ **Time:** {formatted_time}\n"
        f"🌍 **Timezone:** {timezone_name}"
    )