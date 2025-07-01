import requests
import sqlite3
from datetime import datetime, timedelta

API_KEY = "eb51d381bcb4dc58c7eec29f3f488498"
DB_NAME = "users.db"
WEATHERBIT_API_KEY = "6f1bd738429a4fbfba15fac55a3e1856"

def get_last_saved_location():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude FROM locations ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, None)
    except Exception as e:
        print(f"Error getting location: {e}")
        return None, None

def fetch_forecast_weather():
    lat, lon = get_last_saved_location()
    if lat is None or lon is None:
        return None, "No location saved."

    weather_data = {
        'dates': [],
        'temps': [],
        'rain': []
    }

    try:
        # Fetch current weather
        url_current = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response_current = requests.get(url_current)
        data_current = response_current.json()
        if not data_current or 'dt' not in data_current or 'main' not in data_current:
            return None, "Error: Could not fetch current weather data."
        date_now = datetime.utcfromtimestamp(data_current['dt']).strftime('%Y-%m-%d %H:%M')
        temp_now = data_current['main']['temp']
        rain_now = data_current.get('rain', {}).get('1h', 0)
        weather_data['dates'].append(date_now)
        weather_data['temps'].append(temp_now)
        weather_data['rain'].append(rain_now)

        # Fetch 5-day/3-hour forecast
        url_forecast = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response_forecast = requests.get(url_forecast)
        data_forecast = response_forecast.json()
        if not data_forecast or 'list' not in data_forecast:
            return None, "Error: Could not fetch forecast weather data."
        for entry in data_forecast['list']:
            date = datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M')
            temp = entry['main']['temp']
            rain = entry.get('rain', {}).get('3h', 0)
            weather_data['dates'].append(date)
            weather_data['temps'].append(temp)
            weather_data['rain'].append(rain)

        return weather_data, None
    except Exception as e:
        return None, f"Error fetching weather data: {e}"

def save_weather_data():
    weather_data, error = fetch_forecast_weather()
    if error or not weather_data or not all(k in weather_data for k in ['dates', 'temps', 'rain']):
        return error or "No weather data to save."

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weatherHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                temperature REAL,
                rain REAL
            )
        ''')
        
        for i in range(len(weather_data['dates'])):
            cursor.execute('''
                INSERT INTO weatherHistory (date, temperature, rain)
                VALUES (?, ?, ?)
            ''', (weather_data['dates'][i], weather_data['temps'][i], weather_data['rain'][i]))

        conn.commit()
        conn.close()
        return "Weather data saved successfully."
    except Exception as e:
        return f"Error saving weather data: {e}"

def fetch_soil_and_et_data():
    lat, lon = get_last_saved_location()
    if lat is None or lon is None:
        return None, None, "No location saved."

    try:
        # Fetch last 5 days of soil moisture and ET from Weatherbit AgWeather History endpoint
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=4)
        url = (
            f"https://api.weatherbit.io/v2.0/history/agweather?lat={lat}&lon={lon}"
            f"&start_date={start_date}&end_date={end_date}&key={WEATHERBIT_API_KEY}"
        )
        resp = requests.get(url)
        data = resp.json()
        if 'data' not in data or not data['data']:
            return None, None, "No soil moisture data available."
        soil_dates = []
        soil_moisture = []
        et_dates = []
        et_values = []
        for entry in data['data']:
            date = entry.get('valid_date')
            sm = entry.get('soilm_0_10cm')
            et = entry.get('evapotranspiration')
            if date and sm is not None:
                soil_dates.append(date)
                soil_moisture.append(sm)
            if date and et is not None:
                et_dates.append(date)
                et_values.append(et)
        # Store in DB
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS soil_moisture_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    soil_moisture REAL,
                    evapotranspiration REAL
                )
            ''')
            for i in range(len(soil_dates)):
                cursor.execute('''
                    INSERT INTO soil_moisture_history (date, soil_moisture, evapotranspiration)
                    VALUES (?, ?, ?)
                ''', (soil_dates[i], soil_moisture[i], et_values[i] if i < len(et_values) else None))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB error: {e}")
        return {
            'soil_dates': soil_dates,
            'soil_moisture': soil_moisture,
            'et_dates': et_dates,
            'et_values': et_values
        }, None, None
    except Exception as e:
        return None, None, str(e)