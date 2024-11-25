# invoer.py - aangepaste versie zonder expander
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

@st.cache_data
def get_gps_coordinates(location):
    api_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1&limit=1"
    headers = {'User-Agent': 'StreamLit-Weather-app/1.0 (ydsdsy@gmail.com)'}
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error(f"Locatie '{location}' niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van GPS-coördinaten: {e}")
        return None, None

@st.cache_data
def get_sun_times(lat, lon, date):
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)
    if not timezone_str:
        st.error("Tijdzone niet gevonden voor deze locatie.")
        return None, None, None, None, None, None

    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    try:
        response = requests.get(api_url)
        data = response.json()
        if 'results' in data:
            results = data['results']
            local_tz = pytz.timezone(timezone_str)

            # Zet de tijden om naar lokale tijd
            sunrise_local = datetime.fromisoformat(results['sunrise']).astimezone(local_tz)
            sunset_local = datetime.fromisoformat(results['sunset']).astimezone(local_tz)
            civil_twilight_begin_local = datetime.fromisoformat(results['civil_twilight_begin']).astimezone(local_tz)
            civil_twilight_end_local = datetime.fromisoformat(results['civil_twilight_end']).astimezone(local_tz)
            nautical_twilight_begin_local = datetime.fromisoformat(results['nautical_twilight_begin']).astimezone(local_tz)
            nautical_twilight_end_local = datetime.fromisoformat(results['nautical_twilight_end']).astimezone(local_tz)

            return (
                sunrise_local.strftime('%H:%M'), sunset_local.strftime('%H:%M'),
                civil_twilight_begin_local.strftime('%H:%M'), civil_twilight_end_local.strftime('%H:%M'),
                nautical_twilight_begin_local.strftime('%H:%M'), nautical_twilight_end_local.strftime('%H:%M')
            )
        else:
            st.error("Geen gegevens voor zonsopkomst en zonsondergang gevonden.")
            return None, None, None, None, None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van zonsopkomst/zonsondergang: {e}")
        return None, None, None, None, None, None

def show_input_form():
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Vogeltrek Weersgegevens</h1>", unsafe_allow_html=True)

    # Taalkeuze
    lang_choice = st.radio("", ["English", "Nederlands"], horizontal=True)
    st.session_state["language"] = lang_choice

    if lang_choice == "English":
        countries = EUROPEAN_COUNTRIES_EN
        labels = {
            "country": "Select Country", "location": "Location for weather",
            "date": "Date", "start_hour": "Start Hour", "end_hour": "End Hour"
        }
        default_country = "Belgium"
    else:
        countries = EUROPEAN_COUNTRIES_NL
        labels = {
            "country": "Selecteer land", "location": "Locatie voor weergegevens",
            "date": "Datum", "start_hour": "Beginuur", "end_hour": "Einduur"
        }
        default_country = "België"

    # Gebruikersinvoer
    country = st.selectbox(labels["country"], countries, index=countries.index(default_country))
    location = st.text_input(labels["location"], value="Bredene")
    selected_date = st.date_input(labels["date"], value=datetime.now().date())
    latitude, longitude = get_gps_coordinates(location)

    if latitude and longitude:
        sunrise, sunset, civil_twilight_begin, civil_twilight_end, _, _ = get_sun_times(latitude, longitude, selected_date)
        start_hour = datetime.strptime(civil_twilight_begin, '%H:%M').replace(minute=0)
        end_hour = datetime.strptime(civil_twilight_end, '%H:%M').replace(minute=0) + timedelta(hours=1)

        st.time_input(labels["start_hour"], value=start_hour.time(), key="start_hour")
        st.time_input(labels["end_hour"], value=end_hour.time(), key="end_hour")

        # Opslaan in session_state
        #st.session_state.update({
        #    "country": country, "location": location, "latitude": latitude, "longitude": longitude,
        #    "selected_date": selected_date, "sunrise": sunrise, "sunset": sunset,
        #    "start_hour": start_hour, "end_hour": end_hour
        #})

        st.write(f"Locatie: {country}, {location} - GPS: {latitude:.2f}°N {longitude:.2f}°E")
    else:
        st.error("GPS-coördinaten konden niet worden opgehaald.")

    return latitude, longitude, location
