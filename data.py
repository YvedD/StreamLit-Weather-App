import streamlit as st

# Functie voor de expander die gegevens toont
def show_data_expander():
    # Check of de benodigde gegevens aanwezig zijn in st.session_state
    if 'latitude' in st.session_state and 'longitude' in st.session_state and 'location' in st.session_state:
        latitude = st.session_state['latitude']
        longitude = st.session_state['longitude']
        location = st.session_state['location']

        # Maak een expander die altijd uitgeklapt is
        with st.expander("Location Data", expanded=True):
            st.write("### Location Details")
            st.write(f"**Location:** {location}")
            st.write(f"**Latitude:** {latitude:.2f}")
            st.write(f"**Longitude:** {longitude:.2f}")

            # Toon alle andere gegevens die we mogelijk hebben opgeslagen in session_state
            if 'sunrise' in st.session_state and 'sunset' in st.session_state:
                sunrise = st.session_state['sunrise']
                sunset = st.session_state['sunset']
                st.write(f"**Sunrise:** {sunrise}")
                st.write(f"**Sunset:** {sunset}")

            # Als er geen sunrise of sunset beschikbaar zijn, geef een waarschuwing
            else:
                st.write("**Sunrise and Sunset data are not available.**")
    else:
        st.error("No location data found in session state.")  # Als er geen locatiegegevens in session_state zijn
