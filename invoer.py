# invoer.py
import streamlit as st
from datetime import datetime, timedelta
import requests
from timezonefinder import TimezoneFinder
import pytz

# Lijsten met Europese landen
EUROPEAN_COUNTRIES_EN = ["Belgium", "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", ...]  # Engelse lijst
EUROPEAN_COUNTRIES_NL = ["België", "Albanië", "Andorra", "Armenië", "Oostenrijk", "Azerbeidzjan", ...]  # Nederlandse lijst

# Functie om GPS-coördinaten op te halen via een externe API (gebaseerd op locatie)
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
            st.error("Location not found.")  # Foutmelding
            return None, None
    except requests.RequestException as e:
        st.error(f"Error fetching GPS coordinates: {e}")
        return None, None

# Functie om zonsopkomst en zonsondergang te berekenen (inclusief tijdzoneaanpassing)
def get_sun_times(lat, lon, date):
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)

    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    try:
        response = requests.get(api_url)
        data = response.json()
        if 'results' in data:
            sunrise_utc = datetime.fromisoformat(data['results']['sunrise'])
            sunset_utc = datetime.fromisoformat(data['results']['sunset'])

            # Converteer naar lokale tijdzone
            local_tz = pytz.timezone(timezone_str)
            sunrise_local = sunrise_utc.astimezone(local_tz)
            sunset_local = sunset_utc.astimezone(local_tz)

            return sunrise_local.strftime('%H:%M'), sunset_local.strftime('%H:%M')
        else:
            st.error("Sunrise and sunset times not found.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Error fetching sunrise/sunset times: {e}")
        return None, None

# Invoervenster
def show_input_form():
    # Standaardinstellingen
    default_country_en = "Belgium"
    default_country_nl = "België"
    default_location = "Bredene"
    selected_date = datetime.now().date() - timedelta(days=1)

    # Taaloptie
    lang_choice = st.radio("Select Language/Kies uw taal", ["English", "Nederlands"], horizontal=True)
    st.session_state["language"] = lang_choice

    if lang_choice == "English":
        countries = EUROPEAN_COUNTRIES_EN
        country_label, location_label, date_label = "Select Country", "Location for weather", "Date"
        default_country = default_country_en
    else:
        countries = EUROPEAN_COUNTRIES_NL
        country_label, location_label, date_label = "Selecteer land", "Locatie voor weergegevens", "Datum"
        default_country = default_country_nl

    # Selectie en invoervelden
    country = st.selectbox(country_label, countries, index=countries.index(default_country))
    location = st.text_input(location_label, value=default_location)
    selected_date = st.date_input(date_label, value=selected_date)

    # Zoek coördinaten
    latitude, longitude = get_gps_coordinates(location)

    # Haal zonsopkomst en zonsondergang op
    if latitude and longitude:
        sunrise, sunset = get_sun_times(latitude, longitude, selected_date)
        if sunrise and sunset:
            st.write(f"Sunrise: {sunrise}, Sunset: {sunset}")
    else:
        st.write(f"{location_label} not found.")

    return country, location, latitude, longitude  # Retourneer de gegevens
