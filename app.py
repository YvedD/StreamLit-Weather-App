import streamlit as st
from geopy.geocoders import Nominatim
import emoji

# Mapping voor landcodes naar vlaggen-emoji's
def get_flag(country_code):
    flag_offset = 127397  # Unicode offset voor vlaggen
    flag_emoji = "".join(chr(ord(char) + flag_offset) for char in country_code.upper())
    return flag_emoji

# Functie om locaties met meerdere resultaten op te halen
def get_location_choices(query):
    geolocator = Nominatim(user_agent="weather_app")
    locations = geolocator.geocode(query, exactly_one=False, addressdetails=True)
    choices = []
    if locations:
        for loc in locations:
            country_code = loc.raw.get('address', {}).get('country_code', 'unknown').upper()
            country_name = loc.raw.get('address', {}).get('country', 'Unknown')
            flag = get_flag(country_code) if len(country_code) == 2 else ""
            display_name = f"{loc.address} ({flag} {country_name})"
            choices.append((display_name, loc.latitude, loc.longitude))
    return choices

# Streamlit app
def main():
    st.title("Plaatsselectie met Landkeuze")

    # Plaatsinvoer
    location_query = st.text_input("Voer de naam van de plaats in:")

    # Zoek knoppen om keuzes weer te geven
    if st.button("Zoeken"):
        location_choices = get_location_choices(location_query)
        
        if location_choices:
            # Dropdown-menu met opties en vlaggen
            location_display_names = [choice[0] for choice in location_choices]
            selected_location = st.selectbox("Selecteer de juiste locatie:", location_display_names)
            
            # Zoek geselecteerde locatie coördinaten
            selected_data = next(((lat, lon) for name, lat, lon in location_choices if name == selected_location), None)
            
            if selected_data:
                st.write(f"**Geselecteerde locatie coördinaten:** Latitude: {selected_data[0]}, Longitude: {selected_data[1]}")
        else:
            st.write("Geen resultaten gevonden, probeer een andere zoekterm.")

if __name__ == "__main__":
    main()
