import streamlit as st
import requests
from datetime import datetime, timedelta
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# Functie om windrichtingen om te zetten naar afkortingen
def degrees_to_direction(degrees):
    directions = ['N', 'NNO', 'NO', 'ONO', 'O', 'OZO', 'ZO', 'ZZO', 'Z', 'ZZW', 'ZW', 'WZW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
def kmh_to_beaufort(kmh):
    if kmh is None:
        return None
    elif kmh < 1:
        return 0
    elif kmh <= 5:
        return 1
    elif kmh <= 11:
        return 2
    elif kmh <= 19:
        return 3
    elif kmh <= 28:
        return 4
    elif kmh <= 38:
        return 5
    elif kmh <= 49:
        return 6
    elif kmh <= 61:
        return 7
    elif kmh <= 74:
        return 8
    elif kmh <= 88:
        return 9
    elif kmh <= 102:
        return 10
    elif kmh <= 117:
        return 11
    else:
        return 12

# Standaardwaarden
country = "België"
location_name = "Bredene"
selected_date = datetime.now() - timedelta(days=1)  # Gisteren
start_hour = "08:00"
end_hour = "16:00"

# Invoer voor locatie en datum/tijdinstellingen
st.title("Weerdata Opvragen met Locatie Weergave")
country = st.selectbox("Land:", ["België", "Nederland", "Duitsland", "Frankrijk", "Spanje", "Italië", "Portugal", 
                                 "Oostenrijk", "Zwitserland", "Zweden", "Noorwegen", "Denemarken", "Finland", 
                                 "Ierland", "Verenigd Koninkrijk", "Polen", "Tsjechië", "Slowakije", "Hongarije", 
                                 "Griekenland", "Kroatië", "Slovenië", "Litouwen", "Letland", "Estland", "Roemenië", 
                                 "Bulgarije", "Servië", "Bosnië en Herzegovina", "Montenegro", "Albanië", "IJsland", 
                                 "Luxemburg", "Andorra", "Liechtenstein", "Malta", "Cyprus"], index=0)
location_name = st.text_input("Stad/Locatie (bijv. Amsterdam):", location_name)
selected_date = st.date_input("Selecteer de datum:", selected_date.date())
hours = [f"{str(i).zfill(2)}:00" for i in range(24)]
start_hour = st.selectbox("Startuur:", hours, index=8)  # Standaard 08:00
end_hour = st.selectbox("Einduur:", hours, index=16)  # Standaard 16:00

# Functie om weerdata op te halen
def fetch_weather_data(lat, lon, start_date, end_date):
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_direction_80m&daily=sunrise,sunset&timezone=Europe%2FBerlin"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Fout bij het ophalen van weergegevens: {response.status_code}")
        return None

# Functie om de locatie op de kaart te tonen
def show_location_on_map(lat, lon, location_name):
    m = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker([lat, lon], popup=location_name).add_to(m)
    st_folium(m)

# Haal de geografische coördinaten op
geolocator = Nominatim(user_agent="weather_app")
location = geolocator.geocode(f"{location_name}, {country}")

if location:
    latitude, longitude = location.latitude, location.longitude
    
    # Toon de kaart in de tweede expander
    with st.expander("Kaart Weergave"):
        show_location_on_map(latitude, longitude, location_name)

    # Verkrijg de historische weerdata
    start_date = selected_date - timedelta(days=1)  # Gisteren
    end_date = selected_date  # Vandaag
    weather_data = fetch_weather_data(latitude, longitude, start_date.date(), end_date.date())

    if weather_data:
        # Verkrijg de gegevens van de API response
        hourly = weather_data['hourly']
        times = [datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M") for i in range(len(hourly['time']))]
        temperatures = hourly['temperature_2m']
        wind_speeds = [kmh_to_beaufort(speed) for speed in hourly['wind_speed_10m']]
        wind_directions = [degrees_to_direction(deg) if deg is not None else '' for deg in hourly['wind_direction_80m']]
        cloudcover = hourly['cloud_cover']
        cloudcover_low = hourly['cloud_cover_low']
        cloudcover_mid = hourly['cloud_cover_mid']
        cloudcover_high = hourly['cloud_cover_high']
        precipitation = hourly['precipitation']

        # Toon de historische weergegevens in de eerste expander
        with st.expander("Historische Weergegevens - Kort Overzicht"):
            for i in range(len(times)):
                weather_info = f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf"
                st.code(weather_info, language="plaintext")

        # Optioneel: Toon extra gegevens in de grafieken (indien gewenst)
        # Hier kun je de code toevoegen voor grafieken als dat nodig is
