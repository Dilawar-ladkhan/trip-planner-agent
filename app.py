import streamlit as st
import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

st.set_page_config(page_title="Trip Planner Agent", layout="wide")
st.title("🌍 Trip Planner Agent (OpenRouter + Real-time Weather)")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def get_current_weather(city: str):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    return requests.get(url, timeout=20).json()


def get_forecast(city: str):
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    return requests.get(url, timeout=20).json()


def generate_trip_plan(city, days, month, current_weather, forecast_weather):
    llm = ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.6,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Trip Planner MCP Agent"
        }
    )

    prompt = f"""
You are a travel planning agent.

User wants a {days}-day trip to {city} in {month}.

REAL-TIME WEATHER (CURRENT):
{current_weather}

REAL-TIME FORECAST:
{forecast_weather}

Return output in this exact format:

1) Cultural & Historic Significance (1 paragraph)

2) Current Weather + Forecast Summary (bullet points)

3) Travel Dates (assume a realistic {days}-day trip in {month})

4) Flight Options (3 options)
Provide realistic structured options with:
- Airline
- Departure time
- Duration
- Estimated price

5) Hotel Options (3 options)
Provide realistic structured options with:
- Hotel name
- Area
- Price per night
- Rating

6) Day-wise Trip Plan (Day 1 to Day {days})
Include:
- Morning
- Afternoon
- Evening
"""
    return llm.invoke(prompt).content


city = st.text_input("Destination City", "Tokyo")
days = st.selectbox("Trip Duration (days)", [2, 3], index=1)
month = st.selectbox("Month", ["May", "June", "July", "August"], index=0)

if st.button("🚀 Plan My Trip"):
    with st.spinner("Fetching real-time weather..."):
        current = get_current_weather(city)
        forecast = get_forecast(city)

    st.subheader("🌦 Real-time Weather (OpenWeather)")

    if "main" in current:
        st.write(f"**City:** {current.get('name')}")
        st.write(f"**Temperature:** {current['main']['temp']} °C")
        st.write(f"**Feels Like:** {current['main']['feels_like']} °C")
        st.write(f"**Humidity:** {current['main']['humidity']}%")
        st.write(f"**Condition:** {current['weather'][0]['description']}")
    else:
        st.error("Could not fetch current weather.")
        st.json(current)

    st.markdown("---")

    if "list" in forecast:
        st.write("### 📅 Forecast (Next ~24 hours preview)")
        for item in forecast["list"][:8]:
            st.write(
                f"{item['dt_txt']} → {item['main']['temp']}°C, {item['weather'][0]['description']}"
            )
    else:
        st.error("Could not fetch forecast.")
        st.json(forecast)

    st.markdown("---")

    with st.spinner("Generating trip plan with OpenRouter LLM..."):
        plan = generate_trip_plan(city, days, month, current, forecast)

    st.subheader("🗺 Trip Plan")
    st.write(plan)
