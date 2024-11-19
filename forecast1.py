import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

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
        country_coords = {
            "België": [50.8503, 4.3517],
            "Nederland": [52.3676, 4.9041],
            "Duitsland": [51.1657, 10.4515]
            # Voeg hier meer landen toe als dat nodig is
        }

        # Kies de coördinaten voor het gekozen land (standaard België)
        coords = country_coords.get(country, [50.8503, 4.3517])

        # Maak de Folium-kaart aan
        m = folium.Map(location=coords, zoom_start=6)

        # Voeg de OpenWeatherMap temperatuurlaag toe
        tile_url = "https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=54fb4ec132c9baed8b35a4bac2b9f9e1"
        folium.TileLayer(
            tiles=tile_url,
            attr='Map data © OpenWeatherMap',
            name="Temperatuurkaart",
            overlay=True,
            control=True,
            opacity=0.5
        ).add_to(m)

        # Weergeef de kaart binnen Streamlit met st_folium
        st_folium(m, width=700, height=500)

