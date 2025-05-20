import customtkinter as ctk
import requests
import json
import os
from PIL import Image, ImageTk

# --- Configuration ---
# You need to get your own API key from a weather service (e.g., OpenWeatherMap, WeatherAPI.com)
# Create a config.ini file in the same directory as main.py and add your API key:
# [weather]
# api_key = YOUR_API_KEY_HERE

# For demonstration, we'll use a placeholder API key. Replace this!
API_KEY = "YOUR_API_KEY_HERE" # <<< IMPORTANT: Replace with your actual API key!
BASE_URL = "http://api.openweathermap.org/data/2.5/weather" # OpenWeatherMap example
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast" # For chance of rain (5-day forecast)

# List of major cities in Indian states for demonstration
INDIAN_CITIES = {
    "Andhra Pradesh": "Hyderabad",
    "Arunachal Pradesh": "Itanagar",
    "Assam": "Guwahati",
    "Bihar": "Patna",
    "Chhattisgarh": "Raipur",
    "Goa": "Panaji",
    "Gujarat": "Ahmedabad",
    "Haryana": "Chandigarh",
    "Himachal Pradesh": "Shimla",
    "Jharkhand": "Ranchi",
    "Karnataka": "Bengaluru",
    "Kerala": "Kochi",
    "Madhya Pradesh": "Bhopal",
    "Maharashtra": "Mumbai",
    "Manipur": "Imphal",
    "Meghalaya": "Shillong",
    "Mizoram": "Aizawl",
    "Nagaland": "Kohima",
    "Odisha": "Bhubaneswar",
    "Punjab": "Chandigarh",
    "Rajasthan": "Jaipur",
    "Sikkim": "Gangtok",
    "Tamil Nadu": "Chennai",
    "Telangana": "Hyderabad",
    "Tripura": "Agartala",
    "Uttar Pradesh": "Lucknow",
    "Uttarakhand": "Dehradun",
    "West Bengal": "Kolkata"
}

