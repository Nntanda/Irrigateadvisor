from weather_data import fetch_forecast_weather, fetch_soil_and_et_data
import requests
from datetime import datetime, timedelta

print("Testing fetch_forecast_weather...")
weather_data, error = fetch_forecast_weather()
if error:
    print(f"Weather fetch FAILED: {error}")
else:
    print("Weather fetch SUCCESS:")
    print(weather_data)

print("\nTesting fetch_soil_and_et_data...")
soil_data, _, error = fetch_soil_and_et_data()
if error:
    print(f"Soil/ET fetch FAILED: {error}")
else:
    print("Soil/ET fetch SUCCESS:")
    print(soil_data)

# Debug: Try Weatherbit AgWeather History endpoint
from weather_data import get_last_saved_location
lat, lon = get_last_saved_location()
if lat and lon:
    api_key = "6f1bd738429a4fbfba15fac55a3e1856"
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=4)
    url = f"https://api.weatherbit.io/v2.0/history/agweather?lat={lat}&lon={lon}&start_date={start_date}&end_date={end_date}&key={api_key}"
    print(f"\nFetching AgWeather History API: {url}")
    resp = requests.get(url)
    print("Raw response:")
    print(resp.text)
else:
    print("No saved location for soil API test.") 