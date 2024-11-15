import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import streamlit as st

# Zet de pagina in Wide Mode
st.set_page_config(layout="wide")

# CSS voor het instellen van de breedte
st.markdown("""
    <style>
        .container {
            width: 80%;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Lijst van landen in Europa, Nabije Oosten en Azië
countries = [
    "België", "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Bahrain", "Belarus", "Bosnia and Herzegovina", 
    "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia", 
    "Germany", "Greece", "Hungary", "Iceland", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jordan", "Kazakhstan", 
    "Kosovo", "Kuwait", "Kyrgyzstan", "Latvia", "Lebanon", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", 
    "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Oman", "Pakistan", "Palestine", 
    "Poland", "Portugal", "Qatar", "Romania", "Russia", "San Marino", "Saudi Arabia", "Serbia", "Singapore", 
    "Slovakia", "Slovenia", "South Korea", "Spain", "Sri Lanka", "Syria", "Sweden", "Switzerland", "Tajikistan", 
    "Turkey", "Turkmenistan", "Ukraine", "United Arab Emirates", "United Kingdom", "Uzbekistan", "Yemen", 
    "China", "Japan", "India", "Indonesia", "Malaysia", "Mongolia", "Nepal", "North Korea", "Philippines", "Singapore", 
    "South Korea", "Thailand", "Vietnam"
]

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

# Functie om de juiste API URL en parameters te bepalen (historisch of vandaag)
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

# Functie om 3-daagse voorspelling op te halen
def get_forecast(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "cloudcover", "cloudcover_low", "cloudcover_mid", 
                   "cloudcover_high", "visibility", "wind_speed_10m", "wind_direction_10m"],
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
    cloudcovers = np.array(hourly.get("cloudcover", []))
    cloudcover_low = np.array(hourly.get("cloudcover_low", []))
    cloudcover_mid = np.array(hourly.get("cloudcover_mid", []))
    cloudcover_high = np.array(hourly.get("cloudcover_high", []))
    wind_speeds = np.array(hourly.get("wind_speed_10m", []))
    wind_directions = np.array(hourly.get("wind_direction_10m", []))
    visibility = np.array(hourly.get("visibility", []))
    precipitation = np.array(hourly.get("precipitation", []))
    
    return times, temperatures, cloudcovers, cloudcover_low, cloudcover_mid, cloudcover_high, wind_speeds, wind_directions, visibility, precipitation

# Streamlit app
def main():
    st.title("Weather Data Viewer")

    # Gebruik de container met de breedte van 80%
    with st.container():
        st.markdown("<div class='container'>", unsafe_allow_html=True)

        # Invoervelden voor locatie en land
        country_name = st.selectbox("Kies het land:", countries, index=countries.index("België"))
        location_name = st.text_input(f"Voer de naam van de plaats in in {country_name}:")
        date = st.date_input("Kies de datum voor historische gegevens:", datetime.today()).strftime("%Y-%m-%d")
        start_time = st.time_input("Starttijd:", datetime(2023, 1, 1, 12, 0)).strftime("%H:%M")
        end_time = st.time_input("Eindtijd:", datetime(2023, 1, 1, 12, 0)).strftime("%H:%M")

        if st.button("Gegevens ophalen"):
            try:
                # Coördinaten ophalen
                latitude, longitude = get_coordinates(location_name, country_name)
                st.write(f"Gegevens voor {location_name}, {country_name} (latitude: {latitude}, longitude: {longitude}) op {date}")

                # Verkrijg de juiste API URL en parameters
                url, params = get_api_url_and_params(date, latitude, longitude)

                # API-aanroep voor historische gegevens
                response = requests.get(url, params=params)
                response.raise_for_status()
