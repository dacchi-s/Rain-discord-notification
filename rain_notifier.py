#!/usr/bin/env python3
"""
Rain Cloud Radar Discord Notification Bot

Fetches precipitation forecasts for a specified location using Open-Meteo JMA API
and sends a Discord notification when rain is expected.
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# ===== Configuration =====
# Coordinates (environment variables or default values)
LATITUDE = float(os.getenv("RAIN_LATITUDE", "35.6895"))
LONGITUDE = float(os.getenv("RAIN_LONGITUDE", "139.6917"))

# Precipitation threshold for notification (mm)
RAIN_THRESHOLD = float(os.getenv("RAIN_THRESHOLD", "0.5"))

# Time range to check (hours ahead)
HOURS_TO_CHECK = int(os.getenv("RAIN_HOURS_TO_CHECK", "1"))

# Discord Webhook URL (environment variable)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# API endpoint
API_BASE = "https://api.open-meteo.com/v1/jma"


@dataclass
class RainForecast:
    """Precipitation forecast data"""
    time: datetime
    precipitation: float
    weather_code: int


def fetch_rain_forecast(lat: float, lon: float, hours: int) -> list[RainForecast]:
    """
    Fetch precipitation forecast from Open-Meteo JMA API

    Args:
        lat: Latitude
        lon: Longitude
        hours: Number of hours to fetch

    Returns:
        List of precipitation forecasts
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation,weather_code",
        "forecast_hours": hours,
        "timezone": "Asia/Tokyo",
    }

    try:
        response = requests.get(API_BASE, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        precipitations = hourly.get("precipitation", [])
        weather_codes = hourly.get("weather_code", [])

        for i, time_str in enumerate(times):
            dt = datetime.fromisoformat(time_str)
            precip = precipitations[i] if i < len(precipitations) else 0.0
            code = weather_codes[i] if i < len(weather_codes) else 0

            forecasts.append(RainForecast(
                time=dt,
                precipitation=precip,
                weather_code=code
            ))

        return forecasts

    except requests.RequestException as e:
        print(f"API request error: {e}", file=sys.stderr)
        return []


def get_weather_description(code: int) -> str:
    """
    Get Japanese weather description from WMO weather code

    Args:
        code: WMO weather code

    Returns:
        Weather description in Japanese
    """
    weather_codes = {
        0: "快晴",
        1: "晴れ",
        2: "一部曇り",
        3: "曇り",
        45: "霧",
        48: "霧氷",
        51: "小雨",
        53: "小雨",
        55: "小雨",
        61: "小雨",
        63: "雨",
        65: "大雨",
        66: "雨氷",
        67: "雨氷",
        71: "小雪",
        73: "雪",
        75: "大雪",
        77: "霧雪",
        80: "にわか雨",
        81: "にわか雨",
        82: "激しいにわか雨",
        85: "にわか雪",
        86: "激しいにわか雪",
        95: "雷雨",
        96: "雷雨と雹",
        99: "激しい雷雨と雹",
    }
    return weather_codes.get(code, "不明")


def create_webhook_payload(forecasts: list[RainForecast]) -> dict:
    """
    Create Discord webhook payload with embed

    Args:
        forecasts: List of precipitation forecasts

    Returns:
        Discord webhook payload dictionary
    """
    # Build forecast details
    forecast_text = ""
    for f in forecasts:
        time_str = f.time.strftime("%H:%M")
        weather_desc = get_weather_description(f.weather_code)
        forecast_text += f"`{time_str}` - {weather_desc} (降水量: {f.precipitation}mm)\n"

    embed = {
        "title": "🌧️ 雨が降りそうです",
        "description": "まもなく雨が予想されます。",
        "color": 0x5865F2,  # Discord Blurple
        "fields": [
            {
                "name": "予報",
                "value": forecast_text or "データなし",
                "inline": False
            },
            {
                "name": "場所",
                "value": f"緯度: {LATITUDE}, 経度: {LONGITUDE}\n(東京都新宿区付近)",
                "inline": False
            }
        ],
        "footer": {
            "text": "Powered by Open-Meteo JMA API"
        },
        "timestamp": datetime.now().isoformat()
    }

    return {"embeds": [embed]}


def send_discord_notification(webhook_url: str, forecasts: list[RainForecast]) -> bool:
    """
    Send notification to Discord via webhook

    Args:
        webhook_url: Discord Webhook URL
        forecasts: List of precipitation forecasts

    Returns:
        True if sent successfully
    """
    if not webhook_url:
        print("Error: Discord Webhook URL is not configured", file=sys.stderr)
        return False

    try:
        payload = create_webhook_payload(forecasts)
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Discord notification sent successfully")
        return True
    except requests.RequestException as e:
        print(f"Discord notification error: {e}", file=sys.stderr)
        return False


def check_and_notify() -> bool:
    """
    Check precipitation forecast and send Discord notification if needed

    Returns:
        True if rain is expected
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking precipitation forecast...")

    forecasts = fetch_rain_forecast(LATITUDE, LONGITUDE, HOURS_TO_CHECK)

    if not forecasts:
        print("Failed to fetch forecast data")
        return False

    # Detect precipitation exceeding threshold
    rain_forecasts = [f for f in forecasts if f.precipitation >= RAIN_THRESHOLD]

    if rain_forecasts:
        print(f"⚠️  Rain expected: {len(rain_forecasts)} occurrence(s)")
        for f in rain_forecasts:
            print(f"  - {f.time.strftime('%H:%M')}: {f.precipitation}mm ({get_weather_description(f.weather_code)})")

        if DISCORD_WEBHOOK_URL:
            send_discord_notification(DISCORD_WEBHOOK_URL, rain_forecasts)
        else:
            print("Notice: Discord Webhook URL is not set, notification not sent")
            print("Please set the DISCORD_WEBHOOK_URL environment variable")

        return True
    else:
        print("✅ No rain expected")
        return False


def main():
    """Main function"""
    if not DISCORD_WEBHOOK_URL:
        print("Warning: DISCORD_WEBHOOK_URL environment variable is not set")
        print("Set the environment variable or specify it in the code to send notifications")
        print()
        print("Example: export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/...'")

    check_and_notify()


if __name__ == "__main__":
    main()
