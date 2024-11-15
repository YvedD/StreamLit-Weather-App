import streamlit as st
from geopy.geocoders import Nominatim

# Mapping voor landcodes naar vlaggen-emoji's
def get_flag(country_code):
    flag_offset = 127397  # Unicode offset voor vlaggen
    flag_emoji = "".join(chr(ord(char) + flag_offset) for char in country_code.upper())
    return flag_emoji

# Functie om de coördinaten van een locatie op te halen, met landkeuze
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Lijst met landen voor de dropdown (en vlaggen)
countries = [
    ("België", "BE"),
    ("Nederland", "NL"),
    ("Duitsland", "DE"),
    ("Frankrijk", "FR"),
    ("Verenigd Koninkrijk", "GB"),
    ("Spanje", "ES"),
    ("Italië", "IT"),
    ("Luxemburg", "LU")
]

# Streamlit app
def main():
    st.title("Plaatsselectie met Landkeuze")

    # Plaatsinvoer en landenkeuze
    col1, col2 = st.columns([3, 1])
    
    with col1:
        location_name = st.text_input("Voer de naam van de plaats in:")
    
    with col2:
        country_name = st.selectbox("Kies een land:", [country[0] for country in countries], index=0)
    
    # Zoek naar de coördinaten van de opgegeven locatie en land
    if st.button("Zoeken"):
        latitude, longitude = get_coordinates(location_name, country_name)
        
        if latitude is not None and longitude is not None:
            st.write(f"**Geselecteerde locatie coördinaten:**")
            st.write(f"Latitude: {latitude}, Longitude: {longitude}")
        else:
            st.write("Locatie niet gevonden. Probeer het opnieuw.")

if __name__ == "__main__":
    main()
