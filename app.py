import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests

# Functie om zonstijden op te halen
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

# Functie om `st.session_state` te initialiseren of bij te werken
def update_session_state(lat, lon, date):
    if "sun_times" not in st.session_state or st.session_state.get("last_updated_date") != date:
        sunrise, sunset, civil_sunrise, civil_sunset, nautical_sunrise, nautical_sunset = get_sun_times(lat, lon, date)

        st.session_state["sun_times"] = {
            "sunrise": parse_time(sunrise),
            "sunset": parse_time(sunset),
            "civil_sunrise": parse_time(civil_sunrise),
            "civil_sunset": parse_time(civil_sunset),
            "nautical_sunrise": parse_time(nautical_sunrise),
            "nautical_sunset": parse_time(nautical_sunset),
        }
        st.session_state["last_updated_date"] = date

# Functie om de applicatie-UI te tonen
def show_sun_times():
    # Standaard locatie en datum
    lat = 51.2389
    lon = 2.9724
    date = datetime.now().strftime('%Y-%m-%d')

    # Haal of update zonstijden in `st.session_state`
    update_session_state(lat, lon, date)

    # Haal de zonstijden op uit `st.session_state`
    sun_times = st.session_state["sun_times"]

    # Sidebar voor locatie, datum en zonstijdtype
    st.sidebar.write("### Instellingen")
    st.sidebar.text_input("Land", "België")
    st.sidebar.text_input("Locatie", "Bredene")
    selected_date = st.sidebar.date_input("Datum", datetime.now())

    # Radiobutton voor type zonstijden
    sun_type = st.sidebar.radio("Selecteer zonstijden", ["Sunrise/Sunset", "Civil", "Nautical"], index=0, horizontal=True)

    # Bepaal start- en eindtijd afhankelijk van de selectie
    if sun_type == "Sunrise/Sunset":
        slider_start = sun_times["sunrise"]
        slider_end = sun_times["sunset"]
    elif sun_type == "Civil":
        slider_start = sun_times["civil_sunrise"]
        slider_end = sun_times["civil_sunset"]
    elif sun_type == "Nautical":
        slider_start = sun_times["nautical_sunrise"]
        slider_end = sun_times["nautical_sunset"]

    # Slider met volledige uren en markers
    start_hour = slider_start.replace(minute=0, second=0, microsecond=0)
    end_hour = slider_end.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    slider_min = 0
    slider_max = 23

    # Slider minimum, maximum, en markers
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
    st.write(f"**Zonsopgang:** {format_time(sun_times['sunrise'])}")
    st.write(f"**Zonsondergang:** {format_time(sun_times['sunset'])}")
    st.write(f"**Civiele Zonsopgang:** {format_time(sun_times['civil_sunrise'])}")
    st.write(f"**Civiele Zonsondergang:** {format_time(sun_times['civil_sunset'])}")
    st.write(f"**Nautische Zonsopgang:** {format_time(sun_times['nautical_sunrise'])}")
    st.write(f"**Nautische Zonsondergang:** {format_time(sun_times['nautical_sunset'])}")

# App structuur
def main():
    # Configuratie voor de pagina
    st.set_page_config(layout="wide")

    # CSS om iconen en menu te verbergen
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.write("De bovenste iconen zijn nu verborgen!")    
    st.title("Sunrise, Sunset, and Twilight Times")
    #st.title("Mijn Streamlit App")

    # Hoofdapp inhoud
    show_sun_times()

if __name__ == "__main__":
    main()
