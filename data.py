# data.py
import streamlit as st
import requests

def show_data_expander():
    # Haal de gegevens op uit session_state
    country = st.session_state.get("country", "België")
    location = st.session_state.get("location", "Bredene")
    latitude = st.session_state.get("latitude", 51.2389)
    longitude = st.session_state.get("longitude", 2.9724)
    selected_date = st.session_state.get("selected_date", None)
    start_hour = st.session_state.get("start_hour", "00:00")
    end_hour = st.session_state.get("end_hour", "23:00")

    # Toon de data expander
    with st.expander("Data", expanded=True):
        st.write(f"Showing data for {location} in {country} at coordinates ({latitude}, {longitude})")
        st.write(f"Date: {selected_date}, Start Hour: {start_hour}, End Hour: {end_hour}")

        # Hier kun je de Open-Meteo API aanroepen met de opgehaalde gegevens
        # Voorbeeld API-aanroep:
        if latitude and longitude and selected_date:
            api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start={selected_date}T{start_hour}&end={selected_date}T{end_hour}&timezone=auto"
            response = requests.get(api_url)
            data = response.json()

            # Toon voorbeeldweerdata (pas dit aan zoals gewenst)
            st.write("Weather Data:", data)
