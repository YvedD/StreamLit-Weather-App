# invoer.py
import streamlit as st
from datetime import datetime, timedelta
import requests
from timezonefinder import TimezoneFinder
import pytz

# Lijst van Europese landen in Engels en Nederlands
EUROPEAN_COUNTRIES_EN = ["Belgium", "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Bulgaria",
                         "Bosnia and Herzegovina", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                         "Finland", "Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy",
                         "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta",
                         "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Poland",
                         "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain",
                         "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"]

EUROPEAN_COUNTRIES_NL = ["België", "Albanië", "Andorra", "Armenië", "Oostenrijk", "Azerbeidzjan", "Bulgarije",
                         "Bosnië en Herzegovina", "Kroatië", "Cyprus", "Tsjechië", "Denemarken", "Estland", "Finland",
                         "Georgië", "Duitsland", "Griekenland", "Hongarije", "IJsland", "Ierland", "Italië",
                         "Kazachstan", "Kosovo", "Letland", "Liechtenstein", "Litouwen", "Luxemburg", "Malta",
                         "Moldavië", "Monaco", "Montenegro", "Nederland", "Noord-Macedonië", "Noorwegen", "Polen",
                         "Portugal", "Roemenië", "Rusland", "San Marino", "Servië", "Slovenië", "Spanje", "Zweden",
                         "Zwitserland", "Turkije", "Oekraïne", "Verenigd Koninkrijk", "Vaticaanstad"]

# Functie om GPS-coördinaten op te halen via een externe API
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

# Functie om zonsopkomst en zonsondergang op te halen, rekening houdend met de tijdzone
def get_sun_times(lat, lon, date):
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)
    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if 'results' in data:
            sunrise_utc = datetime.fromisoformat(data['results']['sunrise'])
            sunset_utc = datetime.fromisoformat(data['results']['sunset'])
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

# De invoerfunctie om de locatie, datum en tijdsperiode op te geven
def show_input_form():
    default_country_en = "Belgium"
    default_country_nl = "België"
    default_location = "Bredene"
    latitude = 51.2389
    longitude = 2.9724
    selected_date = datetime.now().date() - timedelta(days=1)

    # Titel van de applicatie
    st.markdown('<h3 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px; text-align: center;">Migration Historic Weather Data<br>and 3 day Forecast</h3>', unsafe_allow_html=True)
    
    with st.expander("Input Data", expanded=True):
        # Taalkeuze binnen de expander
        lang_choice = st.radio("Select Language/Kies uw taal",
                               options=["English", "Nederlands"],
                               index=0 if st.session_state.get("language", "English") == "English" else 1,
                               key="language_selector", horizontal=True)
        st.session_state["language"] = lang_choice

        # Landenlijst en labels op basis van de taalkeuze
        if lang_choice == "English":
            countries = EUROPEAN_COUNTRIES_EN
            country_label, location_label, date_label = "Select Country", "Location for weather", "Date"
            start_hour_label, end_hour_label, sunrise_label, sunset_label = "Start Hour", "End Hour", "Sunrise", "Sunset"
            default_country = default_country_en
        else:
            countries = EUROPEAN_COUNTRIES_NL
            country_label, location_label, date_label = "Selecteer land", "Locatie voor weergegevens", "Datum"
            start_hour_label, end_hour_label, sunrise_label, sunset_label = "Beginuur", "Einduur", "Zonsopkomst", "Zonsondergang"
            default_country = default_country_nl

        # Invoer van gegevens
        country = st.selectbox(country_label, countries, index=countries.index(default_country))
        location = st.text_input(location_label, value=default_location)
        selected_date = st.date_input(date_label, value=selected_date)
        start_hour = st.selectbox(start_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=8)
        end_hour = st.selectbox(end_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=16)

        # Haal GPS-coördinaten en zonsopkomst/zonsopgang op
        latitude, longitude = get_gps_coordinates(location)
        if latitude and longitude:
            sunrise, sunset = get_sun_times(latitude, longitude, selected_date)
            st.write(f"**{country_label}**: {country}, **{location_label}**: {location}, **GPS**: {latitude:.2f}°N {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**{sunrise_label}**: {sunrise}, **{sunset_label}**: {sunset}")
        else:
            st.write(f"{location_label} not found.")
