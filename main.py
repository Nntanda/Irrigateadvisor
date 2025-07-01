import matplotlib.pyplot as plt
import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty
from geopy.geocoders import Nominatim
from vegetable_db import create_vegetable_table, save_vegetable_selection, get_latest_vegetable_selection
from location_db import create_location_table, save_location, get_last_saved_location
from weather_data import fetch_forecast_weather, fetch_soil_and_et_data
from user_db import create_user_table
import folium
import webbrowser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time
import os
import numpy as np
from kivy_garden.mapview import MapView, MapMarker

# Optional dependencies
MAPVIEW_AVAILABLE = False

try:
    from plyer import notification
except ImportError:
    notification = None

# Load all .kv files
Builder.load_file("welcome.kv")
Builder.load_file("login.kv")
Builder.load_file("signup.kv")
Builder.load_file("home.kv")
Builder.load_file("location.kv")
Builder.load_file("vegetable_selection.kv")
Builder.load_file("weather_chart.kv")
Builder.load_file("soil_moisture.kv")
Builder.load_file("recommendations.kv")

# --- Helper Functions ---
def show_popup(title, message, auto_dismiss=True, callback=None):
    """Show a popup with optional callback."""
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.7, 0.3), auto_dismiss=auto_dismiss)
    if callback is not None:
        popup.bind(on_dismiss=callback)
    popup.open()
    return popup

def safe_notify(title, message, timeout=10):
    """Send a notification if supported."""
    notify_func = getattr(notification, 'notify', None)
    if callable(notify_func):
        try:
            notify_func(title=title, message=message, timeout=timeout)
        except Exception:
            pass

# --- Screens ---
class WelcomeScreen(Screen):
    pass

class LoginScreen(Screen):
    def login(self):
        email = self.ids.login_email.text.strip()
        password = self.ids.login_password.text.strip()
        if not email or not password:
            show_popup("Error", "Please enter both email and password.")
            return
        from user_db import validate_user
        if validate_user(email, password):
            popup = show_popup("Success", f"Login successful!\n\nWelcome back, {email}!\n\nRedirecting to dashboard...", auto_dismiss=False)
            Clock.schedule_once(lambda dt: self.redirect_to_home(popup, email), 1.5)
        else:
            show_popup("Error", "Invalid email or password.")
    def redirect_to_home(self, popup, email):
        popup.dismiss()
        home_screen = self.manager.get_screen('home')
        home_screen.update_user_email(email)
        self.manager.current = 'home'
        self.ids.login_email.text = ""
        self.ids.login_password.text = ""

class SignupScreen(Screen):
    def signup(self):
        email = self.ids.signup_email.text.strip()
        password = self.ids.signup_password.text.strip()
        confirm = self.ids.confirm_password.text.strip()
        if not email or not password or not confirm:
            show_popup("Error", "All fields are required.")
            return
        if password != confirm:
            show_popup("Error", "Passwords do not match.")
            return
        from user_db import add_user
        result = add_user(email, password)
        if result == "invalid_email":
            show_popup("Error", "Please enter a valid email.")
        elif result == "weak_password":
            show_popup("Error", "Password must be at least 6 characters.")
        elif result == "exists":
            show_popup("Error", "Email already exists.")
        elif result == "success":
            popup = show_popup("Success", f"Account created successfully!\n\nEmail: {email}\n\nRedirecting to login page...", auto_dismiss=False)
            Clock.schedule_once(lambda dt: self.redirect_to_login(popup), 2.0)
        else:
            show_popup("Error", "An unknown error occurred.")
    def redirect_to_login(self, popup):
        popup.dismiss()
        self.manager.current = 'login'
        self.ids.signup_email.text = ""
        self.ids.signup_password.text = ""
        self.ids.confirm_password.text = ""

class HomeScreen(Screen):
    def update_user_email(self, email):
        self.ids.welcome_label.text = f"Welcome, {email}!"

class LocationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapview = MapView(zoom=10, lat=-1.2921, lon=36.8219)
        self.marker = MapMarker(lat=-1.2921, lon=36.8219)
        self.mapview.add_marker(self.marker)
        self.add_widget(self.mapview)

    def on_pre_enter(self):
        self.ids.status_label.text = ""
        self.show_last_location_map()

    def use_gps(self):
        try:
            from plyer import gps
            def on_location(**kwargs):
                lat = kwargs.get('lat')
                lon = kwargs.get('lon')
                if lat is not None and lon is not None:
                    self.update_map(lat, lon)
                    save_location('GPS', lat, lon)
                    self.ids.status_label.text = f"Saved GPS location: {lat}, {lon}"
                else:
                    self.ids.status_label.text = "GPS did not return valid coordinates."
            if getattr(gps, 'configure', None) and getattr(gps, 'start', None):
                gps.configure(on_location=on_location)
                gps.start(minTime=1000, minDistance=1)
            else:
                self.ids.status_label.text = "GPS not supported on this platform."
        except Exception as e:
            self.ids.status_label.text = f"GPS failed: {e}"

    def search_location(self):
        place = self.ids.location_input.text
        geolocator = Nominatim(user_agent="kivy_app")
        try:
            location = geolocator.geocode(place)
            if hasattr(location, '__await__') or location is None:
                self.ids.status_label.text = "Location search failed. Please try again."
                return
            if hasattr(location, 'latitude') and hasattr(location, 'longitude'):
                lat, lon = location.latitude, location.longitude
                save_location('manual', lat, lon)
                self.update_map(lat, lon)
                self.ids.status_label.text = f"Saved: {lat}, {lon}"
            else:
                self.ids.status_label.text = "Location not found"
        except Exception as e:
            self.ids.status_label.text = str(e)

    def update_map(self, lat, lon):
        self.mapview.center_on(lat, lon)
        self.marker.lat = lat
        self.marker.lon = lon

    def show_last_location_map(self):
        lat, lon = get_last_saved_location()
        if lat is not None and lon is not None:
            self.update_map(lat, lon)
            self.ids.status_label.text = f"Last saved location: {lat}, {lon}"
        else:
            self.update_map(-1.2921, 36.8219)
            self.ids.status_label.text = "No saved location. Showing default."

class VegetableSelectionScreen(Screen):
    vegetable = StringProperty('Tomato')
    growth_stage = StringProperty('initial')
    def on_pre_enter(self):
        self.ids.vegetable_spinner.text = self.vegetable
        self.ids.growth_stage_spinner.text = self.growth_stage
    def save_selection(self):
        try:
            save_vegetable_selection(self.vegetable, self.growth_stage)
            popup = show_popup("Success", f"Saved {self.vegetable} - {self.growth_stage}\n\nRedirecting to weather charts...", auto_dismiss=False)
            Clock.schedule_once(lambda dt: self.redirect_to_weather(popup), 1.5)
        except Exception as e:
            show_popup("Error", str(e))
    def redirect_to_weather(self, popup):
        popup.dismiss()
        self.manager.current = 'weather_chart'
   
