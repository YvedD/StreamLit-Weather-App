import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests

# Functie om de zonstijden op te halen
def get_sun_times(lat, lon, date):
    # Sunrise-Sunset API
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    response = requests.get(url)
    data = response.json()

    # Haal zonstijden op
    sunrise = data['results']['sunrise']
    sunset = data['results']['sunset']
    civil_sunrise = data['results']['civil_twilight_begin']
    civil_sunset = data['results']['civil_twilight_end']
    nautical_sunrise = data['results']['nautical_twilight_begin']
    nautical_sunset = data['results']['nautical_twilight_end']

    return sunrise, sunset, civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset

# Functie om UTC-tijd om te zetten naar lokale tijd
def parse_time(time_str):
    utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+00:00')
    local_time = utc_time.astimezone(pytz.timezone('Europe/Brussels'))
    return local_time

# Functie voor tijdsnotatie in HH:mm
def format_time(dt):
    return dt.strftime("%H:%M")

# Functie om de applicatie-UI te tonen
def show_sun_times():
    # Standaard locatie en datum
    lat = 51.2389
    lon = 2.9724
    date = datetime.now().strftime('%Y-%m-%d')

    # Haal zonstijden op
    sunrise, sunset, civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset = get_sun_times(lat, lon, date)

    # Zet zonstijden om naar lokale tijd
    sunrise_local = parse_time(sunrise)
    sunset_local = parse_time(sunset)
    civil_sunrise_local = parse_time(civil_sunrise)
    civil_sunset_local = parse_time(civil_sunset)
    nautical_sunrise_local = parse_time(nautical_sunrise)
    nautical_sunset_local = parse_time(nautical_sunset)

    # Sidebar voor locatie en datumselectie
    st.sidebar.write("### Instellingen")
    st.sidebar.text_input("Land", "België")
    st.sidebar.text_input("Locatie", "Bredene")
    st.sidebar.date_input("Datum", datetime.now())

    # Radiobutton voor type zonstijden
    sun_type = st.sidebar.radio("Selecteer zonstijden", ["Sunrise/Sunset", "Civil", "Nautical"], index=0, horizontal=True)

    # Bepaal start- en eindtijd afhankelijk van de selectie
    if sun_type == "Sunrise/Sunset":
        slider_start = sunrise_local
        slider_end = sunset_local
    elif sun_type == "Civil":
        slider_start = civil_sunrise_local
        slider_end = civil_sunset_local
    elif sun_type == "Nautical":
        slider_start = nautical_sunrise_local
        slider_end = nautical_sunset_local

    # Bereken afronding voor slider
    start_hour = slider_start.replace(minute=0, second=0, microsecond=0)
    end_hour = slider_end.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    # Slider minimum, maximum, en markers
    slider_min = 0
    slider_max = 23
    slider_markers = {i: f"{i:02d}:00" for i in range(slider_min, slider_max + 1)}

    # Sidebar slider
    time_range = st.sidebar.slider(
        "Selecteer tijdsperiode",
        min_value=slider_min,
        max_value=slider_max,
        value=(start_hour.hour, end_hour.hour),
        step=1,
        format=""
    )

    # Toon de geselecteerde tijden onder de slider
    chosen_start_time = datetime.combine(datetime.now(), datetime.min.time()) + timedelta(hours=time_range[0])
    chosen_end_time = datetime.combine(datetime.now(), datetime.min.time()) + timedelta(hours=time_range[1])
    st.sidebar.write(f"**Gekozen tijdsperiode:** {chosen_start_time.strftime('%H:%M')} - {chosen_end_time.strftime('%H:%M')}")

    # Zonstijden in het tabblad
    st.write("### Zonstijden")
    st.write(f"**Zonstijlen:** {sun_type}")
    st.write(f"**Zonsopgang:** {format_time(sunrise_local)}")
    st.write(f"**Zonsondergang:** {format_time(sunset_local)}")
    st.write(f"**Civiele Zonsopgang:** {format_time(civil_sunrise_local)}")
    st.write(f"**Civiele Zonsondergang:** {format_time(civil_sunset_local)}")
    st.write(f"**Nautische Zonsopgang:** {format_time(nautical_sunrise_local)}")
    st.write(f"**Nautische Zonsondergang:** {format_time(nautical_sunset_local)}")

# App structuur
def main():
    # Configuratie voor de pagina
    st.set_page_config(page_title="Sun Times App", layout="wide")
    st.title("Sunrise, Sunset, and Twilight Times")

    # Hoofdapp inhoud
    show_sun_times()

if __name__ == "__main__":
    main()
