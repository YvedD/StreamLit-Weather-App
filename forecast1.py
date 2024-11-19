import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import numpy as np

def get_mock_temperature_data():
    # Genereer enkele locaties in België en stel temperaturen in
    locations = [
        {"name": "Brussel", "coords": [50.8503, 4.3517], "temp": 12},
        {"name": "Antwerpen", "coords": [51.2194, 4.4025], "temp": 11},
        {"name": "Gent", "coords": [51.0543, 3.7174], "temp": 10},
        {"name": "Luik", "coords": [50.6326, 5.5797], "temp": 9},
        {"name": "Charleroi", "coords": [50.4114, 4.4445], "temp": 10},
    ]
    return locations

def show_forecast1_expander():
    # Bepaal de datum van "vandaag + 1 dag"
    forecast_date = datetime.now() + timedelta(days=1)
    formatted_date = forecast_date.strftime("%Y/%m/%d")

    # Haal het land op uit de session state (controleer of het bestaat)
    country = st.session_state.get("country", "België")  # Standaard België

    # Expander voor de temperatuurkaart
    with st.expander(f"Temperatuurkaart voor {country} - {formatted_date}", expanded=True):
        st.write(f"Hieronder zie je de temperatuurkaart voor {country} op {formatted_date}.")

        # Centraal coördinaat voor België of een alternatief land als je die nodig hebt
        coords = [50.8503, 4.3517]

        # Maak de Folium-kaart aan
        m = folium.Map(location=coords, zoom_start=7)

        # Voeg een lichte basiskaart toe voor beter contrast
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='© OpenStreetMap contributors',
            name='Lichte basiskaart',
            control=False
        ).add_to(m)

        # Voeg de OpenWeatherMap temperatuurlaag toe
        tile_url = "https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=54fb4ec132c9baed8b35a4bac2b9f9e1"
        folium.TileLayer(
            tiles=tile_url,
            attr='Map data © OpenWeatherMap',
            name="Temperatuurkaart",
            overlay=True,
            control=True,
            opacity=0.6  # Houd opaciteit iets lager zodat cirkels duidelijker zijn
        ).add_to(m)

        # Voeg cirkels met temperatuur aan de kaart toe
        temperature_data = get_mock_temperature_data()
        for data in temperature_data:
            lat, lon = data["coords"]
            temp = data["temp"]

            # Voeg een cirkel toe met temperatuurwaarde als popup en tooltip
            folium.CircleMarker(
                location=[lat, lon],
                radius=12,  # Vergroot cirkelgrootte voor zichtbaarheid
                color='blue',  # Randen van de cirkel
                fill=True,
                fill_color='red' if temp >= 10 else 'blue',  # Kies kleur afhankelijk van temperatuur
                fill_opacity=0.7,
                popup=f"{data['name']}: {temp}°C",
                tooltip=f"{temp}°C"
            ).add_to(m)

        # Weergeef de kaart binnen Streamlit met st_folium
        st_folium(m, width=700, height=500)
