import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests

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

# Placeholder voor jouw bestaande code voor temperatuurvoorspellingen
def show_temperature_forecast():
    # Je eigen code voor het ophalen en weergeven van de temperatuurvoorspellingen
    st.write("Dit is de temperatuurvoorspelling tab. Voeg hier je code in.")
    
# Placeholder voor jouw bestaande code voor meerdaagse weersvoorspellingen
def show_multiday_forecast():
    # Je eigen code voor het ophalen en weergeven van de meerdaagse weersvoorspellingen
    st.write("Dit is de meerdaagse weersvoorspelling tab. Voeg hier je code in.")

# Hoofdfunctie om de app te starten
def main():
    # Sidebar configuratie
    with st.sidebar:
        st.title("Locatie-instellingen")
        
        # Selecteer de datum via de sidebar
        selected_date = st.date_input("Selecteer een datum", value=datetime.now().date())

        # Locatiegegevens kunnen ook aangepast worden in de sidebar
        default_country = st.text_input("Land", value="België")
        default_location = st.text_input("Locatie", value="Bredene")
        latitude = st.number_input("Latitude", value=51.2389)
        longitude = st.number_input("Longitude", value=2.9724)

    # Initialiseer de gegevens en toon ze
    initialize_location_data()

    # Maak tabs aan voor de verschillende secties
    tab1, tab2, tab3 = st.tabs(["Weatherdata", "Temperature Forecast", "Multiday Forecast"])

    # Tab 1: Weatherdata
    with tab1:
        st.subheader("Weatherdata")
        # Hier kunnen we de weerdata weergeven, die via een API of een andere bron opgehaald wordt
        st.write("Weatherdata tab - Toon actuele weersomstandigheden")

    # Tab 2: Temperature Forecast
    with tab2:
        st.subheader("Temperature Forecast")
        show_temperature_forecast()  # Jouw werkende code voor temperatuurvoorspelling

    # Tab 3: Multiday Forecast
    with tab3:
        st.subheader("Multiday Forecast")
        show_multiday_forecast()  # Jouw werkende code voor meerdaagse weersvoorspelling

if __name__ == "__main__":
    main()
