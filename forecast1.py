import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

def show_forecast1_expander():
    # Bepaal de datum van "vandaag + 1 dag"
    forecast_date = datetime.now() + timedelta(days=1)
    formatted_date = forecast_date.strftime("%Y/%m/%d")

    # Dropdownlijst voor het kiezen van een land
    country_options = {
        "België": [50.8503, 4.3517],
        "Nederland": [52.3676, 4.9041],
        "Duitsland": [51.1657, 10.4515],
        "Frankrijk": [46.6034, 1.8883],
        "Spanje": [40.4637, -3.7492],
        "Italië": [41.8719, 12.5674],
        "Verenigd Koninkrijk": [55.3781, -3.4360],
        "Polen": [51.9194, 19.1451],
        "Zweden": [60.1282, 18.6435],
        "Denemarken": [56.2639, 9.5018]
        # Voeg meer landen toe als dat nodig is
    }

    # Voeg een dropdownlijst toe zodat de gebruiker een land kan kiezen
    country = st.selectbox("Kies een land:", list(country_options.keys()), index=0)

    # Expander voor de temperatuurkaart
    with st.expander(f"Temperatuurkaart voor {country} - {formatted_date}", expanded=True):
        # Kies de coördinaten voor het geselecteerde land
        coords = country_options.get(country, [50.8503, 4.3517])  # Standaard naar België als het land niet gevonden wordt

        # Maak de Folium-kaart aan
        m = folium.Map(location=coords, zoom_start=6)

        # Voeg een lichte basiskaart toe voor beter contrast
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='© OpenStreetMap contributors',
            name='Lichte basiskaart',
            control=False
        ).add_to(m)

        # Voeg de OpenWeatherMap temperatuurlaag toe met verhoogde opaciteit
        tile_url = "https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=54fb4ec132c9baed8b35a4bac2b9f9e1"
        folium.TileLayer(
            tiles=tile_url,
            attr='Map data © OpenWeatherMap',
            name="Temperatuurkaart",
            overlay=True,
            control=True,
            opacity=0.9  # Verhoogde opaciteit voor helderdere kleuren
        ).add_to(m)

        # Weergeef de kaart binnen Streamlit met st_folium
        st_folium(m, width=700, height=500)
