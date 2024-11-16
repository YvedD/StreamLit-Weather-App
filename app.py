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
def fetch_weather_data(latitude, longitude, start_date, end_date, start_hour, end_hour):
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_direction_80m&daily=sunrise,sunset&timezone=Europe%2FBerlin"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        filtered_data = {
            'time': [],
            'temperature_2m': [],
            'precipitation': [],
            'cloud_cover': [],
            'cloud_cover_low': [],
            'cloud_cover_mid': [],
            'cloud_cover_high': [],
            'wind_speed_10m': [],
            'wind_direction_80m': []
        }

        # Filter data based on the selected time range
        for i, time in enumerate(data['hourly']['time']):
            time_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M")
            if start_hour <= time_obj.hour < end_hour:
                for key in filtered_data.keys():
                    filtered_data[key].append(data['hourly'][key][i])

        return filtered_data
    else:
        st.error(f"Fout bij het ophalen van weergegevens: {response.status_code}")
        return None

# Functie om een locatie op de kaart te tonen
def show_location_on_map(latitude, longitude, location_name):
    m = folium.Map(location=[latitude, longitude], zoom_start=12)
    folium.Marker([latitude, longitude], popup=location_name).add_to(m)
    # Pas de breedte van de kaart aan zodat deze past binnen de expander
    folium_static(m, width=700)  # Hier stellen we de breedte in op 700 pixels

# Hoofdcode van de app
st.title("Weerdata en Kaartweergave")

# Standaardwaarden voor de invoervelden
default_country = "België"
default_location = "Bredene"
default_date = datetime.today() - timedelta(days=1)  # Gisteren
default_start_time = "08:00"
default_end_time = "16:00"

# Lijst van Europese landen voor de dropdown
countries = ["België", "Nederland", "Frankrijk", "Duitsland", "Luxemburg"]

# Gebruikersinvoer
country = st.selectbox("Land", countries, index=countries.index(default_country))
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
    
    # Verkrijg de historische weerdata
    start_date = selected_date  # De startdatum wordt ingesteld op de geselecteerde datum
    end_date = selected_date    # De einddatum wordt ingesteld op dezelfde geselecteerde datum
    
    # Gebruik de geselecteerde datums en tijdsopties
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_hour = int(start_time[:2])  # Haal het uur uit de starttijd
    end_hour = int(end_time[:2])      # Haal het uur uit de eindtijd

    weather_data = fetch_weather_data(latitude, longitude, start_date_str, end_date_str, start_hour, end_hour)

    if weather_data:
        # Verkrijg de gegevens van de API response
        times = [datetime.strptime(weather_data['time'][i], "%Y-%m-%dT%H:%M") for i in range(len(weather_data['time']))]
        temperatures = weather_data['temperature_2m']
        wind_speeds = [kmh_to_beaufort(speed) for speed in weather_data['wind_speed_10m']]
        wind_directions = [degrees_to_direction(deg) if deg is not None else '' for deg in weather_data['wind_direction_80m']]
        cloudcover = weather_data['cloud_cover']
        cloudcover_low = weather_data['cloud_cover_low']
        cloudcover_mid = weather_data['cloud_cover_mid']
        cloudcover_high = weather_data['cloud_cover_high']
        precipitation = weather_data['precipitation']

        # Toon de historische weergegevens in de eerste expander
        with st.expander("Historische Weergegevens - Kort Overzicht"):
            for i in range(len(times)):
                weather_info = f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf"
                st.code(weather_info, language="plaintext")

        # Toon de kaart in de tweede expander
        with st.expander("Kaart Weergave"):
            show_location_on_map(latitude, longitude, location_name)
