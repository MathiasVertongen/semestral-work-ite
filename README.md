# 🌦️ Weather Dashboard  
**Python application using the free Open-Meteo API (no key required)**

A modular and fully tested Python project that retrieves current weather information and multi-day forecasts for any city in the world. Ideal as a learning project for APIs, Python modularity, CLI tools, and software testing.

---

## ✨ Features

- 🌍 **City Search**  
  - Enter a city via interactive input or via command line  
  - Example: `--city "Prague"`

- 🌡️ **Live Weather Data**  
  - Temperature  
  - Wind speed  
  - Weather conditions + code  

- 📅 **Forecast Mode**  
  - Display forecasts up to **16 days**

- ⚙️ **Command-line Options**  
  - Support for `--forecast`, `--timeout`, …

- 🧪 **Extensive Testing**  
  - Unit tests  
  - Integration tests  
  - Automatic validation of API responses

- 🧰 **No API Key Needed**  
  - Uses the Open-Meteo Forecast and Geocoding API

---

# 🧠 Program Overview

The Weather Dashboard allows users to:

- Enter a city (CLI or interactive)
- Select the desired number of forecast days (0–16)
- Display temperature, wind, precipitation, and conditions
- Optionally run accuracy tests using real API data

**Design principles:**

- Follows **PEP 8** coding conventions  
- Modular structure with small reusable functions  
- User-friendly CLI  
- Clear documentation via docstrings  
- Easy to test and extend

---

# 🧪 Test Suite Overview

All tests are written using Python’s `unittest` framework.  
They validate both functional correctness and real-world API behavior.

---

## 🔍 1. TestDescribeCode
**Purpose:** Verify correct translation of Open-Meteo weather codes  
**Checks:**
- Known codes → correct text  
- Unknown codes → fallback `"Code XXX"`

---

## 🌍 2. TestGeocodeCity
**Purpose:** Validate geocoding (city → coordinates)  
**Checks:**
- Parsing of latitude, longitude, and country code  
- Invalid city raises `ValueError`  
- Mocked API ensures stability

---

## 🌡️ 3. TestGetCurrentWeather
**Purpose:** Validate retrieval of current weather data  
**Checks:**
- JSON includes temperature, wind, and weather code  
- Missing fields trigger errors  
- HTTP errors handled safely

---

## 📅 4. TestGetDailyForecast
**Purpose:** Validate multi-day forecast correctness  
**Checks:**
- Forecast days within 1–16  
- Matching list lengths for time, temperature, precipitation  
- Missing `daily` key → error

---

## 🖨️ 5. TestPrinting
**Purpose:** Validate console output formatting  
**Checks:**
- `print_current()` outputs a correct formatted block  
- `print_forecast()` outputs a clear forecast table  
- Output captured using stdout redirection

---

## ⌨️ 6. TestInteractiveHelpers
**Purpose:** Validate user input handling  
**Checks:**
- Rejects invalid entries (letters, out-of-range numbers)  
- Accepts valid inputs (0–16)

---

## ⚙️ 7. TestArgParse
**Purpose:** Validate command-line argument parsing  
**Checks:**
- `--city`  
- `--forecast`  
- `--timeout`

---

## 🌦️ 8. TestWeatherSimilarity *(Integration Test)*  
*(file: `test_main_accuracy`)*  

**Purpose:** Compare weather between two nearby cities  
**Checks:**
- Retrieves live temperature and wind data  
- Passes if differences ≤ 5°C and ≤ 10 km/h

---

## 🌤️ 9. TestWeatherForecastConsistency *(Integration Test)*  
*(file: `test_main_consistency`)*

**Purpose:** Validate realism of a real 5-day forecast  
**Checks:**
- Correct number of days  
- All lists have matching lengths  
- Logical temperature values (min ≤ max)  
- Realistic ranges for precipitation and wind

---

# 📜 Weather Dashboard License

**License Name:** Weather Dashboard License (MIT-style)  
**Author:** Mathias Vertongen  
**Year:** 2025  

**Permissions:**

- Free use, modification, and redistribution  
- Commercial use allowed  
- Attribution required  
- Must comply with Open-Meteo API terms

---
## **UMLdiagarm**

<img width="865" height="872" alt="image" src="https://github.com/user-attachments/assets/d3d8825a-f227-49cb-b290-c9281a8eb069" />

---

## 📦 Installation

This project uses one external Python library: **requests**.

To install all required dependencies, run the following command in your terminal:

---
```bash
pip install -r requirements.txt


