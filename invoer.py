import streamlit as st
from datetime import datetime, timedelta
import requests
from timezonefinder import TimezoneFinder
import pytz

# Lijsten van Europese landen in Engels en Nederlands
EUROPEAN_COUNTRIES_EN = [
    "Belgium", "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Bulgaria", "Bosnia and Herzegovina", 
    "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "Georgia", "Germany", 
    "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein", 
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", 
    "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", 
    "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"
]

EUROPEAN_COUNTRIES_NL = [
    "België", "Albanië", "Andorra", "Armenië", "Oostenrijk", "Azerbeidzjan", "Bulgarije", "Bosnië en Herzegovina", 
    "Kroatië", "Cyprus", "Tsjechië", "Denemarken", "Estland", "Finland", "Georgië", "Duitsland", 
    "Griekenland", "Hongarije", "IJsland", "Ierland", "Italië", "Kazachstan", "Kosovo", "Letland", "Liechtenstein", 
    "Litouwen", "Luxemburg", "Malta", "Moldavië", "Monaco", "Montenegro", "Nederland", "Noord-Macedonië", 
    "Noorwegen", "Polen", "Portugal", "Roemenië", "Rusland", "San Marino", "Servië", "Slovenië", "Slovenië", 
    "Spanje", "Zweden", "Zwitserland", "Turkije", "Oekraïne", "Verenigd Koninkrijk", "Vaticaanstad"
]

# Functie om GPS-coördinaten op te halen via geocoding service
def get_gps_coordinates(location):
    api_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1&limit=1"
    try:
        response = requests.get(api_url)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error("Locatie niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van GPS-coördinaten: {e}")
        return None, None

# Functie om zonsopkomst en zonsondergang te berekenen
def get_sun_times(lat, lon, date):
    if lat is None or lon is None:
        st.error("Ongeldige GPS-coördinaten.")
        return None, None, None, None  # Extra return-waarden voor nautische schemering
    
    # Bepaal de tijdzone van de opgegeven locatie
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)
    
    if timezone_str is None:
        st.error("Kan de tijdzone voor deze locatie niet vinden.")
        return None, None, None, None

    # Sunrise-sunset API-aanroep voor de opgegeven datum en locatie
    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Controleer of er resultaten zijn
        if 'results' in data:
            # Converteer UTC-tijden voor sunrise, sunset, nautische dawn en nautische dusk naar datetime-objecten
            sunrise_utc = datetime.fromisoformat(data['results']['sunrise'])
            sunset_utc = datetime.fromisoformat(data['results']['sunset'])
            nautical_dawn_utc = datetime.fromisoformat(data['results']['nautical_twilight_begin'])
            nautical_dusk_utc = datetime.fromisoformat(data['results']['nautical_twilight_end'])

            # Laad de lokale tijdzone
            local_tz = pytz.timezone(timezone_str)
            
            # Converteer UTC-tijden naar lokale tijdzone, rekening houdend met DST
            sunrise_local = sunrise_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            sunset_local = sunset_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            nautical_dawn_local = nautical_dawn_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            nautical_dusk_local = nautical_dusk_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)

            # Geef de exacte tijden terug zonder afronding, rekening houdend met DST
            return (
                sunrise_local.strftime('%H:%M'), 
                sunset_local.strftime('%H:%M'), 
                nautical_dawn_local.strftime('%H:%M'), 
                nautical_dusk_local.strftime('%H:%M')
            )
        else:
            st.error("Zonsopkomst en zonsondergang niet gevonden.")
            return None, None, None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van zonsopkomst/zondondergang tijden: {e}")
        return None, None, None, None

# Functie voor invoerformulier
def show_input_form():
    # Standaardwaarden
    default_country_en = "Belgium"  
    default_country_nl = "België"  
    default_location = "Bredene"
    selected_date = datetime.now().date() - timedelta(days=1)

    # Titel boven de expander
    st.markdown(
        '<h3 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px; text-align: center;">'
        'Migration Historic Weather Data<br>and 3 day Forecast</h3>',
        unsafe_allow_html=True
    )

    # Expander voor de invoer
    with st.expander("Input Data", expanded=True):
        # Taalkeuze door middel van een radio knop
        lang_choice = st.radio(
            "Select Language/Kies uw taal",
            options=["English", "Nederlands"],
            index=1 if st.session_state.get("language", "English") == "English" else 1,
            key="language_selector",
            horizontal=True
        )

        # Sla de taalkeuze op in de session_state
        st.session_state["language"] = lang_choice

        # Kies de landenlijst en labels op basis van de taal
        if lang_choice == "English":
            countries = EUROPEAN_COUNTRIES_EN
            country_label = "Select Country"
            location_label = "Location for weather"
            date_label = "Date"
            start_hour_label = "Start Hour"
            end_hour_label = "End Hour"
            sunrise_label = "Sunrise"
            sunset_label = "Sunset"
            default_country = default_country_en
        else:
            countries = EUROPEAN_COUNTRIES_NL
            country_label = "Selecteer land"
            location_label = "Locatie voor weergegevens"
            date_label = "Datum"
            start_hour_label = "Beginuur"
            end_hour_label = "Einduur"
            sunrise_label = "Zonsopkomst"
            sunset_label = "Zonsondergang"
            default_country = default_country_nl

        # Formulier voor invoer
        country = st.selectbox(country_label, countries, index=countries.index(default_country))  
        location = st.text_input(location_label, value=default_location)
        selected_date = st.date_input(date_label, value=selected_date)
        
        # Verkrijg GPS-coördinaten voor de locatie
        latitude, longitude = get_gps_coordinates(location)

        # Haal zonsopkomst en zonsondergang op
        if latitude and longitude:
            sunrise, sunset = get_sun_times(latitude, longitude, selected_date)
        else:
            sunrise = sunset = None
        
        # Stel standaard start- en einduren in op basis van zonsopkomst en zonsondergang
        start_hour = sunrise if sunrise else "00:00"
        end_hour = sunset if sunset else "23:00"

        st.selectbox(start_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=int(start_hour.split(":")[0]))
        st.selectbox(end_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=int(end_hour.split(":")[0]))

        # Sla alle benodigde gegevens op in de session_state
        st.session_state["country"] = country
        st.session_state["location"] = location
        st.session_state["selected_date"] = selected_date
        st.session_state["start_hour"] = start_hour
        st.session_state["end_hour"] = end_hour
        st.session_state["latitude"] = latitude
        st.session_state["longitude"] = longitude
        st.session_state["sunrise"] = sunrise
        st.session_state["sunset"] = sunset
        st.session_state["language"] = lang_choice

        # Toon locatiegegevens en zonsopkomst/zondondergang tijden
        if latitude and longitude:
            st.write(f"**Country**: {country}, **Location**: {location}, **GPS**: {latitude:.2f}°N {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**Sunrise**: {sunrise_local}, **Sunset**: {sunset_local}")
                st.write(f"**Sunrise**: {nautical_dusk_local}, **Sunset**: {nautical_dawn_local}")

        else:
            st.write(f"{location_label} not found.")

    # Retourneer de waarden
    return latitude, longitude, location
