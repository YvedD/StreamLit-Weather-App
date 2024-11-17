# maps.py
import streamlit as st
import folium
from streamlit_folium import st_folium

# Functie om een dynamische kaart te tonen op basis van latitude, longitude en locatie
def show_map_expander(latitude, longitude, location_name="Unknown Location"):
    # Plaats de kaart in een expander die standaard uitgeklapt is
    with st.expander("Map", expanded=True):
        # Maak een folium kaart met de gekozen locatie als startpunt
        m = folium.Map(location=[latitude, longitude], zoom_start=8)
        
        # Voeg een marker toe met de naam van de locatie
        folium.Marker(
            [latitude, longitude],
            popup=f"<strong>{location_name}</strong>",
            tooltip=location_name
        ).add_to(m)
        
        # Render de kaart in Streamlit
        st_folium(m, width=700, height=500)
