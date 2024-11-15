import streamlit as st
import pycountry
from geopy.geocoders import Nominatim

# Functie om de coördinaten van een locatie op te halen, met landkeuze
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Functie om landen in Eurazië op te halen (Europa, Azië en Nabije Oosten)
def get_eurasian_countries():
    # Lijst van landen in Eurazië (gebaseerd op de geografische regio)
    eurasian_countries = [
        "Albania", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium", "Bosnia and Herzegovina",
        "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "Georgia",
        "Germany", "Greece", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Israel",
        "Italy", "Kazakhstan", "Kosovo", "Kuwait", "Kyrgyzstan", "Latvia", "Liechtenstein", "Lithuania",
        "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Morocco", "Nepal", "Netherlands", "Norway",
        "Oman", "Pakistan", "Palestinian Territories", "Poland", "Portugal", "Qatar", "Romania", "Russia",
        "San Marino", "Saudi Arabia", "Serbia", "Singapore", "Slovakia", "Slovenia", "South Korea", "Spain",
        "Sri Lanka", "Syria", "Tajikistan", "Thailand", "Turkey", "Turkmenistan", "Ukraine", "United Kingdom",
        "Uzbekistan", "Vietnam", "Yemen"
    ]
    return eurasian_countries

# Streamlit app
def main():
    st.title("Plaatsselectie met Landkeuze (Eurazië)")

    # Haal de lijst van Euraziatische landen op
    countries = get_eurasian_countries()

    # Plaatsinvoer en landenkeuze
    col1, col2 = st.columns([3, 1])
    
    with col1:
        location_name = st.text_input("Voer de naam van de plaats in:")
    
    with col2:
        country_name = st.selectbox("Kies een land:", countries, index=0)
    
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
