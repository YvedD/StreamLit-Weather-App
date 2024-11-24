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
    # We gebruiken JavaScript om de geolocatie van de gebruiker op te halen
    st.markdown("""
        <script type="text/javascript">
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    // Verstuur de opgehaalde locatie naar Streamlit
                    window.parent.postMessage({latitude, longitude}, "*");
                }, function(error) {
                    console.log(error);
                });
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        </script>
    """, unsafe_allow_html=True)

# Hoofdprogramma
def main():
    # Tab 1: Toon de locatiegegevens
    st.title("Locatiegegevens")
    st.subheader("Locatie van de gebruiker")

    # Zoek de locatie op bij het openen van de app (IP-geolocatie voor desktop)
    if "latitude" not in st.session_state or "longitude" not in st.session_state:
        country = get_country_from_ip()  # IP-geolocatie ophalen
        st.session_state.country = country

        # Voeg geolocatie via JavaScript toe voor mobiele apparaten
        get_location_js()  # Ophaal en verstuur de locatie via JS (voor mobiele apparaten)

    # Wacht tot de locatiegegevens beschikbaar zijn
    if "latitude" in st.session_state and "longitude" in st.session_state:
        st.write(f"Land (op basis van IP): {st.session_state.get('country')}")
        st.write(f"Latitude: {st.session_state.get('latitude')}")
        st.write(f"Longitude: {st.session_state.get('longitude')}")
    else:
        st.write("Locatie wordt opgehaald...")

if __name__ == "__main__":
    main()
