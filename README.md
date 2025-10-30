🌦️ Weather Dashboard

A Python application that retrieves and displays current weather and forecast data for any city using the free Open-Meteo API
.
No API key required. The project includes a modular design, full documentation, and automated test coverage.

Features:

🌍 City search: enter a city interactively or via command-line (--city "Prague")

🌡️ Live data: fetch current temperature, windspeed, condition, and weather code

📅 Forecast mode: display up to 16-day forecasts

⚙️ Command-line options: supports --forecast, --timeout, etc.

🧪 Automated testing: full suite of unit & integration tests for quality assurance

🧰 No API key needed: powered by the Open-Meteo and Geocoding APIs



🧠 Program Overview

The Weather Dashboard allows users to:

Enter a city name manually or via command-line.

Choose how many forecast days (0–16) to view.

Display temperature, windspeed, precipitation, and weather conditions.

Optionally test the accuracy of the API using automated integration tests.

The program’s modular design follows PEP 8 conventions, uses clear docstrings, and separates logic into small reusable methods — making it easily testable and maintainable.

🧪 Test Suite Overview

The project includes a comprehensive suite of unit and integration tests to ensure both functional correctness and real-world reliability.
All tests use Python’s built-in unittest framework.

🔍 1. TestDescribeCode

Purpose: Verify that weather condition codes are correctly translated into text.
Checks:

Known codes → correct text (e.g., 0 → "Clear sky")

Unknown codes → "Code XXX" fallback

🌍 2. TestGeocodeCity

Purpose: Test that geocoding (city → coordinates) works properly.
Checks:

Correct parsing of latitude, longitude, and country code

Invalid city raises ValueError
(Mocked API for reliability)

🌡️ 3. TestGetCurrentWeather

Purpose: Validate correct retrieval and structure of current weather data.
Checks:

JSON structure includes temperature, windspeed, and weather code

Missing or malformed data triggers errors

HTTP errors handled safely

📅 4. TestGetDailyForecast

Purpose: Validate multi-day forecast data.
Checks:

Forecast days within 1–16

Each field (time, temp, precip) has matching length

Missing daily key → raises error

🖨️ 5. TestPrinting

Purpose: Check console output formatting.
Checks:

print_current() and print_forecast() show correct formatted info
(Captured via stdout)

⌨️ 6. TestInteractiveHelpers

Purpose: Verify interactive user input validation.
Checks:

Rejects invalid entries (letters, out-of-range)

Accepts valid numbers (0–16)

⚙️ 7. TestArgParse

Purpose: Test CLI argument parsing.
Checks:

--city, --forecast, and --timeout parsed correctly

🌦️ 8. TestWeatherSimilarity (Integration Test), this test can be found in the file called test_main_accuracy

Purpose: Compare weather data of two neighboring cities.
Checks:

Retrieves live temperature and windspeed

Passes if differences ≤ 5 °C and ≤ 10 km/h respectively
(Uses real API data)

🌤️ 9. TestWeatherForecastConsistency (Integration Test), this test can be found in the file callex test_main_consistency

Purpose: Check that a real 5-day forecast is consistent and realistic.
Checks:

Correct number of forecast days returned

All forecast lists have matching lengths

Logical consistency (min ≤ max temperature)

Physical plausibility (temps, wind, and precipitation within valid ranges)
