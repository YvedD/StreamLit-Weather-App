import streamlit as st
import folium
from streamlit_folium import st_folium

# Toon een kaart in een expander
def show_map_expander():
    # Haal de locatiegegevens uit de session_state
    latitude = st.session_state.get("latitude", 51.2389)  # Gebruik standaard als geen waarde is
    longitude = st.session_state.get("longitude", 2.9724)
    location = st.session_state.get("location", "Unknown")

    # Toon een kaart in een expander
    with st.expander("**Map/Kaart**", expanded=True):
        # Creëer de folium kaart
        m = folium.Map(location=[latitude, longitude], zoom_start=10)

        # Voeg een marker toe voor de locatie
        folium.Marker([latitude, longitude], popup=location).add_to(m)

        # Render de kaart in Streamlit
        st_folium(m, width=700, height=500)
