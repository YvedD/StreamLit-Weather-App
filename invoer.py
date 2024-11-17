# invoer.py
import streamlit as st
from datetime import datetime, timedelta
import requests
from timezonefinder import TimezoneFinder
import pytz

# Lijst van Europese landen in Engels en Nederlands
EUROPEAN_COUNTRIES_EN = [
    "Belgium", "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Bulgaria", "Bosnia and Herzegovina", 
    "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "Georgia", "Germany", 
    "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein", 
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", 
    "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", 
    "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"
]

EUROPEAN_COUNTRIES_NL = [
    "België", "Albanië", "Andorra", "Armenië", "Oostenrijk", "Azerbeidzjan", "Bulgarije", "Bosnië en Herzegovina", 
    "Kroatië", "Cyprus", "Tsjechië", "Denemarken", "Estland", "Finland", "Georgië", "Duitsland", 
    "Griekenland", "Hongarije", "IJsland", "Ierland", "Italië", "Kazachstan", "Kosovo", "Letland", "Liechtenstein", 
    "Litouwen", "Luxemburg", "Malta", "Moldavië", "Monaco", "Montenegro", "Nederland", "Noord-Macedonië", 
    "Noorwegen", "Polen", "Portugal", "Roemenië", "Rusland", "San Marino", "Servië", "Slovenië", "Slovenië", 
    "Spanje", "Zweden", "Zwitserland", "Turkije", "Oekraïne", "Verenigd Koninkrijk", "Vaticaanstad"
]

# Functie om GPS-coördinaten op te halen via geocoding service
def get_gps_coordinates(location):
    api_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1&limit=1"
    try:
        response = requests.get(api_url)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error("Location not found.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Error fetching GPS coordinates: {e}")
        return None, None

def show_input_form():
    # Standaardwaarden voor locatie en datum
    default_location = "Bredene"
    selected_date = datetime.now().date() - timedelta(days=1)

    # Taalkeuze en landselectie
    lang_choice = st.radio("Select Language", ["English", "Nederlands"], index=0)
    if lang_choice == "English":
        countries = EUROPEAN_COUNTRIES_EN
        country_label = "Select Country"
        location_label = "Location for weather"
    else:
        countries = EUROPEAN_COUNTRIES_NL
        country_label = "Selecteer land"
        location_label = "Locatie voor weergegevens"

    country = st.selectbox(country_label, countries)
    location = st.text_input(location_label, value=default_location)
    selected_date = st.date_input("Date", value=selected_date)

    latitude, longitude = get_gps_coordinates(location)
    
    if latitude and longitude:
        # Sla de locatie op in de session state
        st.session_state.latitude = latitude
        st.session_state.longitude = longitude
        st.session_state.location = location
        return latitude, longitude, location
    else:
        return None, None, None
