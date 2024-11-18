#invoer.py - dit is de basiscode om invoer door de gebruikers toe te laten en verschillende belangrijke variabelen op te slaan via st.session_state()

import streamlit as st
from datetime import datetime, timedelta
import requests
from timezonefinder import TimezoneFinder
import pytz

# Functie om GPS-coördinaten op te halen
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

# Functie om zonsopkomst, zonsondergang en schemeringstijden op te halen
def get_sun_times(lat, lon, date):
    if lat is None or lon is None:
        st.error("Ongeldige GPS-coördinaten.")
        return None, None, None, None, None, None, None, None

    # Bepaal de tijdzone voor de locatie
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lng=lon, lat=lat)
    
    if timezone_str is None:
        st.error("Kan de tijdzone voor deze locatie niet vinden.")
        return None, None, None, None, None, None, None, None

    # API-aanroep voor de zon- en schemeringstijden
    api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Controleer of resultaten bestaan
        if 'results' in data:
            # Converteer UTC-tijden voor zonsopkomst, zonsondergang en schemering naar datetime
            sunrise_utc = datetime.fromisoformat(data['results']['sunrise'])
            sunset_utc = datetime.fromisoformat(data['results']['sunset'])
            nautical_dawn_utc = datetime.fromisoformat(data['results']['nautical_twilight_begin'])
            nautical_dusk_utc = datetime.fromisoformat(data['results']['nautical_twilight_end'])
            civil_dawn_utc = datetime.fromisoformat(data['results']['civil_twilight_begin'])
            civil_dusk_utc = datetime.fromisoformat(data['results']['civil_twilight_end'])

            # Laad de lokale tijdzone
            local_tz = pytz.timezone(timezone_str)

            # Converteer UTC-tijden naar lokale tijdzone, met DST-controle
            sunrise_local = sunrise_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            sunset_local = sunset_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            nautical_dawn_local = nautical_dawn_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            nautical_dusk_local = nautical_dusk_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            civil_dawn_local = civil_dawn_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            civil_dusk_local = civil_dusk_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)

            # Controleer of DST actief is
            dst_active = sunrise_local.dst() != timedelta(0)
            dst_status = "DST in effect" if dst_active else "No DST in effect for this location/date"

            # Geef de tijden terug, rekening houdend met DST
            return (
                sunrise_local.strftime('%H:%M'),
                sunset_local.strftime('%H:%M'),
                nautical_dawn_local.strftime('%H:%M'),
                nautical_dusk_local.strftime('%H:%M'),
                civil_dawn_local.strftime('%H:%M'),
                civil_dusk_local.strftime('%H:%M'),
                dst_status
            )
        else:
            st.error("Zonsopkomst en zonsondergang niet gevonden.")
            return None, None, None, None, None, None, "DST status onbekend"
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van zonsopkomst/zondondergang tijden: {e}")
        return None, None, None, None, None, None, "DST status onbekend"

# Functie om het invoerformulier weer te geven en gegevens op te slaan
def show_input_form():
    default_country_en = "Belgium"
    default_country_nl = "België"
    default_location = "Bredene"
    selected_date = datetime.now().date() - timedelta(days=1)

    # Titel en invoerformulier
    st.markdown(
        '<h3 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px; text-align: center;">'
        'Migration Historic Weather Data<br>and 3 day Forecast</h3>',
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
        countries, country_label, location_label, date_label, start_hour_label, end_hour_label = (
            (EUROPEAN_COUNTRIES_EN, "Select Country", "Location for weather", "Date", "Start Hour", "End Hour")
            if lang_choice == "English" else
            (EUROPEAN_COUNTRIES_NL, "Selecteer land", "Locatie voor weergegevens", "Datum", "Beginuur", "Einduur")
        )
        default_country = default_country_en if lang_choice == "English" else default_country_nl

        country = st.selectbox(country_label, countries, index=countries.index(default_country))
        location = st.text_input(location_label, value=default_location)
        selected_date = st.date_input(date_label, value=selected_date)

        start_hour = st.selectbox(start_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=8)
        end_hour = st.selectbox(end_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=16)

        st.session_state.update({
            "country": country,
            "location": location,
            "selected_date": selected_date,
            "start_hour": start_hour,
            "end_hour": end_hour
        })

        latitude, longitude = get_gps_coordinates(location)
        if latitude is not None and longitude is not None:
            st.session_state["latitude"], st.session_state["longitude"] = latitude, longitude

            sunrise, sunset, nautical_dawn, nautical_dusk, civil_dawn, civil_dusk, dst_status = get_sun_times(
                latitude, longitude, selected_date
            )

            if sunrise and sunset and nautical_dawn and nautical_dusk and civil_dawn and civil_dusk:
                st.session_state.update({
                    "sunrise": sunrise,
                    "sunset": sunset,
                    "nautical_dawn": nautical_dawn,
                    "nautical_dusk": nautical_dusk,
                    "civil_dawn": civil_dawn,
                    "civil_dusk": civil_dusk,
                    "dst_status": dst_status
                })

                st.write(f"**Country**: {country}, **Location**: {location}, **GPS**: {latitude:.2f}°N, {longitude:.2f}°E")
                st.write(f"**Sunrise**: {sunrise}, **Sunset**: {sunset}")
                st.write(f"**Nautical Dawn**: {nautical_dawn}, **Nautical Dusk**: {nautical_dusk}")
                st.write(f"**Civil Dawn**: {civil_dawn}, **Civil Dusk**: {civil_dusk}")
                st.write(f"**DST Status**: {dst_status}")
            else:
                st.warning("Could not retrieve complete sunrise and sunset information.")
        else:
            st.error("Could not retrieve GPS coordinates for the provided location.")

    return latitude, longitude, location
