# 🌤 Weather App

A modern, interactive weather application built with **pure Python** — no third-party libraries, no API key required.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)

---

## Preview

Search any city in the world and get:
- Current temperature, feels like, humidity, wind, visibility
- 24-hour hourly forecast
- 7-day daily forecast with temperature range bars
- UV index with exposure advice
- Atmospheric data (pressure, cloud cover, dew point, wind direction)
- Animated sunrise/sunset arc
- °C / °F toggle
- GPS location detection

---

## How It Works

The Python script starts a local HTTP server and serves a self-contained weather UI in your browser. All weather data is fetched client-side from [Open-Meteo](https://open-meteo.com/) — a free, open-source weather API that requires no API key.

```
python weather_app.py  →  opens http://127.0.0.1:8766 in your browser
```

---

## Requirements

- Python 3.8 or higher
- No pip installs needed — uses only Python standard library

---

## Installation & Usage

**1. Clone the repo**
```bash
git clone https://github.com/your-username/weather-app.git
cd weather-app
```

**2. Run the app**
```bash
python weather_app.py
```

The app will automatically open in your default browser at `http://127.0.0.1:8766`.

Press `Ctrl+C` in the terminal to stop the server.

---

## Windows Users

If `python` is not recognized, try:
```bash
py weather_app.py
```

Or use the full Python path:
```bash
C:\Users\YourName\AppData\Local\Programs\Python\Python310\python.exe weather_app.py
```

---

## APIs Used

| API | Purpose | Cost |
|-----|---------|------|
| [Open-Meteo](https://api.open-meteo.com) | Weather forecasts | Free, no key |
| [Open-Meteo Geocoding](https://geocoding-api.open-meteo.com) | City search | Free, no key |

---

## Project Structure

```
weather-app/
│
├── weather_app.py   # Main Python script — server + full UI
└── README.md
```

---

## License

MIT — free to use, modify, and distribute.
