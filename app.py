# app.py
import streamlit as st
from invoer import gebruikers_invoer  # Importeren van de invoerfunctie

# Oproep van gebruikersinvoer uit invoer.py
land, locatie, datum, begin_uur, eind_uur, latitude, longitude, sunrise, sunset = gebruikers_invoer()

# Toon de samenvatting van de invoer
st.write(f"**Geselecteerd land:** {land}")
st.write(f"**Locatie:** {locatie}")
st.write(f"**Coördinaten:** {latitude:.4f}, {longitude:.4f}")
st.write(f"**Zonsopkomst:** {sunrise}")
st.write(f"**Zonsondergang:** {sunset}")
