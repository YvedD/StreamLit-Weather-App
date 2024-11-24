import streamlit as st
import requests
from datetime import datetime, timedelta

# Standaardinstellingen
default_country = "België"
default_location = "Bredene"
latitude = 51.2389
longitude = 2.9724
selected_date = datetime.now() - timedelta(days=1)

# Sessie initialiseren met standaardinstellingen
def initialize_session_state():
    if "country" not in st.session_state:
        st.session_state["country"] = default_country
    if "location" not in st.session_state:
        st.session_state["location"] = default_location
    if "latitude" not in st.session_state:
        st.session_state["latitude"] = latitude
    if "longitude" not in st.session_state:
        st.session_state["longitude"] = longitude
    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = selected_date
    if "sun_times" not in st.session_state:
        st.session_state["sun_times"] = {}

# Functie om de zonstijden op te halen via de Sunrise-Sunset API
def get_sun_times(latitude, longitude, date):
    url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date={date.strftime('%Y-%m-%d')}&formatted=0"
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "OK":
        sun_times = {
            "sunrise": data["results"]["sunrise"],
            "sunset": data["results"]["sunset"],
            "civil_twilight_begin": data["results"]["civil_twilight_begin"],
            "civil_twilight_end": data["results"]["civil_twilight_end"],
            "nautical_twilight_begin": data["results"]["nautical_twilight_begin"],
            "nautical_twilight_end": data["results"]["nautical_twilight_end"],
        }
        return sun_times
    else:
        return None

# Haal de zonstijden op voor de standaardlocatie
def update_sun_times():
    sun_times = get_sun_times(st.session_state["latitude"], st.session_state["longitude"], st.session_state["selected_date"])
    if sun_times:
        st.session_state["sun_times"] = sun_times
    else:
        st.session_state["sun_times"] = {"error": "Kon zonstijden niet ophalen."}

# Hoofdprogramma
def main():
    # Initialiseer de sessie met standaardinstellingen
    initialize_session_state()
    
    # Haal de zonstijden op bij de start
    update_sun_times()
    
    # Toon de standaardlocatiegegevens
    st.title("Locatie en Zonsopgang/Zonsondergang")
    st.write(f"Land: {st.session_state['country']}")
    st.write(f"Locatie: {st.session_state['location']}")
    st.write(f"Latitude: {st.session_state['latitude']}")
    st.write(f"Longitude: {st.session_state['longitude']}")
    st.write(f"Datum: {st.session_state['selected_date'].strftime('%Y-%m-%d')}")
    
    # Toon de zonstijden
    if "sun_times" in st.session_state and st.session_state["sun_times"]:
        if "error" in st.session_state["sun_times"]:
            st.write(st.session_state["sun_times"]["error"])
        else:
            st.write(f"Zonsopgang: {st.session_state['sun_times']['sunrise']}")
            st.write(f"Zonsondergang: {st.session_state['sun_times']['sunset']}")
            st.write(f"Civiele zonsopgang: {st.session_state['sun_times']['civil_twilight_begin']}")
            st.write(f"Civiele zonsondergang: {st.session_state['sun_times']['civil_twilight_end']}")
            st.write(f"Nautische zonsopgang: {st.session_state['sun_times']['nautical_twilight_begin']}")
            st.write(f"Nautische zonsondergang: {st.session_state['sun_times']['nautical_twilight_end']}")
    else:
        st.write("Zonstijden zijn nog niet beschikbaar.")

if __name__ == "__main__":
    main()
