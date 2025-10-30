# test_weather_forecast_consistency.py
import unittest
import time
from main import WeatherApp


class TestWeatherForecastConsistency(unittest.TestCase):
    """
    Integration test that retrieves a real multi-day forecast
    and checks data consistency and realistic value ranges.
    """

    def setUp(self):
        self.app = WeatherApp(timeout=10.0)

    def test_forecast_data_consistency(self):
        city = "Vienna"   # You can change this to any city you like
        days = 5          # Check a 5-day forecast

        # Get coordinates from geocoding API
        lat, lon, name, cc = self.app.geocode_city(city)

        # Fetch the forecast data from Open-Meteo
        forecast = self.app.get_daily_forecast(lat, lon, days)

        # Verify number of forecast days matches the request
        self.assertEqual(len(forecast["time"]), days, "Incorrect number of forecast days returned")

        # Check that all forecast lists have equal length
        keys = [
            "time", "weathercode", "temperature_2m_max",
            "temperature_2m_min", "precipitation_sum",
            "windspeed_10m_max", "winddirection_10m_dominant"
        ]
        lengths = [len(forecast[k]) for k in keys]
        self.assertTrue(all(l == days for l in lengths), "Inconsistent forecast list lengths")

        # Check that temperature and precipitation values are within realistic bounds
        for i in range(days):
            tmin = forecast["temperature_2m_min"][i]
            tmax = forecast["temperature_2m_max"][i]
            prec = forecast["precipitation_sum"][i]
            wind = forecast["windspeed_10m_max"][i]

            self.assertLessEqual(tmin, tmax, f"Day {i}: min temp higher than max temp")
            self.assertGreater(tmax, -50, f"Day {i}: max temp too low")
            self.assertLess(tmax, 60, f"Day {i}: max temp too high")
            self.assertGreaterEqual(prec, 0, f"Day {i}: negative precipitation value")
            self.assertGreaterEqual(wind, 0, f"Day {i}: negative windspeed")

        print(f"\nForecast for {city} ({cc}) verified successfully: {days} days of consistent data.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
