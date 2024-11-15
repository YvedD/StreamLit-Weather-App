import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import streamlit as st

# Functie om coördinaten op te halen
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Location '{location_name}' not found")

# Functie om windrichting om te zetten naar Nederlandse benamingen
def wind_direction_to_dutch(direction):
    directions = {
        'N': 'N', 'NNE': 'NNO', 'NE': 'NO', 'ENE': 'ONO', 'E': 'O', 'ESE': 'OZO', 'SE': 'ZO', 'SSE': 'ZZO',
        'S': 'Z', 'SSW': 'ZZW', 'SW': 'ZW', 'WSW': 'WZW', 'W': 'W', 'WNW': 'WNW', 'NW': 'NW', 'NNW': 'NNW'
    }
    index = round(direction / 22.5) % 16
    direction_name = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][index]
    return directions.get(direction_name, 'Onbekend')

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
def wind_speed_to_beaufort(speed_kmh):
    speed = speed_kmh / 3.6
    beaufort_scale = [(0.3, 0), (1.6, 1), (3.4, 2), (5.5, 3), (8.0, 4), (10.7, 5), (13.8, 6), (17.2, 7), 
                      (20.8, 8), (24.5, 9), (28.2, 10), (32.1, 11)]
    for threshold, bf in beaufort_scale:
        if speed < threshold:
            return bf
    return 12

# Functie om voorspelling voor de komende drie dagen op te halen
def get_forecast(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", 
                   "cloud_cover_high", "visibility", "wind_speed_10m", "wind_direction_10m"],
        "timezone": "Europe/Berlin",
        "forecast_days": 3
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    hourly = data.get("hourly", {})
    
    # Data inlezen
    times = pd.to_datetime(hourly.get("time", []))
    temperatures = np.array(hourly.get("temperature_2m", []))
    cloudcovers = np.array(hourly.get("cloud_cover", []))
    cloudcover_low = np.array(hourly.get("cloud_cover_low", []))
    cloudcover_mid = np.array(hourly.get("cloud_cover_mid", []))
    cloudcover_high = np.array(hourly.get("cloud_cover_high", []))
    wind_speeds = np.array(hourly.get("wind_speed_10m", []))
    wind_directions = np.array(hourly.get("wind_direction_10m", []))
    visibility = np.array(hourly.get("visibility", []))
    precipitation = np.array(hourly.get("precipitation", []))
    
    return times, temperatures, cloudcovers, cloudcover_low, cloudcover_mid, cloudcover_high, wind_speeds, wind_directions, visibility, precipitation

# Streamlit app
def main():
    st.title("Weather Data Viewer")

    location_name = st.text_input("Voer de naam van de plaats in:")
    if st.button("3-daagse voorspelling ophalen"):
        try:
            # Coördinaten ophalen
            latitude, longitude = get_coordinates(location_name)
            st.write(f"Weersvoorspelling voor {location_name} (latitude: {latitude}, longitude: {longitude})")

            # Voorspelling ophalen
            forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_cloudcover_low, forecast_cloudcover_mid, \
            forecast_cloudcover_high, forecast_wind_speeds, forecast_wind_directions, forecast_visibility, forecast_precipitation = get_forecast(latitude, longitude)
            
            # 3-daagse voorspelling per uur weergeven met datum prefix
            st.subheader("3-daagse voorspelling per uur")
            forecast_text = ""
            for forecast_time, temp, cloud, cloud_low, cloud_mid, cloud_high, wind_speed, wind_dir, vis, precip in zip(
                    forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_cloudcover_low,
                    forecast_cloudcover_mid, forecast_cloudcover_high, forecast_wind_speeds, forecast_wind_directions,
                    forecast_visibility, forecast_precipitation):
                
                # Datum en tijd instellen met prefix
                forecast_date = forecast_time.strftime("%Y-%m-%d")
                time_str = forecast_time.strftime("%H:%M")
                
                # Windrichting, windkracht in Beaufort en zichtbaarheid omzetten
                wind_bf = wind_speed_to_beaufort(wind_speed)
                vis_km = vis / 1000 if vis <= 100000 else 0  # Correcte zichtbaarheid naar kilometers
                line = f"{forecast_date} {time_str}: Temp.{temp:.1f}°C - Neersl.{precip}mm - Bew.{cloud}% (L:{cloud_low}%, M:{cloud_mid}%, H:{cloud_high}%) - {wind_direction_to_dutch(wind_dir)} {wind_bf}Bf - Visi.{vis_km:.1f}km"
                
                # Voeg lijn toe aan de tekstuitvoer
                forecast_text += line + "\n"
                
            # Weergeven als tekst
            st.text(forecast_text)
        
        except requests.exceptions.RequestException as e:
            st.error(f"Fout bij API-aanroep: {e}")
        except ValueError as e:
            st.error(f"Fout: {e}")

# Voer de main functie uit
if __name__ == "__main__":
    main()
