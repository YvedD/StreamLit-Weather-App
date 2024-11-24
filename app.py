import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests

# Functie om de zonstijden op te halen
def get_sun_times(lat, lon, date):
    # Verbind met een betrouwbare API (gebruik bijvoorbeeld de "SunCalc" API of een andere zonstijdbepaling API)
    # Dit is een voorbeeld link, zorg ervoor dat je een echte API kiest en een valid key hebt
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    response = requests.get(url)
    data = response.json()

    # Haal de benodigde zonsopgang en zonsondergang tijden op
    civil_sunrise = data['results']['civil_twilight_begin']  # Civiele zonsopgang
    civil_sunset = data['results']['civil_twilight_end']  # Civiele zonsondergang
    nautical_sunrise = data['results']['nautical_twilight_begin']  # Nautische zonsopgang
    nautical_sunset = data['results']['nautical_twilight_end']  # Nautische zonsondergang

    return civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset

# Functie om een datetime object te maken van een tijdstring
def parse_time(time_str):
    # Zet de tijd van UTC naar lokale tijd (en pas DST aan)
    utc_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+00:00')
    local_time = utc_time.astimezone(pytz.timezone('Europe/Brussels'))  # Stel de tijdzone in
    return local_time

# Functie om de slider en de bijbehorende gegevens te tonen
def show_sun_times():
    # Stel locatie in voor België (Bredene) en kies de datum van vandaag
    lat = 51.2389
    lon = 2.9724
    date = datetime.now().strftime('%Y-%m-%d')  # Datum van vandaag

    # Haal zonstijden op
    civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset = get_sun_times(lat, lon, date)

    # Zet de tijden om naar lokale tijd
    civil_sunrise_local = parse_time(civil_sunrise)
    civil_sunset_local = parse_time(civil_sunset)
    nautical_sunrise_local = parse_time(nautical_sunrise)
    nautical_sunset_local = parse_time(nautical_sunset)

    # Toon de tijden in de tekst
    st.write(f"**Civiele Zonsopgang**: {civil_sunrise_local.strftime('%H:%M')}")
    st.write(f"**Civiele Zonsondergang**: {civil_sunset_local.strftime('%H:%M')}")
    st.write(f"**Nautische Zonsopgang**: {nautical_sunrise_local.strftime('%H:%M')}")
    st.write(f"**Nautische Zonsondergang**: {nautical_sunset_local.strftime('%H:%M')}")

    # Toon een radiobutton om de tijdsinstellingen te kiezen
    sun_type = st.radio("Choose Sun Times", ["Civiele", "Nautische"], index=0)

    # Stel de begin- en eindtijden in de slider in op basis van de keuze
    if sun_type == "Civiele":
        slider_start = civil_sunrise_local.replace(minute=0, second=0, microsecond=0)
        slider_end = nautical_sunset_local.replace(minute=0, second=0, microsecond=0)
    else:  # Nautische tijd
        slider_start = nautical_sunrise_local.replace(minute=0, second=0, microsecond=0)
        slider_end = civil_sunset_local.replace(minute=0, second=0, microsecond=0)

    # Zet de slider om de tijd in uren te kiezen
    start_hour = slider_start.hour
    end_hour = slider_end.hour

    time_slider = st.slider(
        "Select Time Period (hours)",
        min_value=0,
        max_value=23,
        value=(start_hour, end_hour),
        step=1
    )

    # Toon de gekozen tijdsperiode
    st.write(f"**Selected Time Period**: {time_slider[0]}:00 - {time_slider[1]}:00")

# App structuur
def main():
    st.set_page_config(page_title="Sun Times App", layout="wide")
    st.title("Sunrise, Sunset, and Twilight Times")

    show_sun_times()

if __name__ == "__main__":
    main()
