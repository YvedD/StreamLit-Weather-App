import streamlit as st
from datetime import datetime
import pytz
from dateutil import parser
import requests
from timezonefinder import TimezoneFinder

# Functie om zonsopkomst en zonsondergang te berekenen
def get_sun_times(lat, lon, date):
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

# Functie om actuele weergegevens op te halen via Open-Meteo API
def get_weather_data(lat, lon, date):
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,wind_speed_10m&start={date}T00:00:00Z&end={date}T23:59:59Z"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Haal de nodige weergegevens op (temperatuur, neerslag, wind)
        temperature = data['hourly']['temperature_2m']
        precipitation = data['hourly']['precipitation']
        wind_speed = data['hourly']['wind_speed_10m']

        return temperature, precipitation, wind_speed
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van weergegevens: {e}")
        return None, None, None

# Functie om de weergegevens en zonsopkomst/zonsondergang te tonen
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

            # Haal weergegevens op van Open-Meteo
            temperature, precipitation, wind_speed = get_weather_data(latitude, longitude, selected_date)

            if temperature and precipitation and wind_speed:
                st.write("**Weather Data (Hourly)**:")
                for i, hour in enumerate(range(int(start_hour[:2]), int(end_hour[:2]) + 1)):
                    # Alleen de relevante uren tonen
                    if hour < len(temperature):
                        st.write(f"Hour {hour}:00 - Temperature: {temperature[hour]}°C, "
                                 f"Precipitation: {precipitation[hour]} mm, Wind Speed: {wind_speed[hour]} m/s")
            else:
                st.error("Weergegevens konden niet worden opgehaald.")
        else:
            st.error("Er ontbreken gegevens. Zorg ervoor dat locatie en zonsopkomst/zonsondergang zijn geladen.")
