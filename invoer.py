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

    # Retourneer de waarden
    return latitude, longitude, location
