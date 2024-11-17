import streamlit as st
from datetime import datetime
import pytz
from dateutil import parser
from timezonefinder import TimezoneFinder
import requests

def get_sun_times(lat, lon, date):
    # Functie om zonsopkomst en zonsondergang te berekenen
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)

    if timezone_str is None:
        st.error("Kan de tijdzone voor deze locatie niet vinden.")
        return None, None

    # API aanroepen voor zonsopkomst en zonsondergang
    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if 'results' in data:
            sunrise_utc = parser.isoparse(data['results']['sunrise'])
            sunset_utc = parser.isoparse(data['results']['sunset'])

            # Converteer naar lokale tijdzone
            local_tz = pytz.timezone(timezone_str)
            sunrise_local = sunrise_utc.astimezone(local_tz)
            sunset_local = sunset_utc.astimezone(local_tz)

            return sunrise_local.strftime('%H:%M'), sunset_local.strftime('%H:%M')
        else:
            st.error("Zonsopkomst en zonsondergang niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van zonsopkomst/zondondergang tijden: {e}")
        return None, None

def show_data_expander():
    # Verkrijg gegevens uit session_state
    country = st.session_state.get("country")
    location = st.session_state.get("location")
    selected_date = st.session_state.get("selected_date")
    start_hour = st.session_state.get("start_hour")
    end_hour = st.session_state.get("end_hour")
    latitude = st.session_state.get("latitude")
    longitude = st.session_state.get("longitude")
    sunrise = st.session_state.get("sunrise")
    sunset = st.session_state.get("sunset")

    # Titel boven de expander
    st.markdown(
        '<h3 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px; text-align: center;">'
        'Weather Data for Migration</h3>',
        unsafe_allow_html=True
    )

    # Expander voor weergegevens
    with st.expander("Weather Data", expanded=True):
        if latitude and longitude and sunrise and sunset:
            # Toon locatiegegevens en zonsopkomst/zonsondergang tijden
            st.write(f"**Country**: {country}, **Location**: {location}")
            st.write(f"**Date**: {selected_date}")
            st.write(f"**Start Hour**: {start_hour}, **End Hour**: {end_hour}")
            st.write(f"**Sunrise**: {sunrise}, **Sunset**: {sunset}")

            # Toon de gegevens voor de gekozen uren
            sunrise_time = datetime.strptime(sunrise, "%H:%M")
            sunset_time = datetime.strptime(sunset, "%H:%M")

            # Als de start- en einduren liggen tussen zonsopkomst en zonsondergang
            hours = [f"{hour:02d}:00" for hour in range(int(sunrise_time.hour), int(sunset_time.hour) + 1)]
            hours_in_range = [hour for hour in hours if start_hour <= hour <= end_hour]

            st.write("Available Hours:", ", ".join(hours_in_range))
        else:
            st.error("Er ontbreken gegevens. Zorg ervoor dat locatie en zonsopkomst/zonsondergang zijn geladen.")
