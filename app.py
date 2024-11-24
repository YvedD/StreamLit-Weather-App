import streamlit as st
from datetime import datetime, timedelta
import requests
import pytz

# Standaardinstellingen
default_country = "België"
default_location = "Bredene"
latitude = 51.2389
longitude = 2.9724
selected_date = datetime.now()  # Vandaag

# Functie om de tijdzone op te halen via een API
@st.cache_data
def get_timezone_info(latitude, longitude):
    # Gebruik een API zoals TimeZoneDB of GeoNames
    api_url = f"http://api.geonames.org/timezoneJSON?lat={latitude}&lng={longitude}&username=your_geonames_username"
    response = requests.get(api_url)
    data = response.json()
    
    # Haal de tijdzone en DST-gegevens uit de response
    timezone = data.get("timezoneId", "Europe/Brussels")
    dst = data.get("dstOffset", 0)  # De DST offset in seconden
    return timezone, dst

# Functie om zonsopgang- en zonsondergangtijden op te halen via een API
@st.cache_data
def get_sun_times(latitude, longitude, date):
    # Gebruik een API om de tijden op te halen (Sunrise-Sunset API)
    api_url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date={date}&formatted=0"
    response = requests.get(api_url)
    data = response.json()
    
    return data["results"]

# Functie om een tijdstempel om te zetten naar de lokale tijd
def convert_to_local_time(utc_time, timezone, dst_offset):
    utc_time = utc_time.replace(tzinfo=pytz.UTC)  # Zet de tijd om naar UTC
    local_time = utc_time.astimezone(pytz.timezone(timezone))  # Converteer naar lokale tijd
    local_time += timedelta(seconds=dst_offset)  # Pas de DST-offset toe
    return local_time

# Functie om alle gegevens op te halen en weer te geven
def initialize_location_data():
    # Haal de standaardlocatiegegevens en zonsopgang/zonsondergang op
    sun_times = get_sun_times(latitude, longitude, selected_date.date())

    # Haal tijdzone-informatie op voor de opgegeven locatie
    timezone, dst_offset = get_timezone_info(latitude, longitude)

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
    st.write(f"Land: {default_country}")
    st.write(f"Locatie: {default_location}")
    st.write(f"Latitude: {latitude}")
    st.write(f"Longitude: {longitude}")
    st.write(f"Datum: {selected_date.date()}")
    st.write(f"Zonsopgang: {sunrise_local.strftime('%H:%M')}")
    st.write(f"Zonsondergang: {sunset_local.strftime('%H:%M')}")
    st.write(f"Civiele zonsopgang: {civil_sunrise_local.strftime('%H:%M')}")
    st.write(f"Civiele zonsondergang: {civil_sunset_local.strftime('%H:%M')}")
    st.write(f"Nautische zonsopgang: {nautical_sunrise_local.strftime('%H:%M')}")
    st.write(f"Nautische zonsondergang: {nautical_sunset_local.strftime('%H:%M')}")

# Functie om weerdata op te halen
@st.cache_data
def get_weather_data(latitude, longitude):
    # Voorbeeld API-aanroep voor weerdata
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=your_api_key&units=metric"
    response = requests.get(api_url)
    return response.json()

# Functie om temperatuurvoorspellingen op te halen
@st.cache_data
def get_temperature_forecast(latitude, longitude):
    # Voorbeeld API-aanroep voor temperatuurvoorspelling
    api_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid=your_api_key&units=metric"
    response = requests.get(api_url)
    return response.json()

# Functie om meerdaagse voorspellingen op te halen
@st.cache_data
def get_multiday_forecast(latitude, longitude):
    # Voorbeeld API-aanroep voor meerdaagse voorspellingen
    api_url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={latitude}&lon={longitude}&cnt=7&appid=your_api_key&units=metric"
    response = requests.get(api_url)
    return response.json()

# Hoofdfunctie om de app te starten
def main():
    # Initialiseer de gegevens en toon ze
    initialize_location_data()

    # Maak tabs aan voor de verschillende secties
    tab1, tab2, tab3 = st.tabs(["Weatherdata", "Temperature Forecast", "Multiday Forecast"])

    # Tab 1: Weatherdata
    with tab1:
        st.subheader("Weatherdata")
        weather_data = get_weather_data(latitude, longitude)
        st.write(weather_data)  # Dit is tijdelijk; vervang door de specifieke velden die je wilt tonen.

    # Tab 2: Temperature Forecast
    with tab2:
        st.subheader("Temperature Forecast")
        temperature_forecast = get_temperature_forecast(latitude, longitude)
        st.write(temperature_forecast)  # Dit is tijdelijk; vervang door de specifieke velden die je wilt tonen.

    # Tab 3: Multiday Forecast
    with tab3:
        st.subheader("Multiday Forecast")
        multiday_forecast = get_multiday_forecast(latitude, longitude)
        st.write(multiday_forecast)  # Dit is tijdelijk; vervang door de specifieke velden die je wilt tonen.

if __name__ == "__main__":
    main()
