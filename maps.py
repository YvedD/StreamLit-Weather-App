# maps.py
import streamlit as st
import folium
from streamlit_folium import st_folium

# Functie om een kaart te tonen met een marker op de specifieke locatie
def show_map_expander(latitude, longitude, location):
    # Centrer de kaart op de opgegeven locatie
    map_center = [latitude, longitude]
    map_object = folium.Map(location=map_center, zoom_start=12)

    # Voeg een marker toe voor de locatie
    folium.Marker(
        location=map_center,
        popup=location,  # Toon de locatie bij het klikken op de marker
        tooltip=location  # Toon locatie bij hover
    ).add_to(map_object)

    # Toon de kaart in een expander die standaard geopend is
    with st.expander("Kaart van locatie", expanded=True):
        st_folium(map_object, width=700, height=500)