# --- GUI Setup ---
class RainPredictionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Indian Rain & Weather Forecast")
        self.geometry("900x700")
        self.resizable(False, False)

        # Set theme
        ctk.set_appearance_mode("Dark") # Options: "Light", "Dark", "System"
        ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

        # Load assets
        self.load_assets()

        # Create frames
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=20, padx=20, fill="x")

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.create_widgets()

        # Initial weather update for all states
        self.update_all_states_weather()

    def load_assets(self):
        script_dir = os.path.dirname(__file__)
        assets_dir = os.path.join(script_dir, "assets")

        try:
            self.rain_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "rain_icon.png")), size=(30, 30))
            self.sun_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "sun_icon.png")), size=(30, 30))
            self.cloud_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "cloud_icon.png")), size=(30, 30))
            self.clear_day_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "clear_day_icon.png")), size=(30, 30))
            self.thunderstorm_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "thunderstorm_icon.png")), size=(30, 30))
            self.drizzle_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "drizzle_icon.png")), size=(30, 30))
            self.snow_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "snow_icon.png")), size=(30, 30))
            self.mist_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "mist_icon.png")), size=(30, 30))
            self.humidity_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "humidity_icon.png")), size=(20, 20))
            self.wind_icon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "wind_icon.png")), size=(20, 20))

        except FileNotFoundError:
            print("Warning: Weather icons not found in 'assets/' directory. Using default labels.")
            self.rain_icon = None # Set to None if not found
            self.sun_icon = None
            self.cloud_icon = None
            self.clear_day_icon = None
            self.thunderstorm_icon = None
            self.drizzle_icon = None
            self.snow_icon = None
            self.mist_icon = None
            self.humidity_icon = None
            self.wind_icon = None

    def get_weather_icon(self, weather_main):
        if self.rain_icon:
            weather_main = weather_main.lower()
            if "rain" in weather_main or "drizzle" in weather_main:
                return self.rain_icon
            elif "clear" in weather_main:
                return self.clear_day_icon
            elif "cloud" in weather_main:
                return self.cloud_icon
            elif "thunderstorm" in weather_main:
                return self.thunderstorm_icon
            elif "snow" in weather_main:
                return self.snow_icon
            elif "mist" in weather_main or "fog" in weather_main or "haze" in weather_main:
                return self.mist_icon
            else:
                return self.sun_icon # Default to sun for other conditions
        return None # Return None if icons are not loaded

    def create_widgets(self):
        # Header
        self.header_label = ctk.CTkLabel(self.header_frame, text="🌦️ India Weather & Rain Forecast ☔", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack()

        self.refresh_button = ctk.CTkButton(self.header_frame, text="Refresh Data", command=self.update_all_states_weather, font=ctk.CTkFont(size=14, weight="bold"))
        self.refresh_button.pack(pady=10)

        # Scrollable frame for states
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, corner_radius=10, border_width=2, border_color="#555555")
        self.scrollable_frame.pack(fill="both", expand=True)

        self.state_frames = {} # Dictionary to store state weather frames

        row_idx = 0
        col_idx = 0
        for state, city in INDIAN_CITIES.items():
            state_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10, fg_color="#333333", border_width=1, border_color="#666666")
            state_frame.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")
            self.scrollable_frame.grid_columnconfigure(col_idx, weight=1) # Make columns expandable

            # Store references to labels for easy updates
            state_info = {
                "state_label": ctk.CTkLabel(state_frame, text=state, font=ctk.CTkFont(size=18, weight="bold"), text_color="#ADD8E6"), # Light Blue
                "city_label": ctk.CTkLabel(state_frame, text=f"City: {city}", font=ctk.CTkFont(size=12, weight="bold")),
                "temp_label": ctk.CTkLabel(state_frame, text="Temp: N/A", font=ctk.CTkFont(size=16)),
                "weather_label": ctk.CTkLabel(state_frame, text="Weather: N/A", font=ctk.CTkFont(size=14)),
                "rain_chance_label": ctk.CTkLabel(state_frame, text="Rain Chance: N/A", font=ctk.CTkFont(size=14), text_color="#90EE90"), # Light Green
                "humidity_label": ctk.CTkLabel(state_frame, text="Humidity: N/A", font=ctk.CTkFont(size=12), image=self.humidity_icon, compound="left", anchor="w"),
                "wind_label": ctk.CTkLabel(state_frame, text="Wind: N/A", font=ctk.CTkFont(size=12), image=self.wind_icon, compound="left", anchor="w"),
                "icon_label": ctk.CTkLabel(state_frame, text="", image=None) # Placeholder for weather icon
            }

            state_info["state_label"].pack(pady=(10, 5))
            state_info["city_label"].pack(pady=2)
            state_info["icon_label"].pack(pady=5)
            state_info["temp_label"].pack(pady=2)
            state_info["weather_label"].pack(pady=2)
            state_info["rain_chance_label"].pack(pady=2)
            state_info["humidity_label"].pack(pady=2)
            state_info["wind_label"].pack(pady=(2, 10))

            self.state_frames[state] = state_info

            col_idx += 1
            if col_idx >= 3: # 3 columns per row
                col_idx = 0
                row_idx += 1

    def get_weather_data(self, city):
        try:
            # Current weather
            params = {"q": city, "appid": API_KEY, "units": "metric"}
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors
            current_weather_data = response.json()

            # 5-day forecast for rain probability
            forecast_params = {"q": city, "appid": API_KEY, "units": "metric"}
            forecast_response = requests.get(FORECAST_URL, params=forecast_params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            return current_weather_data, forecast_data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather for {city}: {e}")
            return None, None
        except json.JSONDecodeError:
            print(f"Error decoding JSON for {city}. API response might be malformed.")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred for {city}: {e}")
            return None, None

    def calculate_rain_chance(self, forecast_data):
        if not forecast_data or "list" not in forecast_data:
            return "N/A"

        rain_timestamps = 0
        total_timestamps = 0
        for item in forecast_data["list"]:
            total_timestamps += 1
            if "rain" in item:
                rain_timestamps += 1
            elif "weather" in item:
                weather_description = item["weather"][0]["main"].lower()
                if "rain" in weather_description or "drizzle" in weather_description or "thunderstorm" in weather_description:
                    rain_timestamps += 1

        if total_timestamps > 0:
            chance = (rain_timestamps / total_timestamps) * 100
            return f"{chance:.0f}%"
        return "0%"

    def update_all_states_weather(self):
        for state, city in INDIAN_CITIES.items():
            self.update_state_weather(state, city)

    def update_state_weather(self, state, city):
        current_weather_data, forecast_data = self.get_weather_data(city)
        state_info = self.state_frames[state]

        if current_weather_data and forecast_data:
            temp_celsius = current_weather_data["main"]["temp"]
            weather_desc = current_weather_data["weather"][0]["description"].capitalize()
            humidity = current_weather_data["main"]["humidity"]
            wind_speed = current_weather_data["wind"]["speed"] # in m/s from OpenWeatherMap
            wind_speed_kmph = wind_speed * 3.6 # Convert to km/h

            rain_chance = self.calculate_rain_chance(forecast_data)

            state_info["temp_label"].configure(text=f"Temp: {temp_celsius:.1f}°C")
            state_info["weather_label"].configure(text=f"Weather: {weather_desc}")
            state_info["rain_chance_label"].configure(text=f"Rain Chance: {rain_chance}")
            state_info["humidity_label"].configure(text=f"Humidity: {humidity}%")
            state_info["wind_label"].configure(text=f"Wind: {wind_speed_kmph:.1f} km/h")

            # Update icon
            icon_image = self.get_weather_icon(current_weather_data["weather"][0]["main"])
            if icon_image:
                state_info["icon_label"].configure(image=icon_image)
            else:
                state_info["icon_label"].configure(text=weather_desc, image=None) # Fallback to text if no icon

        else:
            state_info["temp_label"].configure(text="Temp: N/A")
            state_info["weather_label"].configure(text="Weather: N/A")
            state_info["rain_chance_label"].configure(text="Rain Chance: N/A")
            state_info["humidity_label"].configure(text="Humidity: N/A")
            state_info["wind_label"].configure(text="Wind: N/A")
            state_info["icon_label"].configure(text="No Data", image=None)


if __name__ == "__main__":
    # Create an 'assets' directory and place your icons there.
    # Example icon filenames: rain_icon.png, sun_icon.png, cloud_icon.png, etc.
    # You can download free weather icons from sites like Flaticon or create your own.
    # For a minimal setup, you can comment out the icon loading and rely on text.
    
    # Create assets directory if it doesn't exist
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Created 'assets/' directory. Please place weather icons inside.")
        print("Required icons: rain_icon.png, sun_icon.png, cloud_icon.png, clear_day_icon.png, thunderstorm_icon.png, drizzle_icon.png, snow_icon.png, mist_icon.png, humidity_icon.png, wind_icon.png")

    app = RainPredictionApp()
    app.mainloop()