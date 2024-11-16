import streamlit as st
from datetime import datetime, timedelta
import requests

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
            st.error("Location not found.")  # Error in English
            return None, None
    except requests.RequestException as e:
        st.error(f"Error fetching GPS coordinates: {e}")  # Error message in English
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
            st.error("Sunrise and sunset times not found.")  # Error message in English
            return None, None
    except requests.RequestException as e:
        st.error(f"Error fetching sunrise/sunset times: {e}")  # Error message in English
        return None, None

# De invoerfunctie die de gegevens toont en de invoer mogelijk maakt
def show_input_form():
    # Standaardwaarden voor locatie en datum
    default_country_en = "Belgium"  # Engels
    default_country_nl = "België"  # Nederlands
    default_location = "Bredene"
    latitude = 51.2389
    longitude = 2.9724
    selected_date = datetime.now().date() - timedelta(days=1)

    # Voeg enkel de titel toe boven de expander
    st.markdown(
        '<h1 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px;">Migration Weather Data</h1>',
        unsafe_allow_html=True
    )

    # Laat de gebruiker de taal kiezen
    language = st.selectbox("Select Language/Kies uw taal", ["English", "Dutch"])

    # Kies de landenlijst en de standaardwaarde op basis van de taal
    if language == "English":
        countries = EUROPEAN_COUNTRIES_EN
        country_label = "Select Country"
        country_text = "Country"
        location_label = "Location for weather"
        location_text = "Location"
        date_label = "Date"
        start_hour_label = "Start Hour"
        end_hour_label = "End Hour"
        sunrise_label = "Sunrise"
        sunset_label = "Sunset"
        default_country = default_country_en
    else:
        countries = EUROPEAN_COUNTRIES_NL
        country_label = "Selecteer land"
        country_text = "Land"
        location_label = "Locatie voor weergegevens"
        location_text = "Locatie"
        date_label = "Datum"
        start_hour_label = "Beginuur"
        end_hour_label = "Einduur"
        sunrise_label = "Zonsopkomst"
        sunset_label = "Zonsondergang"
        default_country = default_country_nl

    # Expander die altijd uitgeklapt is
    with st.expander("Input Data", expanded=True):  # Dit maakt de expander standaard uitgeklapt

        # Titel voor de invoer
        st.header(f"{location_label} ")

        # Formulier voor het invoeren van gegevens
        country = st.selectbox(country_label, countries, index=countries.index(default_country))  # Lijst van Europese landen
        location = st.text_input(location_label, value=default_location)
        selected_date = st.date_input(date_label, value=selected_date)
        start_hour = st.selectbox(start_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=8)
        end_hour = st.selectbox(end_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=16)

        # Verkrijg de GPS-coördinaten voor de nieuwe locatie
        latitude, longitude = get_gps_coordinates(location)

        # Haal zonsopkomst en zonsondergang tijden op
        if latitude and longitude:
            sunrise, sunset = get_sun_times(latitude, longitude, selected_date)
        else:
            sunrise = sunset = None

        # Toon Land, Locatie, Latitude en Longitude, en Zonsopkomst/Zonsondergang
        if latitude and longitude:
            st.write(f"**{country_text}**: {country}, **{location_text}**: {location}, **GPS** :{latitude:.2f}°N {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**{sunrise_label}**: {sunrise}, **{sunset_label}**: {sunset}")
        else:
            st.write(f"{location_label} not found.")  # Foutmelding in de gekozen taal
