import streamlit as st
from datetime import datetime, timedelta, time
import requests
from timezonefinder import TimezoneFinder
from pytz import timezone
import folium
from streamlit_folium import st_folium

# Functie om de zonsopgang en zonsondergang op te halen via de Sunrise-Sunset API
def get_sun_times(lat, lon):
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
    response = requests.get(url)
    data = response.json()

    # Haal zonsopgang en zonsondergang tijden in UTC op
    sunrise_utc = data['results']['sunrise']
    sunset_utc = data['results']['sunset']
    civil_sunrise_utc = data['results']['civil_twilight_begin']
    civil_sunset_utc = data['results']['civil_twilight_end']
    nautical_sunrise_utc = data['results']['nautical_twilight_begin']
    nautical_sunset_utc = data['results']['nautical_twilight_end']

    # Converteer UTC naar lokale tijd
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)
    local_tz = timezone(timezone_str)

    # Zet tijden om naar lokale tijd
    def convert_to_local(utc_time):
        utc_dt = datetime.fromisoformat(utc_time)
        return utc_dt.astimezone(local_tz).time()

    local_times = {
        "sunrise": convert_to_local(sunrise_utc),
        "sunset": convert_to_local(sunset_utc),
        "civil_sunrise": convert_to_local(civil_sunrise_utc),
        "civil_sunset": convert_to_local(civil_sunset_utc),
        "nautical_sunrise": convert_to_local(nautical_sunrise_utc),
        "nautical_sunset": convert_to_local(nautical_sunset_utc),
    }

    return local_times

# Functie om de slider in te stellen
def create_time_slider(start_time, end_time):
    # Slider toont een tijdsinterval
    appointment = st.slider(
        "Selecteer het tijdsinterval:",
        min_value=time(0, 0),  # Begin om 00:00
        max_value=time(23, 59),  # Eindig om 23:59
        value=(start_time, end_time),  # Zet standaard op gekozen start/eindtijden
        step=timedelta(minutes=15),  # Intervals van 15 minuten
        format="HH:mm",  # Weergeven in HH:mm formaat
    )
    return appointment

# Functie om de coördinaten op te halen via Nominatim API
def get_coordinates(location, country):
    """Haal de breedte- en lengtegraad op van een opgegeven locatie."""
    url = f"https://nominatim.openstreetmap.org/search?q={location},{country}&format=json&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        if results:
            latitude = float(results[0]['lat'])
            longitude = float(results[0]['lon'])
            return latitude, longitude
    # Als geen resultaten gevonden zijn, gebruik standaardwaarden
    return None, None

# Functie om een Folium-kaart te genereren
def create_map(lat, lon):
    map_ = folium.Map(location=[lat, lon], zoom_start=9)
    
    # Aangepaste marker om te zorgen dat deze goed zichtbaar is
    icon = folium.Icon(color='green', icon='binoculars', icon_color='red', prefix='fa')
    folium.Marker([lat, lon], popup="Geselecteerde Locatie", icon=icon).add_to(map_)
    
    return map_

# Hoofdfunctie om de app te starten
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

    # Sidebar instellingen
    with st.sidebar:
        st.title("Locatie-instellingen")
        
        # Datumselectie
        selected_date = st.date_input("Selecteer een datum", value=datetime.now().date())

        # Land en locatie
        country = st.text_input("Land", value="België")
        location = st.text_input("Locatie", value="Bredene")

        # Haal coördinaten op
        lat, lon = get_coordinates(location, country)

        if lat is None or lon is None:
            st.warning("Locatie niet gevonden. Gebruik standaardwaarden.")
            lat, lon = 51.2389, 2.9724  # Default coördinaten

        # Folium-kaart in de sidebar
        map_ = create_map(lat, lon)
        st_folium(map_, width=600, height=250)

        # Haal zonstijden op
        sun_times = get_sun_times(lat, lon)
        
        # Keuze voor zonstijden
        sun_option = st.radio(
            "Selecteer type zonstijden",
            options=["Normal", "Civil", "Nautical"],
            index=1,
            horizontal=True
        )

        # Bepaal start- en eindtijd op basis van keuze
        if sun_option == "Normal":
            start_time, end_time = sun_times["sunrise"], sun_times["sunset"]
        elif sun_option == "Nautical":
            start_time, end_time = sun_times["nautical_sunrise"], sun_times["nautical_sunset"]
        else:
            start_time, end_time = sun_times["civil_sunrise"], sun_times["civil_sunset"]

        # Slider
        appointment = create_time_slider(start_time, end_time)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Weatherdata", "Temperature Forecast", "Multiday Forecast"])

    # Tab 1: Weatherdata
    with tab1:
        st.subheader("Weatherdata")
        st.write(f"**Land:** {country}")
        st.write(f"**Locatie:** {location}")
        st.write(f"**Latitude:** {lat}")
        st.write(f"**Longitude:** {lon}")
        st.write(f"**Geselecteerde Datum:** {selected_date}")
        st.write(f"**Zonstijden Type:** {sun_option}")
        st.write(f"**Zonsopgang:** {sun_times['sunrise'].strftime('%H:%M')}")
        st.write(f"**Zonsondergang:** {sun_times['sunset'].strftime('%H:%M')}")
        st.write(f"**Geselecteerde Starttijd:** {appointment[0].strftime('%H:%M')}")
        st.write(f"**Geselecteerde Eindtijd:** {appointment[1].strftime('%H:%M')}")

    with tab2:
        st.subheader("Temperature Forecast")
        st.write("Toon temperatuurvoorspellingen.")

    with tab3:
        st.subheader("Multiday Forecast")
        st.write("Toon meerdaagse weersvoorspellingen.")

if __name__ == "__main__":
    main()
