import streamlit as st
import requests

# Functie om het land van de gebruiker op basis van IP-adres op te halen
def get_location_from_ip():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        location = data.get('loc', 'Unknown, Unknown').split(',')
        latitude = location[0]
        longitude = location[1]
        country = data.get('country', 'Unknown')
        return latitude, longitude, country
    except Exception as e:
        return None, None, "Unknown"

# Hoofdprogramma
def main():
    # Tab 1: Toon de locatiegegevens
    st.title("Locatiegegevens")
    st.subheader("Locatie van de gebruiker")

    # Zoek de locatie op bij het openen van de app (via IP-geolocatie)
    latitude, longitude, country = get_location_from_ip()

    if latitude and longitude:
        st.session_state.latitude = latitude
        st.session_state.longitude = longitude
        st.session_state.country = country
    else:
        st.write("Kan locatie niet ophalen.")

    # Weergeven van de locatiegegevens
    if "latitude" in st.session_state and "longitude" in st.session_state:
        st.write(f"Land: {st.session_state.get('country')}")
        st.write(f"Latitude: {st.session_state.get('latitude')}")
        st.write(f"Longitude: {st.session_state.get('longitude')}")
    else:
        st.write("Locatiegegevens worden opgehaald...")

if __name__ == "__main__":
    main()
