import streamlit as st
from invoer import show_input_form
from maps import show_map_expander
from data import show_data_expander  # Importeer de data-expander

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
    # Geneste expander voor sessiegegevens
    # Haal benodigde sessiegegevens op
    lat = st.session_state.get("latitude")
    lon = st.session_state.get("longitude")
    location = st.session_state.get("location")
    date = st.session_state.get("selected_date")
    start_hour = st.session_state.get("start_hour", "08:00")
    end_hour = st.session_state.get("end_hour", "16:00")

    with st.expander("Sessiedata: Locatie en Tijd"):
        st.write(f"**Locatie**: {location}")
        st.write(f"**Latitude**: {lat}")
        st.write(f"**Longitude**: {lon}")
        st.write(f"**Geselecteerde Datum**: {date.strftime('%d-%m-%Y')}")
        st.write(f"**Zonsopgang**: {sunrise}")
        st.write(f"**Zonsondergang**: {sunset}")
        st.write(f"**Startuur**: {start_hour}")
        st.write(f"**Einduur**: {end_hour}")

if __name__ == "__main__":
    main()
