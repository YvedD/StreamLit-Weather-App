import streamlit as st
import streamlit.components.v1 as components

# Functie om de locatie op te halen via JavaScript
def get_location():
    # JavaScript code om de geolocatie op te halen
    js_code = """
    <script>
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const location = {latitude: lat, longitude: lon};
            window.parent.postMessage(location, "*");
        }, function(error) {
            const location = {latitude: "Unknown", longitude: "Unknown"};
            window.parent.postMessage(location, "*");
        });
    </script>
    """
    # Voer de JavaScript uit in een HTML component
    components.html(js_code, height=0)

# Functie om locatie te verwerken en op te slaan in de session_state
def handle_location_message(location):
    if location.get('latitude') != "Unknown" and location.get('longitude') != "Unknown":
        st.session_state['latitude'] = location['latitude']
        st.session_state['longitude'] = location['longitude']
    else:
        st.session_state['latitude'] = None
        st.session_state['longitude'] = None

# Hoofdprogramma
def main():
    st.title("Locatie ophalen")
    st.subheader("Locatie van de gebruiker")

    # Haal de locatie op via JavaScript
    get_location()

    # Toon de locatiegegevens zodra ze beschikbaar zijn
    if "latitude" in st.session_state and "longitude" in st.session_state:
        if st.session_state['latitude'] is not None and st.session_state['longitude'] is not None:
            st.write(f"Latitude: {st.session_state['latitude']}")
            st.write(f"Longitude: {st.session_state['longitude']}")
        else:
            st.write("Kon de locatie niet ophalen.")
    else:
        st.write("Locatiegegevens worden opgehaald...")

# Luister naar berichten van de JavaScript-executie en verwerk ze
components.html("""
<script>
    window.addEventListener("message", function(event) {
        const location = event.data;
        const message = {latitude: location.latitude, longitude: location.longitude};
        window.parent.postMessage(message, "*");
    });
</script>
""", height=0)

if __name__ == "__main__":
    main()
