import streamlit as st
from geopy.geocoders import Nominatim
from emoji import emojize

# Functie om vlag-emoji op te halen op basis van de landcode
def get_flag_emoji(country_code):
    return emojize(f":flag_{country_code.lower()}:", use_aliases=True)

# Functie om meerdere mogelijke locaties met land en vlag op te halen
def get_coordinates_with_country(location_name):
    geolocator = Nominatim(user_agent="weather_app")
    possible_locations = geolocator.geocode(location_name, exactly_one=False, limit=5)
    if not possible_locations:
        st.error(f"Location '{location_name}' not found")
        return []

    locations_info = []
    for location in possible_locations:
        country_code = location.raw.get('address', {}).get('country_code', '').upper()
        flag = get_flag_emoji(country_code) if country_code else ""
        locations_info.append({
            "name": location_name,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "country": location.raw.get('address', {}).get('country', 'Unknown'),
            "country_code": country_code,
            "flag": flag
        })
    return locations_info

# Locatie selecteren via dropdown als er meerdere opties zijn
def select_location(locations):
    location_options = [f"{loc['flag']} {loc['name']}, {loc['country']}" for loc in locations]
    selected_option = st.selectbox("Selecteer de locatie:", location_options)
    selected_location = next(loc for loc in locations if f"{loc['flag']} {loc['name']}, {loc['country']}" == selected_option)
    return selected_location

# Hoofdprogramma
def main():
    st.title("Locatie Selectie met Vlaggen")

    location_name = st.text_input("Voer de naam van de plaats in:")
    if st.button("Zoek locatie"):
        try:
            possible_locations = get_coordinates_with_country(location_name)
            if len(possible_locations) > 1:
                st.write("Meerdere locaties gevonden. Selecteer een van de volgende:")
                selected_location = select_location(possible_locations)
            elif len(possible_locations) == 1:
                selected_location = possible_locations[0]
                st.write(f"Gekozen locatie: {selected_location['flag']} {selected_location['name']} ({selected_location['country']})")
            else:
                return  # Geen locaties gevonden

            # Weergeef coördinaten van de geselecteerde locatie
            st.write(f"GPS Coördinaten: Latitude {selected_location['latitude']}, Longitude {selected_location['longitude']}")

        except Exception as e:
            st.error(f"Fout bij locatiebepaling: {e}")

if __name__ == "__main__":
    main()
