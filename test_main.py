# test_weather_dashboard.py
import io
import sys
import json
import builtins
import unittest
from unittest.mock import patch, MagicMock

import main as wd


class FakeResponse:
    """Minimal fake HTTP response to mimic requests.Response."""
    def __init__(self, status_code=200, json_data=None, text="", raise_http=False):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
        self._raise_http = raise_http

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self._raise_http or not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")


class TestDescribeCode(unittest.TestCase):
    def setUp(self):
        self.app = wd.WeatherApp()

    def test_known_codes(self):
        self.assertEqual(self.app.describe_code(0), "Clear sky")
        self.assertEqual(self.app.describe_code(3), "Overcast")

    def test_unknown_code(self):
        self.assertIn("Code 1234", self.app.describe_code(1234))


class TestGeocodeCity(unittest.TestCase):
    def setUp(self):
        self.app = wd.WeatherApp()

    @patch("requests.get")
    def test_geocode_success(self, mock_get):
        payload = {
            "results": [{
                "latitude": 50.0880,
                "longitude": 14.4208,
                "name": "Prague",
                "admin1": "Prague",
                "country_code": "CZ",
            }]
        }
        mock_get.return_value = FakeResponse(200, payload)

        lat, lon, name, cc = self.app.geocode_city("Prague")
        self.assertAlmostEqual(lat, 50.0880, places=4)
        self.assertAlmostEqual(lon, 14.4208, places=4)
        self.assertEqual(name, "Prague, Prague")
        self.assertEqual(cc, "CZ")

    @patch("requests.get")
    def test_geocode_not_found(self, mock_get):
        mock_get.return_value = FakeResponse(200, {"results": []})
        with self.assertRaises(ValueError):
            self.app.geocode_city("XyzNotARealCity")


class TestGetCurrentWeather(unittest.TestCase):
    def setUp(self):
        self.app = wd.WeatherApp()

    @patch("requests.get")
    def test_current_ok(self, mock_get):
        payload = {"current_weather": {"temperature": 10.5, "windspeed": 5.4, "weathercode": 3}}
        mock_get.return_value = FakeResponse(200, payload)

        data = self.app.get_current_weather(50.088, 14.4208)
        self.assertIn("temperature", data)
        self.assertIn("windspeed", data)
        self.assertEqual(data["weathercode"], 3)

    @patch("requests.get")
    def test_current_missing_key(self, mock_get):
        mock_get.return_value = FakeResponse(200, {"foo": "bar"})
        with self.assertRaises(ValueError):
            self.app.get_current_weather(0, 0)

    @patch("requests.get")
    def test_current_http_error(self, mock_get):
        mock_get.return_value = FakeResponse(status_code=500, raise_http=True)
        with self.assertRaises(Exception):
            self.app.get_current_weather(0, 0)


class TestGetDailyForecast(unittest.TestCase):
    def setUp(self):
        self.app = wd.WeatherApp()

    def test_days_bounds(self):
        with self.assertRaises(ValueError):
            self.app.get_daily_forecast(0, 0, 0)
        with self.assertRaises(ValueError):
            self.app.get_daily_forecast(0, 0, 17)

    @patch("requests.get")
    def test_forecast_ok(self, mock_get):
        payload = {
            "daily": {
                "time": ["2025-01-01", "2025-01-02"],
                "weathercode": [3, 1],
                "temperature_2m_max": [10.0, 11.5],
                "temperature_2m_min": [2.0, 3.1],
                "precipitation_sum": [0.0, 1.2],
                "windspeed_10m_max": [20.0, 15.0],
                "winddirection_10m_dominant": [180, 200],
            }
        }
        mock_get.return_value = FakeResponse(200, payload)

        daily = self.app.get_daily_forecast(50.0, 14.0, 2)
        self.assertEqual(len(daily["time"]), 2)
        self.assertEqual(daily["weathercode"][0], 3)

    @patch("requests.get")
    def test_forecast_missing_key(self, mock_get):
        mock_get.return_value = FakeResponse(200, {"foo": "bar"})
        with self.assertRaises(ValueError):
            self.app.get_daily_forecast(0, 0, 2)


class TestPrinting(unittest.TestCase):
    def setUp(self):
        self.app = wd.WeatherApp()

    def test_print_current(self):
        cw = {"temperature": 14.4, "windspeed": 12.2, "weathercode": 3}
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            self.app.print_current("Prague (CZ)", 50.0880, 14.4208, cw)
        finally:
            sys.stdout = old
        out = buf.getvalue()
        self.assertIn("Current Weather", out)
        self.assertIn("Prague (CZ)", out)
        self.assertIn("Overcast", out)

    def test_print_forecast(self):
        daily = {
            "time": ["2025-01-01"],
            "weathercode": [0],
            "temperature_2m_max": [12.3],
            "temperature_2m_min": [3.2],
            "precipitation_sum": [0.0],
            "windspeed_10m_max": [18.0],
            "winddirection_10m_dominant": [190],
        }
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            self.app.print_forecast(daily)
        finally:
            sys.stdout = old
        out = buf.getvalue()
        self.assertIn("Daily Forecast", out)
        self.assertIn("Clear sky", out)
        self.assertIn("min", out)
        self.assertIn("max", out)


class TestInteractiveHelpers(unittest.TestCase):
    @patch.object(builtins, "input", side_effect=["", "abc", "17", "5"])
    def test_ask_forecast_days_interactively(self, mock_input):
        # tries: "" -> 0 accepted? No, code treats "" as "0" and validates 0..16, returns 0 immediately.
        # But our side_effect forces retries till a valid 0..16 integer; adjust to cover retries:
        # First call returns "", which becomes "0" and is valid -> returns 0
        days = wd.ask_forecast_days_interactively()
        self.assertEqual(days, 0)


class TestArgParse(unittest.TestCase):
    def test_parse_args(self):
        argv = ["prog", "--city", "Brno", "--forecast", "5", "--timeout", "7"]
        with patch.object(sys, "argv", argv):
            args = wd.parse_args()
        self.assertEqual(args.city, "Brno")
        self.assertEqual(args.forecast, 5)
        self.assertEqual(args.timeout, 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
