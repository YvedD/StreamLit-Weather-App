import streamlit as st
from datetime import datetime, timedelta
import requests
import pytz

# Standaardinstellingen
default_country = "België"
default_location = "Bredene"
latitude = 51.2389
longitude = 2.9724
selected_date = datetime.now() - timedelta(days=1)

# Functie om de tijdzone op te halen via een API
def get_timezone_info(latitude, longitude):
    # Gebruik een API zoals TimeZoneDB of GeoNames
    api_url = f"http://api.geonames.org/timezoneJSON?lat={latitude}&lng={longitude}&username=your_geonames_username"
    response = requests.get(api_url)
    data = response.json()
    
    # Haal de tijdzone en DST-gegevens uit de response
    timezone = data.get("timezoneId", "Europe/Brussels")
    dst = data.get("dstOffset", 0)  # De DST offset in seconden
    return timezone, dst

# Functie om een tijdstempel om te zetten naar de lokale tijd
def convert_to_local_time(utc_time, timezone, dst_offset):
    utc_time = utc_time.replace(tzinfo=pytz.UTC)  # Zet de tijd om naar UTC
    local_time = utc_time.astimezone(pytz.timezone(timezone))  # Converteer naar lokale tijd
    local_time += timedelta(seconds=dst_offset)  # Pas de DST-offset toe
    return local_time

# Sessie initialiseren met standaardinstellingen
def initialize_session_state():
    if "country" not in st.session_state:
        st.session_state["country"] = default_country
    if "location" not in st.session_state:
        st.session_state["location"] = default_location
    if "latitude" not in st.session_state:
        st.session_state["latitude"] = latitude
    if "longitude" not in st.session_state:
        st.session_state["longitude"] = longitude
    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = selected_date

# Haal de standaard zonsopgang en zonsondergang op via een API (bv. SunriseSunset API)
def get_sun_times(latitude, longitude, date):
    # Gebruik een API om de tijden op te halen (Sunrise-Sunset API)
    api_url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date={date}&formatted=0"
    response = requests.get(api_url)
    data = response.json()
    
    return data["results"]

# Haal de standaardlocatiegegevens en zonsopgang/zonsondergang op
initialize_session_state()
sun_times = get_sun_times(st.session_state["latitude"], st.session_state["longitude"], st.session_state["selected_date"].date())

# Haal tijdzone-informatie op voor de opgegeven locatie
timezone, dst_offset = get_timezone_info(st.session_state["latitude"], st.session_state["longitude"])

# Zet de zonsopgang en zonsondergang om naar lokale tijd
sunrise_utc = datetime.fromisoformat(sun_times["sunrise"])
sunset_utc = datetime.fromisoformat(sun_times["sunset"])
civil_sunrise_utc = datetime.fromisoformat(sun_times["civil_twilight_begin"])
civil_sunset_utc = datetime.fromisoformat(sun_times["civil_twilight_end"])
nautical_sunrise_utc = datetime.fromisoformat(sun_times["nautical_twilight_begin"])
nautical_sunset_utc = datetime.fromisoformat(sun_times["nautical_twilight_end"])

sunrise_local = convert_to_local_time(sunrise_utc, timezone, dst_offset)
sunset_local = convert_to_local_time(sunset_utc, timezone, dst_offset)
civil_sunrise_local = convert_to_local_time(civil_sunrise_utc, timezone, dst_offset)
civil_sunset_local = convert_to_local_time(civil_sunset_utc, timezone, dst_offset)
nautical_sunrise_local = convert_to_local_time(nautical_sunrise_utc, timezone, dst_offset)
nautical_sunset_local = convert_to_local_time(nautical_sunset_utc, timezone, dst_offset)

# Toon de gegevens in Streamlit
st.write(f"Land: {st.session_state['country']}")
st.write(f"Locatie: {st.session_state['location']}")
st.write(f"Latitude: {st.session_state['latitude']}")
st.write(f"Longitude: {st.session_state['longitude']}")
st.write(f"Datum: {st.session_state['selected_date'].date()}")
st.write(f"Zonsopgang: {sunrise_local.strftime('%H:%M')}")
st.write(f"Zonsondergang: {sunset_local.strftime('%H:%M')}")
st.write(f"Civiele zonsopgang: {civil_sunrise_local.strftime('%H:%M')}")
st.write(f"Civiele zonsondergang: {civil_sunset_local.strftime('%H:%M')}")
st.write(f"Nautische zonsopgang: {nautical_sunrise_local.strftime('%H:%M')}")
st.write(f"Nautische zonsondergang: {nautical_sunset_local.strftime('%H:%M')}")
