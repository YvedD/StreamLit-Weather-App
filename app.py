import streamlit as st
import streamlit.components.v1 as components

# Functie om de locatie op te halen via JavaScript
def get_location():
    # JavaScript voor het ophalen van de locatie van de gebruiker
    js_code = """
    <script>
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const country = "Unknown"; // Geolocatie via JavaScript geeft geen land
            const location = {latitude: lat, longitude: lon, country: country};
            window.parent.postMessage(location, "*");
        }, function(error) {
            const location = {latitude: "Unknown", longitude: "Unknown", country: "Unknown"};
            window.parent.postMessage(location, "*");
        });
    </script>
    """
    # Voer de JavaScript uit en geef het resultaat terug
    components.html(js_code, height=0)

# Hoofdprogramma
def main():
    # Tab 1: Toon de locatiegegevens
    st.title("Locatiegegevens")
    st.subheader("Locatie van de gebruiker")

    # Haal de locatie op via JavaScript
    get_location()

    # Toon de locatiegegevens zodra ze beschikbaar zijn
    if "latitude" in st.session_state and "longitude" in st.session_state:
        st.write(f"Land: {st.session_state['country']}")
        st.write(f"Latitude: {st.session_state['latitude']}")
        st.write(f"Longitude: {st.session_state['longitude']}")
    else:
        st.write("Locatiegegevens worden opgehaald...")

# Sla de locatiegegevens op in de sessie wanneer ze beschikbaar zijn
def handle_location_message(message):
    if message.get('latitude') != "Unknown" and message.get('longitude') != "Unknown":
        st.session_state['latitude'] = message['latitude']
        st.session_state['longitude'] = message['longitude']
        st.session_state['country'] = message['country']

# Luister naar berichten van de JavaScript-executie
components.html("""
<script>
    window.addEventListener("message", function(event) {
        const location = event.data;
        window.parent.postMessage(location, "*");
    });
</script>
""", height=0)

# Start de app
if __name__ == "__main__":
    main()

