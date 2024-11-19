import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import os

# Haal de API-sleutel op uit de omgeving
api_key = os.getenv("API_KEY")  # Leest de API-sleutel vanuit de omgeving

def show_forecast1_expander():
    # Bepaal de datum van "vandaag + 1 dag"
    forecast_date = datetime.now() + timedelta(days=1)
    formatted_date = forecast_date.strftime("%Y/%m/%d")

    # Expander voor het kiezen van een land en het tonen van de temperatuurkaart
    with st.expander(f"**Temp. Map/Kaart : {formatted_date}**", expanded=True):

        # Lijst van landen met zowel de Nederlandse naam als de Engelse naam
        country_options = {
            "België/Belgium": [50.8503, 4.3517],
            "Albanië/Albania": [41.1533, 20.1683],
            "Andorra/Andorra": [42.5078, 1.5211],
            # Voeg andere landen toe hier
        }

        # Dropdownlijst voor het kiezen van een land
        country = st.selectbox("**Select country/Kies een land:**", list(country_options.keys()), index=0)

        # Haal de coördinaten op voor het geselecteerde land
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
        tile_url = f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}"
        folium.TileLayer(
            tiles=tile_url,
            attr='Map data © OpenWeatherMap',
            name="Temperatuurkaart",
            overlay=True,
            control=True,
            opacity=0.7  # Verlaag de opaciteit naar een geldige waarde
        ).add_to(m)

        # Weergeef de kaart binnen Streamlit met st_folium
        st_folium(m, width=700, height=500)


        legend_html = """
        <div style="width: 100%; margin-top: 20px;">
            <div style="display: flex; justify-content: space-between; width: 100%; font-size: 14px; color: #000000; margin-bottom: 5px;">
                <span>-40°C</span>
                <span>-30°C</span>
                <span>-20°C</span>
                <span>-10°C</span>
                <span>0°C</span>
                <span>+10°C</span>
                <span>+20°C</span>
                <span>+30°C</span>
                <span>+40°C</span>
            </div>
            <div style="display: flex; width: 100%;">
                <div style="width: 50%; height: 10px; background: linear-gradient(to right, 
                    rgb(212, 185, 215),
                    rgb(194, 226, 222)
                ); border-radius: 10px; position: relative;">
                </div>
                <div style="width: 50%; height: 10px; background: linear-gradient(to right, 
                    rgb(207, 244, 188),
                    rgb(245, 209, 176)
                ); border-radius: 10px; position: relative;">
                </div>
            </div>
        </div>
        """
        
        st.markdown(legend_html, unsafe_allow_html=True)
