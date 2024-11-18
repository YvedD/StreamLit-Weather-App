#invoer.py - dit is de basiscode om invoer door de gebruikers toe te laten en verschillende belangrijke variabelen op te slaan via st.session_state()
import streamlit as st
from datetime import datetime, timedelta
import requests
from timezonefinder import TimezoneFinder
import pytz

# Lijst van Europese landen in Engels en Nederlands
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
        response.raise_for_status()  # Dit zorgt ervoor dat we een foutmelding krijgen bij een slechte API-aanroep
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error(f"Locatie '{location}' niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van GPS-coördinaten voor locatie '{location}': {e}")
        return None, None
# Functie om zonsopkomst, zonsondergang, en schemeringstijden te berekenen
def get_sun_times(lat, lon, date):
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)
    
    if not timezone_str:
        st.error("Timezone not found for the specified location.")
        return None, None, None, None, None, None

    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if 'results' in data:
            results = data['results']
            
            # Converteer tijden naar datetime-objecten
            sunrise_utc = datetime.fromisoformat(results['sunrise'])
            sunset_utc = datetime.fromisoformat(results['sunset'])
            civil_twilight_begin_utc = datetime.fromisoformat(results['civil_twilight_begin'])
            civil_twilight_end_utc = datetime.fromisoformat(results['civil_twilight_end'])
            nautical_twilight_begin_utc = datetime.fromisoformat(results['nautical_twilight_begin'])
            nautical_twilight_end_utc = datetime.fromisoformat(results['nautical_twilight_end'])
            
            # Zet de tijden om naar lokale tijdzone
            local_tz = pytz.timezone(timezone_str)
            
            # Localize de tijden en pas zonetijd toe
            sunrise_local = sunrise_utc.astimezone(local_tz)
            sunset_local = sunset_utc.astimezone(local_tz)
            civil_twilight_begin_local = civil_twilight_begin_utc.astimezone(local_tz)
            civil_twilight_end_local = civil_twilight_end_utc.astimezone(local_tz)
            nautical_twilight_begin_local = nautical_twilight_begin_utc.astimezone(local_tz)
            nautical_twilight_end_local = nautical_twilight_end_utc.astimezone(local_tz)
            
            # Formatteer de tijden in het juiste formaat
            sun_times = {
                "sunrise": sunrise_local.strftime('%H:%M'),
                "sunset": sunset_local.strftime('%H:%M'),
                "civil_twilight_begin": civil_twilight_begin_local.strftime('%H:%M'),
                "civil_twilight_end": civil_twilight_end_local.strftime('%H:%M'),
                "nautical_twilight_begin": nautical_twilight_begin_local.strftime('%H:%M'),
                "nautical_twilight_end": nautical_twilight_end_local.strftime('%H:%M')
            }
            
            return (sun_times['sunrise'], sun_times['sunset'], 
                    sun_times['civil_twilight_begin'], sun_times['civil_twilight_end'],
                    sun_times['nautical_twilight_begin'], sun_times['nautical_twilight_end'])
        else:
            st.error("Sunrise and sunset times not found.")
            return None, None, None, None, None, None
            
    except requests.RequestException as e:
        st.error(f"Error fetching sunrise/sunset times: {e}")
        return None, None, None, None, None, None
# De invoerfunctie die de gegevens toont en de invoer mogelijk maakt
def show_input_form():
    # Standaardwaarden voor locatie en datum
    default_country_en = "Belgium"  # Engels
    default_country_nl = "België"  # Nederlands
    default_location = "Bredene"
    latitude = 51.2389
    longitude = 2.9724
    selected_date = datetime.now().date() - timedelta(days=1)

    # Voeg enkel de titel toe boven de expander
    st.markdown(
        '<h1 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px;">Migration Weather Data</h1>',
        unsafe_allow_html=True
    )

    # Expander die altijd uitgeklapt is
    with st.expander("Input Data", expanded=True):

        # Taalkeuze door middel van een two-state switch binnen de expander
        lang_choice = st.radio(
            "Select Language/Kies uw taal",
            options=["English", "Nederlands"],
            index=0 if st.session_state.get("language", "English") == "English" else 1,
            key="language_selector",  
            horizontal=True  
        )

        # Sla de taalkeuze op in de session_state
        st.session_state["language"] = lang_choice

        # Kies de landenlijst en de standaardwaarde op basis van de taal
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

        # Formulier voor het invoeren van gegevens
        country = st.selectbox(country_label, countries, index=countries.index(default_country))  # Lijst van Europese landen
        location = st.text_input(location_label, value=default_location)
        selected_date = st.date_input(date_label, value=selected_date)
        start_hour = st.selectbox(start_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=8)
        end_hour = st.selectbox(end_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=16)

        # Verkrijg de GPS-coördinaten voor de nieuwe locatie
        latitude, longitude = get_gps_coordinates(location)

        if latitude is None or longitude is None:
            st.error(f"Could not retrieve GPS coordinates for {location}. Please try again.")
            return None, None, None

        # Haal zonsopkomst en zonsondergang tijden op
        sunrise, sunset, civil_twilight_begin, civil_twilight_end, nautical_twilight_begin, nautical_twilight_end = get_sun_times(latitude, longitude, selected_date)

        # Sla de gegevens op in st.session_state
        st.session_state["latitude"] = latitude
        st.session_state["longitude"] = longitude
        st.session_state["location"] = location
        st.session_state["selected_date"] = selected_date
        st.session_state["start_hour"] = start_hour
        st.session_state["end_hour"] = end_hour
        st.session_state["sunrise"] = sunrise
        st.session_state["sunset"] = sunset
        st.session_state["civil_twilight_begin"] = civil_twilight_begin
        st.session_state["civil_twilight_end"] = civil_twilight_end
        st.session_state["nautical_twilight_begin"] = nautical_twilight_begin
        st.session_state["nautical_twilight_end"] = nautical_twilight_end

        # Toon Land, Locatie, Latitude en Longitude, en Zonsopkomst/Zonsondergang
        if latitude and longitude:
            st.write(f"**Country**: {country}, **Location**: {location}, **GPS** :{latitude:.2f}°N {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**{sunrise_label}**: {sunrise}, **{sunset_label}**: {sunset}")
                # Toon ook de civiele en nautische schemeringstijden
                st.write(f"**Civil Twilight Begin**: {civil_twilight_begin}, **Civil Twilight End**: {civil_twilight_end}")
                st.write(f"**Nautical Twilight Begin**: {nautical_twilight_begin}, **Nautical Twilight End**: {nautical_twilight_end}")
        else:
            st.write(f"{location_label} not found.")  # Foutmelding in de gekozen taal

        # Geef de latitude, longitude en locatie terug voor gebruik in de kaartmodule
        return latitude, longitude, location
