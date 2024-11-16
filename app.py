import streamlit as st
import requests
import json
from geopy.geocoders import Nominatim
import folium
from datetime import datetime, timedelta
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt

# Functie om windrichtingen om te zetten naar afkortingen
def degrees_to_direction(degrees):
    directions = ['N', 'NNO', 'NO', 'ONO', 'O', 'OZO', 'ZO', 'ZZO', 'Z', 'ZZW', 'ZW', 'WZW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
def kmh_to_beaufort(kmh):
    if kmh is None:
        return None
    elif kmh < 1:
        return 0
    elif kmh <= 5:
        return 1
    elif kmh <= 11:
        return 2
    elif kmh <= 19:
        return 3
    elif kmh <= 28:
        return 4
    elif kmh <= 38:
        return 5
    elif kmh <= 49:
        return 6
    elif kmh <= 61:
        return 7
    elif kmh <= 74:
        return 8
    elif kmh <= 88:
        return 9
    elif kmh <= 102:
        return 10
    elif kmh <= 117:
        return 11
    else:
        return 12

# Invoer voor locatie en datum/tijdinstellingen
st.title("Weerdata Opvragen met Locatie Weergave")
country = st.text_input("Land (bijv. Nederland):", "Nederland")
location_name = st.text_input("Stad/Locatie (bijv. Amsterdam):", "Amsterdam")
start_date_input = st.date_input("Selecteer de datum:", datetime.now().date())

# Volle uren selecties
hours = [f"{str(i).zfill(2)}:00" for i in range(24)]
start_hour = st.selectbox("Startuur:", hours, index=0)
end_hour = st.selectbox("Einduur:", hours, index=23)

# Bereken de start- en einddatums voor historische gegevens
start_date = start_date_input - timedelta(days=8)
end_date = start_date_input

# Initialiseer geolocator
geolocator = Nominatim(user_agent="weather_app")
location = geolocator.geocode(f"{location_name}, {country}")

if location:
    latitude, longitude = location.latitude, location.longitude

    # Maak drie expanders voor overzicht, voorspellingen en historische gegevens
    with st.expander("Locatie Overzicht"):
        # Kaart met marker
        st.header("Locatie op kaart")
        map_obj = folium.Map(location=[latitude, longitude], zoom_start=6)
        folium.Marker([latitude, longitude], tooltip=location_name, icon=folium.Icon(color="red")).add_to(map_obj)
        st_folium(map_obj, width=700, height=400)

    # Functie om weerdata op te halen
    def fetch_weather_data(lat, lon, start, end):
        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={start}&end_date={end}"
            f"&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,cloudcover,precipitation,visibility"
            f"&timezone=Europe/Berlin"
        )
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Fout bij het ophalen van weergegevens: {response.status_code}")
            return None

    # Historische gegevens ophalen
    with st.expander("Historische Weergegevens"):
        historical_data = fetch_weather_data(latitude, longitude, start_date, end_date)
        if historical_data:
            hourly = historical_data['hourly']
            times = [datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M") for i in range(len(hourly['time']))]
            temperatures = hourly['temperature_2m']
            wind_speeds = [kmh_to_beaufort(speed) for speed in hourly['wind_speed_10m']]
            wind_directions = [degrees_to_direction(deg) if deg is not None else '' for deg in hourly['wind_direction_10m']]
            cloudcover = hourly.get('cloudcover', [])
            precipitation = hourly.get('precipitation', [])
            visibility = hourly.get('visibility', [])

            # Seaborn plots
            sns.set(style="whitegrid")
            
            # Temperatuur en Windsnelheid Plot
            fig, ax1 = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=times, y=temperatures, color="blue", ax=ax1, label="Temperatuur (°C)")
            sns.lineplot(x=times, y=wind_speeds, color="green", ax=ax1, label="Windsnelheid (Beaufort)")
            ax1.set_xlabel("Datum en Tijd")
            ax1.set_ylabel("Temperatuur / Windsnelheid")
            ax1.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

            # Bewolking en Zichtbaarheid Plot
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=times, y=cloudcover, color="gray", ax=ax2, label="Bewolkingsgraad (%)")
            sns.lineplot(x=times, y=visibility, color="purple", ax=ax2, label="Zichtbaarheid (km)")
            ax2.set_xlabel("Datum en Tijd")
            ax2.set_ylabel("Bewolkingsgraad / Zichtbaarheid")
            ax2.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

            # Neerslag Plot
            fig3, ax3 = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=times, y=precipitation, color="blue", ax=ax3, label="Neerslag (mm)")
            ax3.set_xlabel("Datum en Tijd")
            ax3.set_ylabel("Neerslag")
            ax3.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

            # Grafieken weergeven in Streamlit
            st.pyplot(fig)
            st.pyplot(fig2)
            st.pyplot(fig3)

    # Voorspelde gegevens ophalen en weergeven
    with st.expander("Voorspelde Weergegevens"):
        forecast_start_date = start_date_input
        forecast_end_date = start_date_input + timedelta(days=8)
        forecast_data = fetch_weather_data(latitude, longitude, forecast_start_date, forecast_end_date)
        if forecast_data:
            # Voorbeeld van hoe voorspelde gegevens kunnen worden weergegeven; kan verder worden aangepast
            st.write("Voorspelde weergegevens nog toe te voegen.")
else:
    st.error("Locatie niet gevonden. Controleer de ingevoerde locatie en probeer opnieuw.")
