# test_weather_similarity.py
import unittest
import time
from main import WeatherApp


class TestWeatherSimilarity(unittest.TestCase):
    """
    Integration test that queries the live Open-Meteo API for two nearby cities
    and checks if their weather values are similar.
    """

    def setUp(self):
        self.app = WeatherApp(timeout=10.0)

    def test_two_neighboring_cities(self):
        # Example: Brussels (BE) and Leuven (BE) – ~30 km apart
        city1 = "Brussels"
        city2 = "Leuven"

        # Get coordinates
        lat1, lon1, name1, cc1 = self.app.geocode_city(city1)
        lat2, lon2, name2, cc2 = self.app.geocode_city(city2)

        # Fetch current weather for both
        data1 = self.app.get_current_weather(lat1, lon1)
        # tiny delay to be polite to API
        time.sleep(1)
        data2 = self.app.get_current_weather(lat2, lon2)

        # Extract values
        t1, t2 = data1["temperature"], data2["temperature"]
        w1, w2 = data1["windspeed"], data2["windspeed"]

        # Show for debugging
        print(f"\n{city1}: {t1}°C, {w1} km/h")
        print(f"{city2}: {t2}°C, {w2} km/h")

        # Compare temperature (should be roughly similar)
        temp_diff = abs(t1 - t2)
        wind_diff = abs(w1 - w2)

        # Acceptable tolerances (tune as needed)
        self.assertLessEqual(temp_diff, 5.0, f"Temperature difference too large: {temp_diff}°C")
        self.assertLessEqual(wind_diff, 10.0, f"Windspeed difference too large: {wind_diff} km/h")


if __name__ == "__main__":
    unittest.main(verbosity=2)
