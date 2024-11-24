import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests

# Functie om de zonstijden op te halen
def get_sun_times(lat, lon, date):
    # Verbind met een betrouwbare API (gebruik bijvoorbeeld de "Sunrise-Sunset" API)
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    response = requests.get(url)
    data = response.json()

    # Haal de benodigde zonsopgang en zonsondergang tijden op
    sunrise = data['results']['sunrise']  # Zonsopgang
    sunset = data['results']['sunset']  # Zonsondergang
    civil_sunrise = data['results']['civil_twilight_begin']  # Civiele zonsopgang
    civil_sunset = data['results']['civil_twilight_end']  # Civiele zonsondergang
    nautical_sunrise = data['results']['nautical_twilight_begin']  # Nautische zonsopgang
    nautical_sunset = data['results']['nautical_twilight_end']  # Nautische zonsondergang

    return sunrise, sunset, civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset

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
    sunrise, sunset, civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset = get_sun_times(lat, lon, date)

    # Zet de tijden om naar lokale tijd
    sunrise_local = parse_time(sunrise)
    sunset_local = parse_time(sunset)
    civil_sunrise_local = parse_time(civil_sunrise)
    civil_sunset_local = parse_time(civil_sunset)
    nautical_sunrise_local = parse_time(nautical_sunrise)
    nautical_sunset_local = parse_time(nautical_sunset)

    # Sidebar voor de selectie van de zonsopgang- en zonsondergangtijden
    sun_type = st.sidebar.radio("Select Sun Times", ["Sunrise/Sunset", "Civil", "Nautical"], index=0)

    # Bepaal de begin- en eindtijden in de slider op basis van de keuze
    if sun_type == "Sunrise/Sunset":
        slider_start = sunrise_local
        slider_end = sunset_local
    elif sun_type == "Civil":
        slider_start = civil_sunrise_local
        slider_end = civil_sunset_local
    elif sun_type == "Nautical":
        slider_start = nautical_sunrise_local
        slider_end = nautical_sunset_local

    # Zet de slider om de tijd in uren en minuten te kiezen (afronden naar beneden voor start, naar boven voor eind)
    start_hour = slider_start.replace(minute=0, second=0, microsecond=0)
    end_hour = slider_end.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)  # Afronden naar boven voor eind

    # Om de tijdswaarden van de slider in minuten weer te geven
    def format_time(time_obj):
        return time_obj.strftime("%H:%M")

    # Sidebar Slider (per minuut)
    time_slider = st.sidebar.slider(
        "Select Time Period (minutes)",
        min_value=int(start_hour.timestamp() // 60),
        max_value=int(end_hour.timestamp() // 60),
        value=(int(start_hour.timestamp() // 60), int(end_hour.timestamp() // 60)),
        step=1,
        format="time",
    )

    # Toon de gekozen tijdsperiode in het hoofdgedeelte van de app (tot op minuut)
    start_time_selected = datetime.fromtimestamp(time_slider[0] * 60, pytz.timezone('Europe/Brussels'))
    end_time_selected = datetime.fromtimestamp(time_slider[1] * 60, pytz.timezone('Europe/Brussels'))

    # Toon de tijden boven de bolletjes van de slider
    st.write(f"**Start Time**: {format_time(start_time_selected)}")
    st.write(f"**End Time**: {format_time(end_time_selected)}")

    # Toon de zonstijden in de tab (tot op minuut)
    st.write(f"**Selected Sun Type**: {sun_type}")
    st.write(f"**Zonsopgang**: {format_time(sunrise_local)}")
    st.write(f"**Zonsondergang**: {format_time(sunset_local)}")
    st.write(f"**Civiele Zonsopgang**: {format_time(civil_sunrise_local)}")
    st.write(f"**Civiele Zonsondergang**: {format_time(civil_sunset_local)}")
    st.write(f"**Nautische Zonsopgang**: {format_time(nautical_sunrise_local)}")
    st.write(f"**Nautische Zonsondergang**: {format_time(nautical_sunset_local)}")

# App structuur
def main():
    # Configuratie voor de pagina
    st.set_page_config(page_title="Sun Times App", layout="wide")
    st.title("Sunrise, Sunset, and Twilight Times")

    # Hoofd app content
    show_sun_times()

if __name__ == "__main__":
    main()
