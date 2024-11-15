import streamlit as st
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime, timedelta

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
def plot_location_on_map(lat, lon, zoom_start=2):
    # Creëer een kaart met een basis zoomniveau voor de wereld
    map = folium.Map(location=[0, 0], zoom_start=zoom_start)  # begin met de wereldkaart
    
    if lat and lon:
        # Inzoomen naar de specifieke locatie
        map = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup=f"Locatie: {lat}, {lon}").add_to(map)
    
    # Geef de kaart weer in de Streamlit-app
    return map

# Functie om het actuele weer op te halen met de OpenWeatherMap API
def get_current_weather(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data.get("cod") == 200:
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        return temp, description, humidity
    return None, None, None

# Functie om de weersvoorspellingen voor de komende 3 dagen op te halen
def get_weather_forecast(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    forecasts = []
    if data.get("cod") == "200":
        for forecast in data["list"][:3]:  # Get the first 3 forecasts (next 3 days)
            date = datetime.utcfromtimestamp(forecast["dt"]).strftime('%Y-%m-%d')
            temp = forecast["main"]["temp"]
            description = forecast["weather"][0]["description"]
            forecasts.append((date, temp, description))
    return forecasts

# Functie om historische weersgegevens op te halen
def get_historical_weather(lat, lon, start_date, end_date, api_key):
    url = f"http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={start_date}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    historical_data = []
    if data.get("cod") == 200:
        historical_data.append((start_date, data["current"]["temp"], data["current"]["weather"][0]["description"]))
    return historical_data

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

    # Voeg de zoekknop toe
    api_key = "YOUR_API_KEY"  # Voeg je OpenWeatherMap API-sleutel hier in

    if st.button("Zoek"):
        # Toon de GPS-gegevens in tekstformaat onder de invoervelden
        if location_name and country_name:
            st.write("### GPS Coördinaten (indien gevonden):")
            
            latitude, longitude = get_coordinates(location_name, country_name)
            
            if latitude is not None and longitude is not None:
                # Converteer de coördinaten naar het gewenste formaat
                formatted_coordinates = format_coordinates(latitude, longitude)
                st.write(f"**Locatie**: {location_name}, {country_name}")
                st.write(f"**Coördinaten**: {formatted_coordinates}")
                
                # Toon de huidige weersomstandigheden
                temp, description, humidity = get_current_weather(latitude, longitude, api_key)
                if temp is not None:
                    st.write(f"**Huidige temperatuur**: {temp}°C")
                    st.write(f"**Weerbeschrijving**: {description}")
                    st.write(f"**Luchtvochtigheid**: {humidity}%")
                
                # Toon de weersvoorspellingen
                forecasts = get_weather_forecast(latitude, longitude, api_key)
                st.write("### Weersvoorspelling voor de komende 3 dagen:")
                for date, temp, description in forecasts:
                    st.write(f"{date}: {temp}°C, {description}")
                
                # Toon historische gegevens
                start_date = int((datetime.now() - timedelta(days=1)).timestamp())
                historical_data = get_historical_weather(latitude, longitude, start_date, start_date, api_key)
                st.write("### Historisch Weer (1 dag geleden):")
                for date, temp, description in historical_data:
                    st.write(f"{date}: {temp}°C, {description}")
                
                # Popup om de kaart weer te geven met de gevonden locatie
                with st.expander("Bekijk de kaart van de locatie", expanded=True):
                    map = plot_location_on_map(latitude, longitude, zoom_start=10)
                    st_folium(map, width=700, height=500)
            else:
                st.write("Locatie niet gevonden. Probeer het opnieuw.")

if __name__ == "__main__":
    main()
