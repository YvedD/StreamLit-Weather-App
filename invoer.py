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
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error("Location not found.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Error fetching GPS coordinates: {e}")
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
    default_country_en = "Belgium"  
    default_country_nl = "België"  
    default_location = "Bredene"
    selected_date = datetime.now().date() - timedelta(days=1)

    st.markdown(
        '<h1 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px;">Migration Weather Data</h1>',
        unsafe_allow_html=True
    )

    with st.expander("Input Data", expanded=True):  
        lang_choice = st.radio(
            "Select Language/Kies uw taal",
            options=["English", "Nederlands"],
            index=0 if st.session_state.get("language", "English") == "English" else 1,
            key="language_selector",
            horizontal=True
        )

        st.session_state["language"] = lang_choice

        if lang_choice == "English":
            countries = EUROPEAN_COUNTRIES_EN
            labels = {
                "country": "Select Country", "location": "Location for weather", 
                "date": "Date", "start_hour": "Start Hour", "end_hour": "End Hour",
                "sunrise": "Sunrise", "sunset": "Sunset", 
                "civil_twilight_begin": "Civil Twilight Begins", 
                "civil_twilight_end": "Civil Twilight Ends",
                "nautical_twilight_begin": "Nautical Twilight Begins", 
                "nautical_twilight_end": "Nautical Twilight Ends"
            }
            default_country = default_country_en
        else:
            countries = EUROPEAN_COUNTRIES_NL
            labels = {
                "country": "Selecteer land", "location": "Locatie voor weergegevens", 
                "date": "Datum", "start_hour": "Beginuur", "end_hour": "Einduur",
                "sunrise": "Zonsopkomst", "sunset": "Zonsondergang", 
                "civil_twilight_begin": "Begin burgerlijke schemering", 
                "civil_twilight_end": "Einde burgerlijke schemering",
                "nautical_twilight_begin": "Begin nautische schemering", 
                "nautical_twilight_end": "Einde nautische schemering"
            }
            default_country = default_country_nl

        st.header(f"{labels['location']} ")

        country = st.selectbox(labels['country'], countries, index=countries.index(default_country))
        location = st.text_input(labels['location'], value=default_location)
        selected_date = st.date_input(labels['date'], value=selected_date)
        start_hour = st.selectbox(labels['start_hour'], [f"{hour:02d}:00" for hour in range(24)], index=8)
        end_hour = st.selectbox(labels['end_hour'], [f"{hour:02d}:00" for hour in range(24)], index=16)

        latitude, longitude = get_gps_coordinates(location)
        
        if latitude and longitude:
            sunrise, sunset, civil_twilight_begin, civil_twilight_end, nautical_twilight_begin, nautical_twilight_end = get_sun_times(latitude, longitude, selected_date)
            
            st.write(f"**{labels['country']}**: {country}, **{labels['location']}**: {location}, **GPS**: {latitude:.2f}°N, {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**{labels['sunrise']}**: {sunrise}, **{labels['sunset']}**: {sunset}")
                st.write(f"**{labels['civil_twilight_begin']}**: {civil_twilight_begin}, **{labels['civil_twilight_end']}**: {civil_twilight_end}")
                st.write(f"**{labels['nautical_twilight_begin']}**: {nautical_twilight_begin}, **{labels['nautical_twilight_end']}**: {nautical_twilight_end}")
        else:
            st.write(f"{labels['location']} not found.")
