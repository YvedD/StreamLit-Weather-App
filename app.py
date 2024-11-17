import streamlit as st
from invoer import show_input_form
from maps import show_map_expander
from data import fetch_weather_data, show_weather_expander  # Importeer de functie voor de expander

def main():
    # Verkrijg invoer van de gebruiker
    latitude, longitude, location = show_input_form()
    
    # Toon de kaart op basis van de invoer
    if latitude and longitude:
        show_map_expander(latitude, longitude, location)  # Toon de kaart met de juiste locatie

        # Haal weerdata op voor de geselecteerde locatie
        weather_data = fetch_weather_data(latitude, longitude)  # Roep de functie aan uit data.py
        if weather_data:
            # Toon de weerdata in de expander
            show_weather_expander(weather_data)  # Roep de expander functie aan
        else:
            st.error("No weather data available.")
    else:
        st.error("Invalid location coordinates.")

if __name__ == "__main__":
    main()
