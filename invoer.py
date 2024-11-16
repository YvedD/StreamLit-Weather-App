import streamlit as st
from datetime import datetime, timedelta
import requests

# Lijst van Europese landen voor de dropdown
EUROPEAN_COUNTRIES = [
    "Belgium", "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Bulgaria", "Bosnia and Herzegovina", 
    "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "Georgia", "Germany", 
    "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein", 
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", 
    "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", 
    "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"
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
            st.error("Locatie niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van GPS-coördinaten: {e}")
        return None, None

# Functie om zonsopkomst en zonsondergang te berekenen
def get_sun_times(lat, lon, date):
    api_url = (
        f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if 'results' in data:
            sunrise = datetime.fromisoformat(data['results']['sunrise']).strftime('%H:%M')
            sunset = datetime.fromisoformat(data['results']['sunset']).strftime('%H:%M')
            return sunrise, sunset
        else:
            st.error("Zonsopkomst- en zonsondergangstijden niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van zonsopkomst/zonsondergang: {e}")
        return None, None

# De invoerfunctie die de gegevens toont en de invoer mogelijk maakt
def show_input_form():
    # Standaardwaarden voor locatie en datum
    default_country = "Belgium"
    default_location = "Bredene"
    latitude = 51.2389
    longitude = 2.9724
    selected_date = datetime.now().date() - timedelta(days=1)

    # Voeg enkel de titel toe boven de expander
    st.markdown(
        '<h1 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px;">Migration Weather Data</h1>',
        unsafe_allow_html=True
    )

    # Expander die altijd uitgeklapt is
    with st.expander("Invoer Gegevens", expanded=True):  # Dit maakt de expander standaard uitgeklapt

        # Titel voor de invoer
        st.header("Invoergegevens voor het weer")

        # Formulier voor het invoeren van gegevens
        country = st.selectbox("Selecteer land", EUROPEAN_COUNTRIES, index=EUROPEAN_COUNTRIES.index(default_country))  # Lijst van Europese landen
        location = st.text_input("Locatie", value=default_location)
        selected_date = st.date_input("Datum", value=selected_date)
        start_hour = st.selectbox("Beginuur", [f"{hour:02d}:00" for hour in range(24)], index=8)
        end_hour = st.selectbox("Einduur", [f"{hour:02d}:00" for hour in range(24)], index=16)

        # Verkrijg de GPS-coördinaten voor de nieuwe locatie
        latitude, longitude = get_gps_coordinates(location)

        # Haal zonsopkomst en zonsondergang tijden op
        if latitude and longitude:
            sunrise, sunset = get_sun_times(latitude, longitude, selected_date)
        else:
            sunrise = sunset = None

        # Toon Land, Locatie, Latitude en Longitude, en Zonsopkomst/Zonsondergang
        if latitude and longitude:
            st.write(f"**Land**: {country}, **Locatie**: {location}, **GPS** :{latitude:.2f}°N {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**Zonsopkomst**: {sunrise}, **Zonsondergang**: {sunset}")
        else:
            st.write("Locatie niet gevonden.")
