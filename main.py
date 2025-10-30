"""
Weather Dashboard (City → Geocode → Current + Forecast)
API: Open-Meteo (no API key needed)
Author: Mathias Vertongen
License: MIT
"""

from __future__ import annotations
import argparse
import sys
from typing import Optional, Tuple, Dict, List

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Minimal mapping of Open-Meteo weather codes → human-friendly text
WEATHER_CODE_MAP: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm (slight hail)", 99: "Thunderstorm (heavy hail)",
}


class WeatherApp:
    """Fetch current weather and daily forecast via Open-Meteo."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    # ---------------- Geocoding ----------------
    def geocode_city(self, city: str) -> Tuple[float, float, str, Optional[str]]:
        """
        Return (lat, lon, resolved_city_name, country_code) for a city.
        Raises ValueError if nothing found.
        """
        params = {"name": city, "count": 1, "language": "en", "format": "json"}
        r = requests.get(GEOCODE_URL, params=params, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        results = data.get("results") or []
        if not results:
            raise ValueError(f"City '{city}' not found.")
        top = results[0]
        lat = float(top["latitude"])
        lon = float(top["longitude"])
        name = f"{top.get('name')}"
        cc = top.get("country_code")
        if top.get("admin1"):
            name = f"{name}, {top['admin1']}"
        return lat, lon, name, cc

    # ---------------- Current Weather ----------------
    def get_current_weather(self, lat: float, lon: float) -> dict:
        """Return current weather JSON for given coordinates."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "timezone": "auto",
        }
        r = requests.get(WEATHER_URL, params=params, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if "current_weather" not in data:
            raise ValueError("Weather data missing from API response.")
        return data["current_weather"]

    # ---------------- Daily Forecast ----------------
    def get_daily_forecast(self, lat: float, lon: float, days: int) -> dict:
        """
        Return daily forecast JSON for given coordinates.
        'days' can be 1–16 according to Open-Meteo limits (free).
        """
        if days < 1 or days > 16:
            raise ValueError("Forecast days must be between 1 and 16.")
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join([
                "weathercode",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "windspeed_10m_max",
                "winddirection_10m_dominant",
            ]),
            "forecast_days": days,
            "timezone": "auto",
        }
        r = requests.get(WEATHER_URL, params=params, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if "daily" not in data:
            raise ValueError("Daily forecast missing from API response.")
        return data["daily"]

    # ---------------- Formatting helpers ----------------
    def describe_code(self, code: int) -> str:
        return WEATHER_CODE_MAP.get(code, f"Code {code}")

    def print_current(self, city_label: str, lat: float, lon: float, cw: dict) -> None:
        temp = cw.get("temperature")
        wind = cw.get("windspeed")
        wcode = int(cw.get("weathercode", -999))
        desc = self.describe_code(wcode)
        print("\n— Current Weather —")
        print(f"Location   : {city_label}")
        print(f"Latitude   : {lat:.4f}, Longitude: {lon:.4f}")
        print(f"Temperature: {temp} °C")
        print(f"Windspeed  : {wind} km/h")
        print(f"Condition  : {desc}")

    def print_forecast(self, daily: dict) -> None:
        print("\n— Daily Forecast —")
        dates: List[str] = daily.get("time", [])
        codes: List[int] = daily.get("weathercode", [])
        tmax: List[float] = daily.get("temperature_2m_max", [])
        tmin: List[float] = daily.get("temperature_2m_min", [])
        psum: List[float] = daily.get("precipitation_sum", [])
        wmax: List[float] = daily.get("windspeed_10m_max", [])
        wdir: List[int] = daily.get("winddirection_10m_dominant", [])

        for i in range(len(dates)):
            desc = self.describe_code(int(codes[i]))
            print(
                f"{dates[i]} | {desc:28} | "
                f"min {tmin[i]:>5.1f}°C  max {tmax[i]:>5.1f}°C  "
                f"prec {psum[i]:>4.1f} mm  wind {wmax[i]:>4.0f} km/h dir {wdir[i]:>3}°"
            )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Weather Dashboard using Open-Meteo (no API key needed)"
    )
    p.add_argument("--city", "-c", type=str, help='City name, e.g. --city "Brno"')
    p.add_argument(
        "--forecast", "-f", type=int, default=None,
        help="Number of forecast days (1–16). If omitted, you will be prompted interactively."
    )
    p.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds")
    return p.parse_args()


def ask_forecast_days_interactively() -> int:
    """Prompt the user for 0–16 forecast days (0 = none)."""
    while True:
        days_str = input("How many forecast days (0 for none, 1–16)? ").strip() or "0"
        try:
            days = int(days_str)
            if 0 <= days <= 16:
                return days
        except ValueError:
            pass
        print("Please enter an integer between 0 and 16.")


def main() -> None:
    args = parse_args()
    app = WeatherApp(timeout=args.timeout)

    try:
        # City: CLI or prompt
        if args.city:
            city_input = args.city.strip()
        else:
            city_input = input("Enter a city name: ").strip()
            if not city_input:
                print("No city entered. Exiting.")
                return

        # Forecast days: CLI or prompt
        if args.forecast is None:
            forecast_days = ask_forecast_days_interactively()
        else:
            if not (0 <= args.forecast <= 16):
                print("Error: --forecast must be between 0 and 16.")
                return
            forecast_days = args.forecast

        lat, lon, resolved, cc = app.geocode_city(city_input)
        city_label = resolved if not cc else f"{resolved} ({cc})"

        # Current weather
        cw = app.get_current_weather(lat, lon)
        app.print_current(city_label, lat, lon, cw)

        # Optional forecast
        if forecast_days > 0:
            daily = app.get_daily_forecast(lat, lon, forecast_days)
            app.print_forecast(daily)

    except requests.HTTPError as e:
        print("HTTP error from API:", e)
    except requests.ConnectionError:
        print("Network error: please check your internet connection.")
    except requests.Timeout:
        print("Request timed out. Try again.")
    except ValueError as e:
        print("Error:", e)
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        print("Unexpected error:", e)


if __name__ == "__main__":
    main()
