import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

def show_forecast1_expander():
    forecast_date = datetime.now() + timedelta(days=1)
    formatted_date = forecast_date.strftime("%Y/%m/%d")

    country = st.session_state.get("country", "België")
    with st.expander(f"Temperatuurkaart voor {country} - {formatted_date}", expanded=True):
        st.write(f"Hieronder zie je de temperatuurkaart voor {country} op {formatted_date}.")

        country_coords = {
            "België": [50.8503, 4.3517],
            "Nederland": [52.3676, 4.9041],
            "Duitsland": [51.1657, 10.4515]
        }
        coords = country_coords.get(country, [50.8503, 4.3517])

        m = folium.Map(location=coords, zoom_start=6)

        # Donkere basislaag
        folium.TileLayer(
            tiles='https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png',
            attr='© CartoDB',
            name='Donkere basiskaart',
            control=True
        ).add_to(m)

        # OpenWeatherMap temperatuurlaag met hogere opaciteit
        tile_url = "https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=54fb4ec132c9baed8b35a4bac2b9f9e1"
        folium.TileLayer(
            tiles=tile_url,
            attr='Map data © OpenWeatherMap',
            name="Temperatuurkaart",
            overlay=True,
            control=True,
            opacity=0.8  # Verhoogde opaciteit
        ).add_to(m)

        # CSS-styling voor fellere kleuren (optioneel)
        st.markdown(
            """
            <style>
            [id^=folium-map] {
                filter: contrast(1.5) brightness(1.2);
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st_folium(m, width=700, height=500)
