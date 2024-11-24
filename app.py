import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests

# Functie om de zonstijden op te halen
def get_sun_times(lat, lon, date):
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    response = requests.get(url)
    data = response.json()

    sunrise = data['results']['sunrise']
    sunset = data['results']['sunset']
    civil_sunrise = data['results']['civil_twilight_begin']
    civil_sunset = data['results']['civil_twilight_end']
    nautical_sunrise = data['results']['nautical_twilight_begin']
    nautical_sunset = data['results']['nautical_twilight_end']

    return sunrise, sunset, civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset

# Functie om een datetime object te maken van een tijdstring
def parse_time(time_str, timezone):
    utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+00:00')
    return utc_time.astimezone(timezone)

# Functie om tijden te formatteren
def format_time(dt):
    return dt.strftime("%H:%M")

# Functie om de slider te tonen met annotaties
def show_slider_with_times(slider_start, slider_end):
    # Converteer de begin- en eindtijden naar timestamps voor de slider
    start_timestamp = int(slider_start.timestamp())
    end_timestamp = int(slider_end.timestamp())

    # Slider component
    selected_time_range = st.slider(
        "Select Time Period:",
        min_value=start_timestamp,
        max_value=end_timestamp,
        value=(start_timestamp, end_timestamp),
        step=60,
        format=None,
    )

    # Gekozen start- en eindtijd
    start_time = datetime.fromtimestamp(selected_time_range[0], pytz.timezone('Europe/Brussels'))
    end_time = datetime.fromtimestamp(selected_time_range[1], pytz.timezone('Europe/Brussels'))

    # Toon de tijden boven de markers
    st.write(
        f"**Start Time Marker**: {format_time(slider_start)} | "
        f"**End Time Marker**: {format_time(slider_end)}"
    )
    st.write(f"**Selected Start Time**: {format_time(start_time)}")
    st.write(f"**Selected End Time**: {format_time(end_time)}")

    return start_time, end_time

# Functie om de UI-componenten te tonen
def show_sun_times():
    # Sidebar Locatie en Datum
    st.sidebar.header("Location and Date")
    country = st.sidebar.text_input("Country", "Belgium")
    location = st.sidebar.text_input("Location", "Bredene")
    lat = st.sidebar.number_input("Latitude", 51.2389)
    lon = st.sidebar.number_input("Longitude", 2.9724)
    date = st.sidebar.date_input("Date", datetime.now().date())

    # Haal de zonstijden op
    timezone = pytz.timezone('Europe/Brussels')
    sun_times = get_sun_times(lat, lon, date)
    sunrise_local = parse_time(sun_times[0], timezone)
    sunset_local = parse_time(sun_times[1], timezone)
    civil_sunrise_local = parse_time(sun_times[2], timezone)
    civil_sunset_local = parse_time(sun_times[3], timezone)
    nautical_sunrise_local = parse_time(sun_times[4], timezone)
    nautical_sunset_local = parse_time(sun_times[5], timezone)

    # Kies tussen de verschillende zontypes
    sun_type = st.sidebar.radio(
        "Select Sun Times Type",
        ["Sunrise/Sunset", "Civil", "Nautical"],
        index=1
    )

    # Tijden voor de slider op basis van keuze
    if sun_type == "Sunrise/Sunset":
        slider_start = sunrise_local
        slider_end = sunset_local
    elif sun_type == "Civil":
        slider_start = civil_sunrise_local
        slider_end = civil_sunset_local
    elif sun_type == "Nautical":
        slider_start = nautical_sunrise_local
        slider_end = nautical_sunset_local

    # Toon slider en markeringen
    start_time, end_time = show_slider_with_times(slider_start, slider_end)

    # Tekstweergave van alle zontijden
    st.header("Sun Times for Selected Location")
    st.write(f"**Country**: {country}")
    st.write(f"**Location**: {location}")
    st.write(f"**Date**: {date}")
    st.write(f"**Selected Sun Type**: {sun_type}")
    st.write(f"**Zonsopgang**: {format_time(sunrise_local)}")
    st.write(f"**Zonsondergang**: {format_time(sunset_local)}")
    st.write(f"**Civiele Zonsopgang**: {format_time(civil_sunrise_local)}")
    st.write(f"**Civiele Zonsondergang**: {format_time(civil_sunset_local)}")
    st.write(f"**Nautische Zonsopgang**: {format_time(nautical_sunrise_local)}")
    st.write(f"**Nautische Zonsondergang**: {format_time(nautical_sunset_local)}")

# App structuur
def main():
    st.set_page_config(page_title="Sun Times App", layout="wide")
    st.title("Sunrise, Sunset, and Twilight Times")

    # Toon de zonstijden
    show_sun_times()

if __name__ == "__main__":
    main()
