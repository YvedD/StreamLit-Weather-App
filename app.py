import streamlit as st
import datetime
import requests
import json
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Functie om de coördinaten van de locatie op te halen
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Functie om de coördinaten naar een begrijpelijk formaat om te zetten
def format_coordinates(lat, lon):
    lat_d, lat_m, lat_s = decimal_to_dms(abs(lat))
    lon_d, lon_m, lon_s = decimal_to_dms(abs(lon))
    
    lat_direction = "N" if lat >= 0 else "S"
    lon_direction = "E" if lon >= 0 else "W"
    
    return f"{lat_d}°{lat_m}'{lat_s}\"{lat_direction} {lon_d}°{lon_m}'{lon_s}\"{lon_direction}"

# Functie om decimale coördinaten om te zetten naar graad, minuut, seconde formaat
def decimal_to_dms(degrees):
    g = int(degrees)
    minutes = (degrees - g) * 60
    m = int(minutes)
    seconds = (minutes - m) * 60
    s = round(seconds, 1)
    return g, m, s

# Functie om historische gegevens op te halen van de Open-Meteo API
def fetch_weather_data(latitude, longitude, start_time, end_time):
    historical_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={start_time.strftime('%Y-%m-%d')}&end_date={end_time.strftime('%Y-%m-%d')}&hourly=temperature_2m,cloudcover,precipitation,wind_speed_10m,wind_direction_10m,visibility"
    response = requests.get(historical_url)
    data = response.json()

    # Controleer de respons en log de gegevens
    st.write("Open-Meteo Historical Data Response:")
    st.write(data)

    historical_data = []
    for i in range(len(data['hourly']['temperature_2m'])):
        timestamp = start_time + datetime.timedelta(hours=i)
        temp = data['hourly']['temperature_2m'][i]
        cloud = data['hourly']['cloudcover'][i]
        precip = data['hourly']['precipitation'][i]
        wind_speed = data['hourly']['wind_speed_10m'][i]
        wind_dir = data['hourly']['wind_direction_10m'][i]
        vis = data['hourly']['visibility'][i]
        
        historical_data.append({
            "timestamp": timestamp,
            "temp": temp,
            "cloud": cloud,
            "precip": precip,
            "wind_dir": wind_dir,
            "wind_speed": wind_speed,
            "vis": vis
        })
    return historical_data

# Functie om weersvoorspellingen op te halen van de Open-Meteo API
def fetch_forecast_data(latitude, longitude):
    forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,cloudcover_mean,wind_speed_10m_max,wind_direction_10m_max,visibility_mean&timezone=Europe/Brussels"
    response = requests.get(forecast_url)
    data = response.json()

    # Controleer de respons en log de gegevens
    st.write("Open-Meteo Forecast Data Response:")
    st.write(data)

    # Zorg ervoor dat de data de verwachte structuur heeft
    if 'daily' not in data or 'temperature_2m_max' not in data['daily']:
        st.error("Er is een probleem met het ophalen van de weersvoorspellingen. Controleer de invoer en probeer het opnieuw.")
        return []

    forecast_data = []
    for i in range(len(data['daily']['temperature_2m_max'])):
        forecast_data.append({
            "day": f"Dag {i+1}",
            "temp_max": data['daily']['temperature_2m_max'][i],
            "temp_min": data['daily']['temperature_2m_min'][i],
            "precip": data['daily']['precipitation_sum'][i],
            "cloud": data['daily']['cloudcover_mean'][i],
            "wind_speed": data['daily']['wind_speed_10m_max'][i],
            "wind_dir": data['daily']['wind_direction_10m_max'][i],
            "vis": data['daily']['visibility_mean'][i]
        })
    return forecast_data

# Functie om de locatie op een kaart te tonen
def plot_location_on_map(lat, lon, zoom_start=10):
    map = folium.Map(location=[lat, lon], zoom_start=zoom_start)
    folium.Marker([lat, lon], popup=f"Locatie: {lat}, {lon}").add_to(map)
    return map

# Gebruik van session_state om gegevens en status te behouden
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = None
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = None
if 'location' not in st.session_state:
    st.session_state.location = ""

# Hoofdapplicatie
def main():
    st.title("Weerapplicatie voor Locaties")

    # Invoervelden voor land, locatie, datum, beginuur en einduur
    country = st.selectbox("Kies een land", ["Belgium", "Nederland", "Frankrijk", "Duitsland", "Luxemburg"], index=0)
    location_name = st.text_input("Voer de naam van de plaats in:")
    date = st.date_input("Kies een datum", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())
    start_time = st.time_input("Kies een beginuur", value=datetime.time(8, 0))
    end_time = st.time_input("Kies een einduur", value=datetime.time(15, 0))

    # Functie om historische data en voorspellingen te tonen
    if st.button("Opzoeken"):
        if location_name:
            latitude, longitude = get_coordinates(location_name, country)
            st.session_state.coordinates = (latitude, longitude)
            st.session_state.location = location_name

            # Haal de historische gegevens op
            st.session_state.historical_data = fetch_weather_data(latitude, longitude, datetime.datetime.combine(date, start_time), datetime.datetime.combine(date, end_time))

            # Haal de voorspellingen op
            st.session_state.forecast_data = fetch_forecast_data(latitude, longitude)

    # 3 expanders voor weergave
    with st.expander("Weatherdata", expanded=False):
        if st.session_state.historical_data:
            # Maak een DataFrame van historische gegevens
            historical_df = pd.DataFrame(st.session_state.historical_data)
            historical_df['timestamp'] = historical_df['timestamp'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
            st.write(historical_df.to_string(index=False))
        else:
            st.write("Voer de locatie en datum in en klik op 'Opzoeken' om historische gegevens op te halen.")

    with st.expander("Map of location", expanded=False):
        if st.session_state.coordinates:
            lat, lon = st.session_state.coordinates
            map = plot_location_on_map(lat, lon)
            st_folium(map, width=700, height=500)
        else:
            st.write("Voer de locatie in en klik op 'Opzoeken' om de kaart te tonen.")

    with st.expander("3 day's Forecast for this location", expanded=False):
        if st.session_state.forecast_data:
            forecast_df = pd.DataFrame(st.session_state.forecast_data)
            st.write(forecast_df.to_string(index=False))
        else:
            st.write("Voer de locatie in en klik op 'Opzoeken' om de voorspellingen te bekijken.")

if __name__ == "__main__":
    main()
