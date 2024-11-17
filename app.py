# app.py
import streamlit as st
from invoer import show_input_form
from maps import show_map_expander
from data import show_data_expander  # Dit is de nieuwe sectie voor data

def main():
    # Titel van de app
    st.markdown(
        '<h1 style="font-size: 36px; font-weight: bold; color: #4CAF50; text-align: center;">Migration Historic Weather Data and 3-day Forecast</h1>',
        unsafe_allow_html=True
    )
    
    # Toon het invoerscherm voor locatie en andere gegevens
    latitude, longitude, location = show_input_form()

    # Toon de kaart met de gekozen locatie
    if latitude and longitude:
        show_map_expander(latitude, longitude, location)
    else:
        st.warning("Geen geldige locatie geselecteerd!")

    # Toon de data expander (verplaatsbare sectie)
    show_data_expander(latitude, longitude, location)

if __name__ == "__main__":
    main()
