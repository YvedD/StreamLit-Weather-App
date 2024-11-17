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

# Twee arrays voor de Engelse en Nederlandse kompasrichtingen
english_compass_directions = [
    (0, "N"), (22.5, "NNE"), (45, "NE"), (67.5, "ENE"),
    (90, "E"), (112.5, "ESE"), (135, "SE"), (157.5, "SSE"),
    (180, "S"), (202.5, "SSW"), (225, "SW"), (247.5, "WSW"),
    (270, "W"), (292.5, "WNW"), (315, "NW"), (337.5, "NNW"), (360, "N")
]

dutch_compass_directions = [
    (0, "NO"), (22.5, "NNO"), (45, "NO"), (67.5, "ONO"),
    (90, "O"), (112.5, "OZO"), (135, "ZO"), (157.5, "ZZO"),
    (180, "Z"), (202.5, "ZZW"), (225, "ZW"), (247.5, "WZW"),
    (270, "W"), (292.5, "WNW"), (315, "NW"), (337.5, "NNW"), (360, "NO")
]

# Functie om windrichting te converteren naar kompasrichting
def degrees_to_compass(degrees, language="en"):
    directions = english_compass_directions if language == "en" else dutch_compass_directions
    
    for direction in directions:
        if degrees <= direction[0]:
            return direction[1]
    return "N"  # Default to N if no match

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
    language = st.session_state.get("language", "Nederlands")  # De taalkeuze, standaard Nederlands

    # Haal de weergegevens op van Open-Meteo
    if latitude and longitude and selected_date:
        temperature, humidity, precipitation, cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high, visibility, wind_speed, wind_direction = get_weather_data(latitude, longitude, selected_date, selected_date)

        if temperature and humidity and precipitation and cloud_cover and visibility and wind_speed and wind_direction:
            # Toon de gegevens in een andere expander voor de weerdata
            with st.expander("Hourly Weather Data", expanded=True):
                st.write(f"**Weather Data for {selected_date}:**")

                # Loop over alle uren en toon de gegevens per uur
                for hour in range(len(temperature)):
                    hour_label = f"{hour}:00"
                    # Zet windrichting om naar kompasrichting afhankelijk van de taalkeuze
                    wind_dir_compass = degrees_to_compass(wind_direction[hour], language)
                    # Maak de gegevens per uur op één regel
                    weather_info = f"{hour_label} | Temperature: {temperature[hour]}°C | Humidity: {humidity[hour]}% | Precipitation: {precipitation[hour]} mm | Cloud Cover: {cloud_cover[hour]}% | Low Cloud Cover: {cloud_cover_low[hour]}% | Mid Cloud Cover: {cloud_cover_mid[hour]}% | High Cloud Cover: {cloud_cover_high[hour]}% | Visibility: {visibility[hour]} km | Wind Speed: {wind_speed[hour]} m/s | Wind Direction: {wind_dir_compass}"
                    st.markdown(weather_info)

        else:
            st.error("Weerdata konden niet worden opgehaald.")