class WeatherChartScreen(Screen):
    def on_pre_enter(self):
        self.load_weather()
    def load_weather(self):
        data, error = fetch_forecast_weather()
        if error or not data:
            show_popup("Error", error or "No data available.")
            return
        dates = data.get('dates')
        temps = data.get('temps')
        rain = data.get('rain')
        if not (dates and temps and rain):
            show_popup("Error", "Incomplete weather data.")
            return
        fig, ax1 = plt.subplots(figsize=(10, 5))
        if isinstance(ax1, (list, tuple, np.ndarray)):
            ax1 = ax1[0]
        ax1.plot(dates, temps, label='Temp (°C)', color='orange', marker='o')
        ax1.set_ylabel("Temperature (°C)", color='orange')
        ax1.tick_params(axis='y', labelcolor='orange')
        ax1.set_xticks(dates[::8])
        ax1.set_xticklabels(dates[::8], rotation=45, ha='right')
        ax2 = ax1.twinx()
        ax2.plot(dates, rain, label='Precipitation (mm)', color='blue', marker='s')
        ax2.set_ylabel("Rainfall (mm)", color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        plt.title("Temperature & Rainfall Forecast (OpenWeatherMap)")
        plt.tight_layout()
        chart_path = "weather_chart.png"
        plt.savefig(chart_path)
        plt.close()
        self.ids.chart_image.source = chart_path
            
class SoilMoistureScreen(Screen):
    def on_pre_enter(self):
        self.load_soil_and_et()
    def load_soil_and_et(self):
        data, _, error = fetch_soil_and_et_data()
        if error or not data:
            show_popup("Error", error or "No data available.")
            return
        soil_dates = data.get('soil_dates')
        soil_moisture = data.get('soil_moisture')
        et_dates = data.get('et_dates')
        et_values = data.get('et_values')
        if not (soil_dates and soil_moisture and et_dates and et_values):
            show_popup("Error", "Incomplete soil/ET data.")
            return
        fig, ax1 = plt.subplots(figsize=(10, 5))
        if isinstance(ax1, (list, tuple, np.ndarray)):
            ax1 = ax1[0]
        ax1.plot(soil_dates, soil_moisture, label='Soil Moisture (%)', color='green', marker='o')
        ax1.set_ylabel("Soil Moisture (%)", color='green')
        ax1.tick_params(axis='y', labelcolor='green')
        ax1.set_xticks(soil_dates)
        ax1.set_xticklabels(soil_dates, rotation=45, ha='right')
        ax2 = ax1.twinx()
        ax2.plot(et_dates, et_values, label='Evapotranspiration (mm)', color='purple', marker='s')
        ax2.set_ylabel("Evapotranspiration (mm)", color='purple')
        ax2.tick_params(axis='y', labelcolor='purple')
        plt.title("Soil Moisture Forecast & Last 5 Days Evapotranspiration")
        plt.tight_layout()
        chart_path = "soil_chart.png"
        plt.savefig(chart_path)
        plt.close()
        self.ids.soil_chart_image.source = chart_path

class RecommendationsScreen(Screen):
    def on_pre_enter(self):
        self.show_recommendation()
    def show_recommendation(self):
        # Recommendation table
        rec_table = {
            'Tomato': {
                'Initial':    {'trigger': (70, 80), 'water': '0.18–0.27'},
                'Development':{'trigger': (60, 70), 'water': '0.27–0.45'},
                'Mid-season': {'trigger': (70, 80), 'water': '0.45–0.72'},
                'Late':       {'trigger': (50, 60), 'water': '0.18–0.36'},
            },
            'Cabbage': {
                'Initial':    {'trigger': (70, 80), 'water': '0.18–0.36'},
                'Development':{'trigger': (60, 70), 'water': '0.36–0.54'},
                'Mid-season': {'trigger': (70, 80), 'water': '0.54–0.72'},
                'Late':       {'trigger': (50, 60), 'water': '0.27–0.45'},
            },
            'Carrot': {
                'Initial':    {'trigger': (70, 80), 'water': '0.18–0.27'},
                'Development':{'trigger': (60, 70), 'water': '0.27–0.45'},
                'Mid-season': {'trigger': (70, 80), 'water': '0.36–0.54'},
                'Late':       {'trigger': (50, 60), 'water': '0.18–0.36'},
            },
            'Sukuma': {
                'Initial':    {'trigger': (70, 80), 'water': '0.18–0.36'},
                'Development':{'trigger': (60, 70), 'water': '0.27–0.45'},
                'Mid-season': {'trigger': (70, 80), 'water': '0.45–0.63'},
                'Late':       {'trigger': (50, 60), 'water': '0.27–0.45'},
            },
        }
        irrigation_types = [
            ("Drip", 0.90),
            ("Laser Spray", 0.80),
            ("Sprinkler", 0.75),
            ("Furrow", 0.60),
        ]
        crop, stage = None, None
        try:
            crop, stage = get_latest_vegetable_selection()
        except Exception:
            pass
        soil_moisture = None
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT soil_moisture FROM soil_moisture_history WHERE soil_moisture IS NOT NULL ORDER BY date DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                soil_moisture = row[0]
            conn.close()
        except Exception:
            pass
        rec_msg = "Insufficient data for recommendation."
        if crop and stage and soil_moisture is not None:
            rec = rec_table.get(crop, {}).get(stage, None)
            if rec:
                min_trig, max_trig = rec['trigger']
                if soil_moisture < min_trig:
                    irrigation_type, eff = irrigation_types[0]
                    rec_msg = (
                        f"Soil moisture is {soil_moisture:.1f}%, which is below the recommended {min_trig}-{max_trig}%\n"
                        f"Irrigate with approx. {rec['water']} litres per plant per day.\n"
                        f"Recommended irrigation type: {irrigation_type} (Efficiency: {int(eff*100)}%)"
                    )
                    safe_notify(
                        title="Irrigation Alert",
                        message=(f"{crop} ({stage}): Soil moisture low! Irrigate with {rec['water']} L/plant/day using {irrigation_type}."),
                        timeout=10
                    )
                else:
                    rec_msg = f"Soil moisture is {soil_moisture:.1f}%. No irrigation needed at this stage."
        self.ids.recommendation_label.text = rec_msg

class IrrigationApp(App):
    def build(self):
        create_user_table()
        create_location_table()
        create_vegetable_table()
        sm = ScreenManager(transition=FadeTransition(duration=0.4))
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(LocationScreen(name='location'))
        sm.add_widget(VegetableSelectionScreen(name='vegetable_selection'))
        sm.add_widget(WeatherChartScreen(name='weather_chart'))
        sm.add_widget(SoilMoistureScreen(name='soil_moisture'))
        sm.add_widget(RecommendationsScreen(name='recommendations'))
        return sm

if __name__ == '__main__':
    IrrigationApp().run()
