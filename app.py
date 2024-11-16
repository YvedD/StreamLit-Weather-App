import streamlit as st
from datetime import datetime, timedelta
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import folium_static

# Functies voor windrichting en omrekening naar Beaufort
def degrees_to_direction(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    ix = int((degrees + 22.5) / 45)
    return directions[ix % 8]

def kmh_to_beaufort(speed_kmh):
    if speed_kmh < 1:
        return 0
    elif speed_kmh <= 5:
        return 1
    elif speed_kmh <= 11:
        return 2
    elif speed_kmh <= 19:
        return 3
    elif speed_kmh <= 28:
        return 4
    elif speed_kmh <= 38:
        return 5
    elif speed_kmh <= 49:
        return 6
    elif speed_kmh <= 61:
        return 7
    elif speed_kmh <= 74:
        return 8
    elif speed_kmh <= 88:
        return 9
    elif speed_kmh <= 102:
        return 10
    elif speed_kmh <= 117:
        return 11
    else:
        return 12

# Functie om weergegevens op te halen van de Open-Meteo API
def fetch_weather_data(latitude, longitude, start_date, end_date):
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_direction_80m&daily=sunrise,sunset&timezone=Europe%2FBerlin"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Fout bij het ophalen van weergegevens: {response.status_code}")
        return None

# Functie om een locatie op de kaart te tonen
def show_location_on_map(latitude, longitude, location_name):
    m = folium.Map(location=[latitude, longitude], zoom_start=12)
    folium.Marker([latitude, longitude], popup=location_name).add_to(m)
    folium_static(m)

# Hoofdcode van de app
st.title("Weerdata en Kaartweergave")

# Standaardwaarden voor de invoervelden
default_country = "België"
default_location = "Bredene"
default_date = datetime.today() - timedelta(days=1)  # Gisteren
default_start_time = "08:00"
default_end_time = "16:00"

# Gebruikersinvoer
country = st.text_input("Land", value=default_country)
location_name = st.text_input("Locatie", value=default_location)

# Maak het datumveld en tijdvelden dynamisch
selected_date = st.date_input("Selecteer een datum", default_date)
start_time = st.selectbox("Selecteer startuur", [f"{i:02}:00" for i in range(24)], index=8)  # Standaardwaarde 08:00
end_time = st.selectbox("Selecteer einduur", [f"{i:02}:00" for i in range(24)], index=16)  # Standaardwaarde 16:00

# Haal de geografische coördinaten op
geolocator = Nominatim(user_agent="weather_app")
location = geolocator.geocode(f"{location_name}, {country}")

if location:
    latitude, longitude = location.latitude, location.longitude
    
    # Toon de kaart in de tweede expander
    with st.expander("Kaart Weergave"):
        show_location_on_map(latitude, longitude, location_name)

    # Verkrijg de historische weerdata
    start_date = selected_date  # De startdatum wordt ingesteld op de geselecteerde datum
    end_date = selected_date    # De einddatum wordt ingesteld op dezelfde geselecteerde datum
    
    # Gebruik de geselecteerde datums en tijdsopties
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    weather_data = fetch_weather_data(latitude, longitude, start_date_str, end_date_str)

    if weather_data:
        # Verkrijg de gegevens van de API response
        hourly = weather_data['hourly']
        times = [datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M") for i in range(len(hourly['time']))]
        temperatures = hourly['temperature_2m']
        wind_speeds = [kmh_to_beaufort(speed) for speed in hourly['wind_speed_10m']]
        wind_directions = [degrees_to_direction(deg) if deg is not None else '' for deg in hourly['wind_direction_80m']]
        cloudcover = hourly['cloud_cover']
        cloudcover_low = hourly['cloud_cover_low']
        cloudcover_mid = hourly['cloud_cover_mid']
        cloudcover_high = hourly['cloud_cover_high']
        precipitation = hourly['precipitation']

        # Toon de historische weergegevens in de eerste expander
        with st.expander("Historische Weergegevens - Kort Overzicht"):
            for i in range(len(times)):
                weather_info = f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf"
                st.code(weather_info, language="plaintext")
