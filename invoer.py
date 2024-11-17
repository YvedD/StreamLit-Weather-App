# invoer.py
import streamlit as st
from datetime import datetime, timedelta  # Zorg ervoor dat zowel datetime als timedelta zijn geïmporteerd

def show_input_form():
    # Standaardwaarden voor locatie en datum
    default_country_en = "Belgium"
    default_country_nl = "België"
    default_location = "Bredene"
    latitude = 51.2389
    longitude = 2.9724
    selected_date = datetime.now().date() - timedelta(days=1)

    # Voeg enkel de titel toe boven de expander
    st.markdown(
    '<h3 style="font-size: 36px; font-weight: bold; color: #4CAF50; margin-bottom: 20px; text-align: center;">Migration Historic Weather Data<br>and 3 day Forecast</h3>',
    unsafe_allow_html=True
    )
    # Expander die altijd uitgeklapt is
    with st.expander("Input Data", expanded=True):  # Dit maakt de expander standaard uitgeklapt

        # Zet standaard de taal op Nederlands
        lang_choice = st.radio(
            "Select Language/Kies uw taal",
            options=["English", "Nederlands"],
            index=1,  # Zet de index standaard op 1 voor Nederlands
            key="language_selector",
            horizontal=True
        )

        st.session_state["language"] = lang_choice

        if lang_choice == "English":
            countries = EUROPEAN_COUNTRIES_EN
            country_label = "Select Country"
            country_text = "Country"
            location_label = "Location for weather"
            location_text = "Location"
            date_label = "Date"
            start_hour_label = "Start Hour"
            end_hour_label = "End Hour"
            sunrise_label = "Sunrise"
            sunset_label = "Sunset"
            default_country = default_country_en
        else:
            countries = EUROPEAN_COUNTRIES_NL
            country_label = "Selecteer land"
            country_text = "Land"
            location_label = "Locatie voor weergegevens"
            location_text = "Locatie"
            date_label = "Datum"
            start_hour_label = "Beginuur"
            end_hour_label = "Einduur"
            sunrise_label = "Zonsopkomst"
            sunset_label = "Zonsondergang"
            default_country = default_country_nl

        st.header(f"{location_label} " )

        # Formulier voor het invoeren van gegevens
        country = st.selectbox(country_label, countries, index=countries.index(default_country))
        location = st.text_input(location_label, value=default_location)
        selected_date = st.date_input(date_label, value=selected_date)
        start_hour = st.selectbox(start_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=8)
        end_hour = st.selectbox(end_hour_label, [f"{hour:02d}:00" for hour in range(24)], index=16)

        # Verkrijg de GPS-coördinaten voor de nieuwe locatie
        latitude, longitude = get_gps_coordinates(location)

        if latitude and longitude:
            sunrise, sunset = get_sun_times(latitude, longitude, selected_date)
        else:
            sunrise = sunset = None

        # Sla alle relevante waarden op in session_state
        st.session_state["country"] = country
        st.session_state["location"] = location
        st.session_state["latitude"] = latitude
        st.session_state["longitude"] = longitude
        st.session_state["selected_date"] = selected_date
        st.session_state["start_hour"] = start_hour
        st.session_state["end_hour"] = end_hour

        if latitude and longitude:
            st.write(f"**{country_text}**: {country}, **{location_text}**: {location}, **GPS** :{latitude:.2f}°N {longitude:.2f}°E")
            if sunrise and sunset:
                st.write(f"**{sunrise_label}**: {sunrise}, **{sunset_label}**: {sunset}")
        else:
            st.write(f"{location_label} not found.")

    return latitude, longitude, location
