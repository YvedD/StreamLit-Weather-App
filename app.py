import streamlit as st
from invoer import show_input_form
from maps import show_map_expander
from data import fetch_weather_data, show_weather_expander  # Importeer de functie voor de expander

def main():
    # Verkrijg invoer van de gebruiker
    latitude, longitude, location = show_input_form()

    # Toon de data-expander na de kaart
    show_data_expander(latitude, longitude, location)  # Toon de data-expander voor de opgegeven locatie

    # Toon de kaart op basis van de invoer
    if latitude and longitude:
        show_map_expander(latitude, longitude, location)  # Toon de kaart met de juiste locatie

    else:
        st.error("Invalid location coordinates.")

if __name__ == "__main__":
    main()
