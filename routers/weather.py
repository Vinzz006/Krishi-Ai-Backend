import httpx
from fastapi import APIRouter

router = APIRouter()

# Kerala districts and their approximate lat/lon
KERALA_LOCATIONS = {
    "thiruvananthapuram": (8.5241, 76.9366),
    "kochi": (9.9312, 76.2673),
    "kozhikode": (11.2588, 75.7804),
    "thrissur": (10.5276, 76.2144),
    "palakkad": (10.7867, 76.6548),
    "kollam": (8.8932, 76.6141),
    "kannur": (11.8745, 75.3704),
    "kottayam": (9.5916, 76.5222),
    "alappuzha": (9.4981, 76.3388),
    "malappuram": (11.0510, 76.0711),
    "idukki": (9.9189, 77.1025),
    "wayanad": (11.6854, 76.1320),
    "kasaragod": (12.4996, 74.9869),
    "pathanamthitta": (9.2648, 76.7870),
}

@router.get("/")
async def get_weather(location: str = "kochi"):
    loc = location.lower()
    lat, lon = KERALA_LOCATIONS.get(loc, KERALA_LOCATIONS["kochi"])

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
        f"&timezone=Asia/Kolkata&forecast_days=5"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()

    current = data.get("current", {})
    daily = data.get("daily", {})

    wmo_codes = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Foggy", 51: "Light Drizzle", 61: "Light Rain", 63: "Moderate Rain",
        65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm",
    }
    wc = current.get("weather_code", 0)
    condition = wmo_codes.get(wc, "Variable")

    # Farm advisory based on weather
    rh = current.get("relative_humidity_2m", 70)
    precip = current.get("precipitation", 0)
    temp = current.get("temperature_2m", 28)

    advisories = []
    if rh > 85:
        advisories.append("⚠️ High humidity — increased risk of fungal diseases. Monitor crops closely.")
    if precip > 10:
        advisories.append("🌧️ Heavy rainfall — ensure proper field drainage to prevent waterlogging.")
    if temp > 35:
        advisories.append("🌡️ High temperature — irrigate in evening, provide shade for seedlings.")
    if temp < 18:
        advisories.append("❄️ Cool weather — good for Rabi crops. Monitor for mist/fog-related diseases.")
    if not advisories:
        advisories.append("✅ Weather conditions are favorable for most field operations today.")

    forecast = []
    if daily.get("time"):
        for i in range(min(5, len(daily["time"]))):
            forecast.append({
                "date": daily["time"][i],
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "precipitation": daily["precipitation_sum"][i],
                "wind_max": daily["wind_speed_10m_max"][i],
            })

    return {
        "location": location.title(),
        "coordinates": {"lat": lat, "lon": lon},
        "current": {
            "temperature": temp,
            "humidity": rh,
            "precipitation": precip,
            "wind_speed": current.get("wind_speed_10m", 0),
            "condition": condition,
        },
        "forecast": forecast,
        "farm_advisories": advisories,
        "source": "Open-Meteo"
    }
