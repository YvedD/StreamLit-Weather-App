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

# Functie om weergegevens op te halen via Open-Meteo API
def get_weather_data(lat, lon, start_date, end_date):
    api_url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,relative_humidity_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_80m,wind_direction_80m&timezone=Europe%2FBerlin"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Haal alle benodigde weerparameters op
        hourly_data = data['hourly']
        temperature = hourly_data['temperature_2m']
        humidity = hourly_data['relative_humidity_2m']
        precipitation = hourly_data['precipitation']
        cloud_cover = hourly_data['cloud_cover']
        cloud_cover_low = hourly_data['cloud_cover_low']
        cloud_cover_mid = hourly_data['cloud_cover_mid']
        cloud_cover_high = hourly_data['cloud_cover_high']
        visibility = hourly_data['visibility']
        wind_speed = hourly_data['wind_speed_80m']
        wind_direction = hourly_data['wind_direction_80m']

        return temperature, humidity, precipitation, cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high, visibility, wind_speed, wind_direction
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van weergegevens: {e}")
        return None, None, None, None, None, None, None, None, None, None

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

    # Expander voor zonsopkomst en zonsondergang
    with st.expander("Sunrise & Sunset Data", expanded=True):
        if latitude and longitude and sunrise and sunset:
            # Toon locatiegegevens en zonsopkomst/zonsondergang tijden
            st.write(f"**Country**: {country}, **Location**: {location}")
            st.write(f"**Date**: {selected_date}")
            st.write(f"**Start Hour**: {start_hour}, **End Hour**: {end_hour}")
            st.write(f"**Sunrise**: {sunrise}, **Sunset**: {sunset}")
        else:
            st.error("Er ontbreken gegevens. Zorg ervoor dat locatie en zonsopkomst/zonsondergang zijn geladen.")

    # Haal de weergegevens op van Open-Meteo
    if latitude and longitude and selected_date:
        temperature, humidity, precipitation, cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high, visibility, wind_speed, wind_direction = get_weather_data(latitude, longitude, selected_date, selected_date)

        if temperature and humidity and precipitation and cloud_cover and visibility and wind_speed and wind_direction:
            # Toon de gegevens in een andere expander voor de weerdata
            with st.expander("Hourly Weather Data", expanded=True):
                st.write(f"**Weather Data for {selected_date}:**")
                st.write("Hour | Temperature (°C) | Humidity (%) | Precipitation (mm) | Cloud Cover (%) | Low Cloud Cover (%) | Mid Cloud Cover (%) | High Cloud Cover (%) | Visibility (km) | Wind Speed (m/s) | Wind Direction (°)")
                for hour in range(len(temperature)):
                    st.write(f"{hour}:00 | {temperature[hour]}°C | {humidity[hour]}% | {precipitation[hour]} mm | {cloud_cover[hour]}% | {cloud_cover_low[hour]}% | {cloud_cover_mid[hour]}% | {cloud_cover_high[hour]}% | {visibility[hour]} km | {wind_speed[hour]} m/s | {wind_direction[hour]}°")
        else:
            st.error("Weerdata konden niet worden opgehaald.")
