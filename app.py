import streamlit as st
from invoer import show_input_form
from maps import show_map_expander
from data import show_data_expander  # Importeer de functie voor de data-expander

def main():
    # Verkrijg invoer van de gebruiker
    latitude, longitude, location = show_input_form()
    
    # Toon de kaart op basis van de invoer
    if latitude and longitude:
        show_map_expander(latitude, longitude, location)  # Toon de kaart met de juiste locatie
        
        # Toon de data-expander na de kaart
        show_data_expander(latitude, longitude, location)  # Toon de data-expander voor de opgegeven locatie
    else:
        st.error("Invalid location coordinates.")  # Foutmelding als de locatie niet geldig is

if __name__ == "__main__":
    main()
