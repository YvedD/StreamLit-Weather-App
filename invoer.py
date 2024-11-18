import streamlit as st
from datetime import datetime, timedelta
import requests
from timezonefinder import TimezoneFinder
import pytz

# Lijsten van Europese landen in Engels en Nederlands
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

# Functie om GPS-coördinaten op te halen via een geocoding service
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

# Functie om zonsopkomst en zonsondergang te verkrijgen van de Open-Meteo API
def get_sun_times(lat, lon, date):
    api_url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={date}&end_date={date}"
        "&daily=sunrise,sunset&timezone=Europe%2FBerlin"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if 'daily' in data and 'sunrise' in data['daily'] and 'sunset' in data['daily']:
            sunrise = data['daily']['sunrise'][0]
            sunset = data['daily']['sunset'][0]

            # Haal de tijd in HH:MM formaat
            sunrise_local = datetime.fromisoformat(sunrise).strftime('%H:%M')
            sunset_local = datetime.fromisoformat(sunset).strftime('%H:%M')

            return sunrise_local, sunset_local
        else:
            st.error("Zonsopkomst en zonsondergang niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van zonsopkomst/zondondergang tijden: {e}")
        return None, None

# Functie voor invoerformulier
def show_input_form():
    # Standaardwaarden
    default_country_en = "Belgium"  
    default_country_nl = "België"  
    default_location = "Bredene"
    selected_date = datetime.now().date() - timedelta(days=1)

    # Titel boven de expander
    st.markdown(
        '<h3 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px; text-align: center;">'
        'Migration Historic Weather Data<br>and 3 day Forecast</h3>',
        unsafe_allow_html=True
    )

    # Expander voor de invoer
    with st.expander("Input Data", expanded=True):
        # Taalkeuze door middel van een radio knop
        lang_choice = st.radio(
            "Select Language/Kies uw taal",
            options=["English", "Nederlands"],
            index=1 if st.session_state.get("language", "English") == "English" else 1,
            key="language_selector",
            horizontal=True
        )

        # Sla de taalkeuze op in de session_state
        st.session_state["language"] = lang_choice

        # Kies de landenlijst en labels op basis van de taal
        if lang_choice == "English":
            countries = EUROPEAN_COUNTRIES_EN
            country_label = "Select Country"
            location_label = "Location for weather"
            date_label = "Date"
            start_hour_label = "Start Hour"
            end_hour_label = "End Hour"
            sunrise_label = "Sunrise"
            sunset_label = "Sunset"
            default_country = default_country_en
        else:
            countries = EUROPEAN_COUNTRIES_NL
            country_label = "Selecteer land"
            location_label = "Locatie voor weergegevens"
            date_label = "Datum"
            start_hour_label = "Beginuur"
            end_hour_label = "Einduur"
            sunrise_label = "Zonsopkomst"
            sunset_label = "Zonsondergang"
            default_country = default_country_nl

        # Formulier voor invoer
        country = st.selectbox(country_label, countries, index=countries.index(default_country))  
        location = st.text_input(location_label, value=default_location)
        selected_date = st.date_input(date_label, value=selected_date)

        # Verkrijg GPS-coördinaten voor de locatie
        latitude, longitude = get_gps_coordinates(location)

        # Haal zonsopkomst en zonsondergang op
        if latitude and longitude:
            sunrise, sunset = get_sun_times(latitude, longitude, selected_date)
            start_hour_default = sunrise if sunrise else "08:00"  # Standaardtijd als zonsopgang niet beschikbaar is
            end_hour_default = sunset if sunset else "16:00"  # Standaardtijd als zonsondergang niet beschikbaar is
        else:
            start_hour_default = "08:00"
            end_hour_default = "16:00"

        # Gebruiker kan nog steeds uren aanpassen indien gewenst
        start_hour = st.selectbox(start_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=0, key="start_hour", format_func=lambda x: start_hour_default if x == "08:00" else x)
        end_hour = st.selectbox(end_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=23, key="end_hour", format_func=lambda x: end_hour_default if x == "16:00" else x)

        # Sla alle benodigde gegevens op in de session_state
        st.session_state["country"] = country
        st.session_state["location"] = location
        st.session_state["selected_date"] = selected_date
        st.session_state["start_hour"] = start_hour
        st.session_state["end_hour"] = end_hour
        st.session_state["latitude"] = latitude
        st.session_state["longitude"] = longitude
        st.session_state["sunrise"] = sunrise
        st.session_state["sunset"] = sunset
        st.session_state["language"] = lang_choice

        # Toon locatiegegevens en zonsopkomst/zondondergang tijden
        if latitude and longitude:
            st.write(f"**Country**: {country}, **Location**: {location}, **GPS**: {latitude:.2f}°N {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**Sunrise**: {sunrise}, **Sunset**: {sunset}")
        else:
            st.write(f"{location_label} not found.")

    return latitude, longitude, location
