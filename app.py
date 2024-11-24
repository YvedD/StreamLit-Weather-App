import streamlit as st
import requests

# Functie om het land van de gebruiker op basis van IP-adres op te halen
def get_country_from_ip():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        country = data.get('country', 'Unknown')
        return country
    except Exception as e:
        return "Unknown"

# Functie om geolocatie op te halen via JavaScript (HTML5 geolocatie)
def get_location_js():
    st.markdown("""
        <script type="text/javascript">
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    window.parent.postMessage({latitude, longitude}, "*");
                });
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        </script>
    """, unsafe_allow_html=True)

# Hoofdprogramma
def main():
    # Zoek de locatie op bij het openen van de app (IP-geolocatie voor desktop)
    if "latitude" not in st.session_state or "longitude" not in st.session_state:
        country = get_country_from_ip()  # IP-geolocatie ophalen
        st.session_state.country = country
        st.session_state.latitude = 51.2389  # Standaardlocatie voor België (Bredene)
        st.session_state.longitude = 2.9724

    # Voeg geolocatie via JavaScript toe voor mobiele apparaten
    if st.session_state.get("latitude") == 51.2389 and st.session_state.get("longitude") == 2.9724:
        get_location_js()  # Ophaal en verstuur de locatie via JS (voor mobiele apparaten)

    # Tab 1: Toon de locatiegegevens
    st.title("Locatiegegevens")
    st.subheader("Locatie van de gebruiker")
    st.write(f"Land: {st.session_state.get('country')}")
    st.write(f"Latitude: {st.session_state.get('latitude')}")
    st.write(f"Longitude: {st.session_state.get('longitude')}")

if __name__ == "__main__":
    main()
