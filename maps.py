import streamlit as st
import folium
from streamlit_folium import st_folium

def show_map_expander(latitude, longitude, location_name):
    # Expander voor de kaartweergave
    with st.expander("Map View", expanded=True):
        # Controleer of coördinaten aanwezig zijn
        if latitude is not None and longitude is not None:
            # Maak een Folium-kaart met de opgegeven coördinaten als middelpunt
            map_center = [latitude, longitude]
            m = folium.Map(location=map_center, zoom_start=10)

            # Voeg een marker toe voor de locatie
            folium.Marker(
                location=map_center,
                popup=location_name,
                tooltip="Location",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

            # Weergeven van de kaart met Streamlit
            st_folium(m, width=700, height=500)
        else:
            st.warning("Location coordinates are missing. Please enter a valid location in the input expander.")

