import streamlit as st
from invoer import show_input_form
from maps import show_map_expander
from data import show_data_expander  # Importeer de data-expander
from forecast1 import show_forecast1_expander

def main():
    # Verkrijg invoer van de gebruiker
    latitude, longitude, location = show_input_form()

    # Toon de kaart op basis van de invoer
    if latitude and longitude:
        # Eerst de kaart-expander tonen zonder argumenten, want de waarden worden uit session_state gehaald
        show_map_expander()  # Toon de kaart met de juiste locatie
    else:
        st.error("Invalid location coordinates.")  # Foutmelding als de locatie niet geldig is

    # Altijd de data-expander tonen (zelfstandig van de locatie)
    show_data_expander()  # Toon de data-expander voor de opgegeven locatie

    #toon een weerkaart (test)!
    show_forecast1_expander()
    
if __name__ == "__main__":
    main()
