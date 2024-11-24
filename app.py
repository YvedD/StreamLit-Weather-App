import streamlit as st
from datetime import datetime, timedelta, time
import requests
from timezonefinder import TimezoneFinder
from pytz import timezone
import pytz

# Functie om de zonsopgang en zonsondergang op te halen via de Sunrise-Sunset API
def get_sun_times(lat, lon):
    # API-endpoint voor Sunrise-Sunset API
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
    response = requests.get(url)
    data = response.json()

    # Haal de zonsopgang en zonsondergang tijden in UTC op
    sunrise_utc = data['results']['sunrise']
    sunset_utc = data['results']['sunset']
    
    # Converteer UTC naar lokale tijd (inclusief rekening houden met de tijdzone en DST)
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)  # Vind de tijdzone van de locatie
    local_tz = timezone(timezone_str)  # Gebruik pytz om de tijdzone te verkrijgen

    # Zet de tijden om van UTC naar lokale tijd
    utc_sunrise = datetime.fromisoformat(sunrise_utc)
    utc_sunset = datetime.fromisoformat(sunset_utc)

    local_sunrise = utc_sunrise.astimezone(local_tz).time()
    local_sunset = utc_sunset.astimezone(local_tz).time()

    return local_sunrise, local_sunset

# Functie om de slider in te stellen voor de start- en eindtijden
def create_time_slider(start_hour, end_hour):
    # Ronde start- en eindtijden af naar beneden en naar boven
    start_hour_rounded = time(start_hour.hour, 0)  # Ronden naar beneden naar het begin van het uur
    end_hour_rounded = time(end_hour.hour + 1, 0)  # Ronden naar boven naar het begin van het volgende uur

    # De slider retourneert een tuple van de start- en eindtijden
    appointment = st.slider(
        "Selecteer het tijdsinterval:",
        min_value=time(0, 0),  # Begin om 00:00
        max_value=time(23, 0),  # Eindig om 23:00
        value=(start_hour_rounded, end_hour_rounded),  # De standaardwaarden worden ingesteld op civiele zonsopgang en zonsondergang
        step=timedelta(hours=1),  # Stappen van één uur
        format="HH:mm",  # Weergeven in het formaat uur:minuten
    )

    # Toon de geselecteerde tijden boven de slider
    st.write(f"Starttijd: {appointment[0].strftime('%H:%M')}")
    st.write(f"Eindtijd: {appointment[1].strftime('%H:%M')}")
    
    return appointment

# Hoofdfunctie om de app te starten
def main():
    # Instellen van de standaardlocatie (Bredene, België) als voorbeeld
    default_country = "België"
    default_location = "Bredene"
    latitude = 51.2389
    longitude = 2.9724
    selected_date = datetime.now().date()  # Gebruik de huidige datum

    # Haal de zonsopgang en zonsondergang op voor de gekozen locatie (Bredene)
    sunrise, sunset = get_sun_times(latitude, longitude)

    # Sidebar configuratie
    with st.sidebar:
        st.title("Locatie-instellingen")
        
        # Selecteer de datum via de sidebar
        selected_date = st.date_input("Selecteer een datum", value=datetime.now().date())

        # Locatiegegevens kunnen ook aangepast worden in de sidebar
        default_country = st.text_input("Land", value=default_country)
        default_location = st.text_input("Locatie", value=default_location)
        latitude = st.number_input("Latitude", value=latitude)
        longitude = st.number_input("Longitude", value=longitude)

        # Keuze voor de zonsopgang/ondergang
        zonsopgang_keuze = st.radio(
            "Selecteer type zonsopgang/zonsondergang",
            options=["Normal", "Civil", "Nautical"],
            index=1,  # Standaard op 'Civil'
            horizontal=True  # Zet de radio buttons naast elkaar
        )

        # Sla de geselecteerde optie op in de session_state
        if "zonsopgang_keuze" not in st.session_state:
            st.session_state.zonsopgang_keuze = "Civil"
        st.session_state.zonsopgang_keuze = zonsopgang_keuze
        
        # Kies de juiste zonsopgang/zonsondergang tijden op basis van de keuze
        if zonsopgang_keuze == "Normal":
            start_hour, end_hour = sunrise, sunset
        elif zonsopgang_keuze == "Nautical":
            start_hour, end_hour = sunrise, sunset
        else:  # 'Civil' is de default
            start_hour, end_hour = sunrise, sunset

        # Voeg de tijdsinterval slider toe met de civiele zonsopgang en zonsondergang als standaard
        appointment = create_time_slider(start_hour, end_hour)

    # Maak tabs aan voor de verschillende secties
    tab1, tab2, tab3 = st.tabs(["Weatherdata", "Temperature Forecast", "Multiday Forecast"])

    # Tab 1: Weatherdata
    with tab1:
        st.subheader("Weatherdata")
        st.write("Locatiegegevens:")
        st.write(f"Land: {default_country}")
        st.write(f"Locatie: {default_location}")
        st.write(f"Latitude: {latitude}")
        st.write(f"Longitude: {longitude}")
        st.write(f"Geselecteerde datum: {selected_date}")

        # Toon de geselecteerde tijden en zonsopgang/ondergang details
        st.write(f"Zonsopgang type: {zonsopgang_keuze}")
        st.write(f"Zonsopgang: {sunrise.strftime('%H:%M')}")
        st.write(f"Zonsondergang: {sunset.strftime('%H:%M')}")

        # De slider tijden (start en eindtijden)
        st.write(f"Starttijd van geselecteerd interval: {appointment[0].strftime('%H:%M')}")
        st.write(f"Eindtijd van geselecteerd interval: {appointment[1].strftime('%H:%M')}")

    # Tab 2: Temperature Forecast
    with tab2:
        st.subheader("Temperature Forecast")
        st.write("Temperature Forecast tab - Toon temperatuurvoorspellingen")

    # Tab 3: Multiday Forecast
    with tab3:
        st.subheader("Multiday Forecast")
        st.write("Multiday Forecast tab - Toon meerdaagse weersvoorspellingen")

if __name__ == "__main__":
    main()
