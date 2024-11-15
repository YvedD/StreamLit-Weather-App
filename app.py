import streamlit as st
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Functie om decimale coördinaten om te zetten naar graad, minuut, seconde formaat
def decimal_to_dms(degrees):
    g = int(degrees)
    minutes = (degrees - g) * 60
    m = int(minutes)
    seconds = (minutes - m) * 60
    s = round(seconds, 1)
    return g, m, s

# Functie om de coördinaten van een locatie op te halen, met landkeuze
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Functie om decimale coördinaten om te zetten naar het gewenste formaat met N/S, E/W
def format_coordinates(lat, lon):
    lat_d, lat_m, lat_s = decimal_to_dms(abs(lat))
    lon_d, lon_m, lon_s = decimal_to_dms(abs(lon))
    
    lat_direction = "N" if lat >= 0 else "S"
    lon_direction = "E" if lon >= 0 else "W"
    
    return f"{lat_d}°{lat_m}'{lat_s}\"{lat_direction} {lon_d}°{lon_m}'{lon_s}\"{lon_direction}"

# Functie om de kaart weer te geven met de locatie
def plot_location_on_map(lat, lon):
    # Creëer een kaart met de opgegeven locatie
    map = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker([lat, lon], popup=f"Locatie: {lat}, {lon}").add_to(map)
    
    # Geef de kaart weer in de Streamlit-app
    return st_folium(map, width=700, height=500)

# Streamlit app
def main():
    st.title("Plaatsselectie met Landkeuze (Eurazië)")

    # Haal de lijst van Euraziatische landen op
    countries = [
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
            # Converteer de coördinaten naar het gewenste formaat
            formatted_coordinates = format_coordinates(latitude, longitude)
            st.write(f"**Geselecteerde locatie coördinaten:**")
            st.write(formatted_coordinates)
            
            # Toon de locatie op een kaart
            plot_location_on_map(latitude, longitude)
        else:
            st.write("Locatie niet gevonden. Probeer het opnieuw.")

if __name__ == "__main__":
    main()
