import streamlit as st

def show_data_expander():
    # Haal de gegevens uit session_state
    country = st.session_state.get('country', 'Unknown')  # Haal het land op, met 'Unknown' als default
    location = st.session_state.get('location', 'Unknown')  # Haal de locatie op
    selected_date = st.session_state.get('selected_date', 'Unknown')  # Haal de datum op, met 'Unknown' als default
    start_hour = st.session_state.get('start_hour', 'Unknown')  # Haal het startuur op
    end_hour = st.session_state.get('end_hour', 'Unknown')  # Haal het einduur op
    latitude = st.session_state.get('latitude', 'Unknown')  # Haal de latitude op
    longitude = st.session_state.get('longitude', 'Unknown')  # Haal de longitude op
    sunrise = st.session_state.get('sunrise', 'Unknown')  # Haal de sunrise op
    sunset = st.session_state.get('sunset', 'Unknown')  # Haal de sunset op

    # Maak een expander die altijd uitgeklapt is
    with st.expander("Location Data", expanded=True):
        st.write("### Location Details")
        st.write(f"**Location:** {location}")
        st.write(f"**Latitude:** {latitude}")
        st.write(f"**Longitude:** {longitude}")
        st.write(f"**Country:** {country}")
        st.write(f"**Date:** {selected_date}")
        st.write(f"**Start Hour:** {start_hour}")
        st.write(f"**End Hour:** {end_hour}")

        if sunrise != 'Unknown' and sunset != 'Unknown':
            st.write(f"**Sunrise:** {sunrise}")
            st.write(f"**Sunset:** {sunset}")
        else:
            st.write("**Sunrise and Sunset data are not available.**")
