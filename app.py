import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import streamlit as st
import folium
from streamlit_folium import st_folium

# Functie om coördinaten op te halen
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Location '{location_name}, {country_name}' not found")

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

# Functie om te bepalen welke API te gebruiken (historisch of forecast)
def get_api_url_and_params(date, latitude, longitude):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if date == today or date == yesterday:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "apparent_temperature", "cloudcover", "cloudcover_low", "cloudcover_mid",
                       "cloudcover_high", "wind_speed_10m", "wind_direction_10m", "visibility", "precipitation"],
            "timezone": "Europe/Berlin",
            "past_days": 1 if date == yesterday else 0
        }
    else:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date,
            "end_date": date,
            "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "precipitation", "cloudcover",
                       "cloudcover_low", "cloudcover_mid", "cloudcover_high", "visibility"],
            "timezone": "Europe/Berlin"
        }
    return url, params

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

# Functie om decimale coördinaten om te zetten naar graad, minuut, seconde formaat
def decimal_to_dms(degrees):
    g = int(degrees)
    minutes = (degrees - g) * 60
    m = int(minutes)
    seconds = (minutes - m) * 60
    s = round(seconds, 1)
    return g, m, s

# Functie om decimale coördinaten om te zetten naar het gewenste formaat met N/S, E/W
def format_coordinates(lat, lon):
    lat_d, lat_m, lat_s = decimal_to_dms(abs(lat))
    lon_d, lon_m, lon_s = decimal_to_dms(abs(lon))
    
    lat_direction = "N" if lat >= 0 else "S"
    lon_direction = "E" if lon >= 0 else "W"
    
    return f"{lat_d}°{lat_m}'{lat_s}\"{lat_direction} {lon_d}°{lon_m}'{lon_s}\"{lon_direction}"

# Functie om de kaart weer te geven met de locatie
def plot_location_on_map(lat, lon, zoom_start=2):
    # Creëer een kaart met een basis zoomniveau voor de wereld
    map = folium.Map(location=[0, 0], zoom_start=zoom_start)  # begin met de wereldkaart
    
    if lat and lon:
        # Inzoomen naar de specifieke locatie
        map = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup=f"Locatie: {lat}, {lon}").add_to(map)
    
    # Geef de kaart weer in de Streamlit-app
    return map

# Streamlit app
def main():
    st.title("Weer Data Viewer met Locatie en Kaart")

    # Invoervelden voor locatie en tijd
    location_name = st.text_input("Voer de naam van de plaats in:")
    country_name = st.selectbox("Kies een land:", [
        "Albania", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium", "Bosnia and Herzegovina",
        "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "Georgia",
        "Germany", "Greece", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Israel",
        "Italy", "Kazakhstan", "Kosovo", "Kuwait", "Kyrgyzstan", "Latvia", "Liechtenstein", "Lithuania",
        "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Morocco", "Nepal", "Netherlands", "Norway",
        "Oman", "Pakistan", "Palestinian Territories", "Poland", "Portugal", "Qatar", "Romania", "Russia",
        "San Marino", "Saudi Arabia", "Serbia", "Singapore", "Slovakia", "Slovenia", "South Korea", "Spain",
        "Sri Lanka", "Syria", "Tajikistan", "Thailand", "Turkey", "Turkmenistan", "Ukraine", "United Kingdom",
        "Uzbekistan", "Vietnam", "Yemen"
    ])
    date = st.date_input("Voer de datum in:").strftime("%Y-%m-%d")
    start_time = st.time_input("Kies het startuur:", datetime(2023, 1, 1, 12, 0)).strftime("%H:%M")
    end_time = st.time_input("Kies het einduur:", datetime(2023, 1, 1, 12, 0)).strftime("%H:%M")
    
    if location_name and country_name:
        try:
            # Coördinaten ophalen
            lat, lon = get_coordinates(location_name, country_name)
            st.write(f"Coördinaten voor {location_name}: {lat}, {lon}")
            
            # De weerdata verkrijgen
            times, temperatures, cloudcovers, cloudcover_low, cloudcover_mid, cloudcover_high, wind_speeds, wind_directions, visibility, precipitation = get_forecast(lat, lon)
            
            # Maak een kaart van de locatie
            map = plot_location_on_map(lat, lon)
            st_folium(map, width=800, height=600)
            
        except ValueError as e:
            st.error(f"Error: {str(e)}")
