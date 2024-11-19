import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import os

# Haal de API-sleutel op uit de omgevingsvariabelen
api_key = os.getenv("API_KEY_OPENWEATHERMAPS")

# Controleer of de API-sleutel is opgehaald
if api_key:
    st.write("API Key is geladen !")  # Dit is optioneel om te testen
else:
    st.write("API Key is niet gevonden!")  # Dit helpt bij troubleshooting
    
def show_forecast1_expander():
    # Bepaal de datum van "vandaag + 1 dag"
    forecast_date = datetime.now() + timedelta(days=1)
    formatted_date = forecast_date.strftime("%Y/%m/%d")
    
    # Expander voor het kiezen van een land en het tonen van de temperatuurkaart
    with st.expander(f"**Temp. Map/Kaart: {formatted_date}**", expanded=True):

        # Dropdownlijst voor het kiezen van een land
        country_options = {
            "België": [50.8503, 4.3517],
            "Albanië": [41.1533, 20.1683],
            "Andorra": [42.5078, 1.5211],
            "Armenië": [40.0691, 45.0382],
            "Oostenrijk": [47.5162, 14.5501],
            "Azerbeidzjan": [40.1431, 47.5769],
            "Bulgarije": [42.7339, 25.4858],
            "Bosnië en Herzegovina": [43.8486, 18.3564],
            "Kroatië": [45.1, 15.2],
            "Cyprus": [35.1264, 33.4299],
            "Tsjechië": [49.8175, 15.4730],
            "Denemarken": [56.2639, 9.5018],
            "Estland": [58.5953, 25.0136],
            "Finland": [61.9241, 25.7482],
            "Georgië": [42.3154, 43.3569],
            "Duitsland": [51.1657, 10.4515],
            "Griekenland": [39.0742, 21.8243],
            "Hongarije": [47.1625, 19.5033],
            "IJsland": [64.9631, -19.0208],
            "Ierland": [53.4129, -8.2439],
            "Italië": [41.8719, 12.5674],
            "Kazachstan": [48.0196, 66.9237],
            "Kosovo": [42.6026, 20.9020],
            "Letland": [56.8796, 24.6032],
            "Liechtenstein": [47.1415, 9.5215],
            "Litouwen": [55.1694, 23.8813],
            "Luxemburg": [49.6117, 6.13],
            "Malta": [35.9375, 14.3754],
            "Moldavië": [47.4116, 28.3699],
            "Monaco": [43.7333, 7.4167],
            "Montenegro": [42.7087, 19.3744],
            "Nederland": [52.3676, 4.9041],
            "Noord-Macedonië": [41.6086, 21.7453],
            "Noorwegen": [60.4720, 8.4689],
            "Polen": [51.9194, 19.1451],
            "Portugal": [39.3999, -8.2245],
            "Roemenië": [45.9432, 24.9668],
            "Rusland": [55.7558, 37.6173],
            "San Marino": [43.9333, 12.45],
            "Servië": [44.0165, 21.0059],
            "Slovenië": [46.1511, 14.9955],
            "Spanje": [40.4637, -3.7492],
            "Zweden": [60.1282, 18.6435],
            "Zwitserland": [46.8182, 8.2275],
            "Turkije": [38.9637, 35.2433],
            "Oekraïne": [48.3794, 31.1656],
            "Verenigd Koninkrijk": [55.3781, -3.4360],
            "Vaticaanstad": [41.9029, 12.4534]
        }

        # Dropdownlijst voor het kiezen van een land
        country = st.selectbox("**Select country/Kies een land:**", list(country_options.keys()), index=0)

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
        tile_url = f"https://tile.openweathermap.org/map/cloud_new/{{z}}/{{x}}/{{y}}.png?appid=54fb4ec132c9baed8b35a4bac2b9f9e1"
        folium.TileLayer(
            tiles=tile_url,
            attr='Map data © OpenWeatherMap',
            name="Temperatuurkaart",
            overlay=True,
            control=True,
            opacity=3.0  # Verhoogde opaciteit voor helderdere kleuren
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
            </div>
            <div style="display: flex; width: 100%;">
                <div style="width: 100%; height: 10px; background: linear-gradient(to right, 
                    rgba(130, 22, 146, 1),
                    rgba(130, 87, 219, 1),
                    rgba(32, 140, 236, 1),
                    rgba(32, 196, 232, 1),
                    rgba(35, 221, 221, 1),
                    rgba(194, 255, 40, 1),
                    rgba(255, 240, 40, 1),
                    rgba(255, 194, 40, 1),
                    rgba(252, 128, 20, 1)
                ); border-radius: 10px; position: relative;">
                </div>
            </div>
        </div>
        """
        st.markdown(legend_html, unsafe_allow_html=True)
