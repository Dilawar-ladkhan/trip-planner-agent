from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

mcp = FastMCP("Trip Planner MCP Server")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@mcp.tool()
def get_current_weather(city: str) -> dict:
    """Get current weather for a city using OpenWeather API."""
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    r = requests.get(url, timeout=20)
    data = r.json()

    if r.status_code != 200:
        return {"error": data}

    return {
        "city": city,
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"]
    }


@mcp.tool()
def get_weather_forecast(city: str) -> dict:
    """
    Get 5-day forecast (3-hour intervals) using OpenWeather.
    We'll summarize day-wise.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    r = requests.get(url, timeout=20)
    data = r.json()

    if r.status_code != 200:
        return {"error": data}

    daily = {}

    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
        temp = item["main"]["temp"]
        condition = item["weather"][0]["description"]

        if dt not in daily:
            daily[dt] = {"temps": [], "conditions": []}

        daily[dt]["temps"].append(temp)
        daily[dt]["conditions"].append(condition)

    summary = []
    for day, vals in list(daily.items())[:5]:
        avg_temp = sum(vals["temps"]) / len(vals["temps"])
        common_condition = max(set(vals["conditions"]), key=vals["conditions"].count)
        summary.append({
            "date": day,
            "avg_temp_c": round(avg_temp, 1),
            "condition": common_condition
        })

    return {"city": city, "forecast": summary}


if __name__ == "__main__":
    mcp.run()
