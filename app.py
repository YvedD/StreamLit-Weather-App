# app.py
import streamlit as st
from invoer import show_input_form   # Importeer de functie voor gebruikersinvoer
from data import show_data_expander  # Importeer de functie voor data-weergave (momenteel nog in ontwikkeling)
from maps import show_map_expander   # Importeer de kaartfunctie om een kaart te renderen

# Titel van het project
st.markdown('<div class="project-title">Migration Weather Data</div>', unsafe_allow_html=True)

# Toon de invoer en ontvang land, locatie en coördinaten
country, location, latitude, longitude = show_input_form()

# Toon de data-expander, momenteel "Under Construction"
show_data_expander()

# Toon de kaart-expander als er coördinaten beschikbaar zijn
if latitude is not None and longitude is not None:
    show_map_expander(latitude, longitude, location)
