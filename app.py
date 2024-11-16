import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from datetime import datetime, timedelta
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt

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

# Europese landenlijst voor dropdown
european_countries = [
    "België", "Nederland", "Duitsland", "Frankrijk", "Spanje", "Italië", "Portugal", 
    "Oostenrijk", "Zwitserland", "Zweden", "Noorwegen", "Denemarken", "Finland", 
    "Ierland", "Verenigd Koninkrijk", "Polen", "Tsjechië", "Slowakije", "Hongarije", 
    "Griekenland", "Kroatië", "Slovenië", "Litouwen", "Letland", "Estland", "Roemenië", 
    "Bulgarije", "Servië", "Bosnië en Herzegovina", "Montenegro", "Albanië", "IJsland", 
    "Luxemburg", "Andorra", "Liechtenstein", "Malta", "Cyprus"
]

# Invoer voor locatie en datum/tijdinstellingen
st.title("Weerdata Opvragen met Locatie Weergave")
country = st.selectbox("Land:", european_countries, index=european_countries.index("België"))
location_name = st.text_input("Stad/Locatie (bijv. Bredene):", "Bredene")
selected_date = st.date_input("Selecteer de datum:", datetime.now().date() - timedelta(days=1))

# Volle uren selecties
hours = [f"{str(i).zfill(2)}:00" for i in range(24)]
start_hour = st.selectbox("Startuur:", hours, index=6)  # Startuur is 06:00 als standaard
end_hour = st.selectbox("Einduur:", hours, index=20)  # Einduur is 20:00 als standaard

# Dummy string voor initiële weergave (indien geen wijzigingen)
default_location = "België - Bredene - Gisteren - 08:00 tot 16:00"
weather_info_display = st.empty()
weather_info_display.text(f"Standaard weerinformatie: {default_location}")

# Functie om weerdata op te halen
def fetch_weather_data(lat, lon, start, end):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start}&end_date={end}"
        f"&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,cloudcover,cloudcover_low,cloudcover_mid,cloudcover_high,precipitation,visibility"
        f"&timezone=Europe/Berlin"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Fout bij het ophalen van weergegevens: {response.status_code}")
        return None

# Knop om weergegevens op te vragen
if country or location_name or selected_date or start_hour or end_hour:
    # Update de weergegevens zodra de gebruiker wijzigingen aanbrengt
    weather_info_display.text(f"Gegevens opgevraagd voor: {country} - {location_name} - {selected_date} - {start_hour} tot {end_hour}")

# Functie voor het ophalen van locatie-coördinaten
def get_coordinates(location_name, country):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country}")
    if location:
        return location.latitude, location.longitude
    else:
        st.error(f"Kan locatie '{location_name}, {country}' niet vinden.")
        return None, None

# Haal de coördinaten op voor de opgegeven locatie
latitude, longitude = get_coordinates(location_name, country)

# Verwerk de gegevens als coördinaten beschikbaar zijn
if latitude and longitude:
    start_datetime = datetime.combine(selected_date, datetime.strptime(start_hour, "%H:%M").time())
    end_datetime = datetime.combine(selected_date, datetime.strptime(end_hour, "%H:%M").time())

    # Haal weergegevens op voor de opgegeven periode
    historical_data = fetch_weather_data(latitude, longitude, start_datetime.date(), end_datetime.date())
    
    # Display voor de expander als gegevens beschikbaar zijn
    if historical_data:
        with st.expander("Historische Weergegevens - Kort Overzicht"):
            hourly = historical_data['hourly']
            times = [datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M") for i in range(len(hourly['time']))]
            temperatures = hourly['temperature_2m']
            wind_speeds = [kmh_to_beaufort(speed) for speed in hourly['wind_speed_10m']]
            wind_directions = [degrees_to_direction(deg) if deg is not None else '' for deg in hourly['wind_direction_10m']]
            cloudcover = hourly.get('cloudcover', [])
            cloudcover_low = hourly.get('cloudcover_low', [])
            cloudcover_mid = hourly.get('cloudcover_mid', [])
            cloudcover_high = hourly.get('cloudcover_high', [])
            precipitation = hourly.get('precipitation', [])
            
            # Filteren op geselecteerde datum en tijdsbereik
            for i in range(len(times)):
                if start_datetime <= times[i] <= end_datetime:
                    if temperatures[i] is not None and precipitation[i] is not None and cloudcover[i] is not None:
                        weather_info = f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf"
                        st.code(weather_info)
        
        # Grafieken
        with st.expander("Historische Weergegevens - Grafieken"):
            sns.set(style="whitegrid")
            filtered_times = [time for time in times if start_datetime <= time <= end_datetime]
            filtered_temperatures = [temperatures[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]
            filtered_wind_speeds = [wind_speeds[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]
            filtered_cloudcover = [cloudcover[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]
            filtered_precipitation = [precipitation[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]

            # Temperatuur en Windsnelheid Plot
            fig, ax1 = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=filtered_times, y=filtered_temperatures, color="blue", ax=ax1, label="Temperatuur (°C)")
            sns.lineplot(x=filtered_times, y=filtered_wind_speeds, color="green", ax=ax1, label="Windsnelheid (Beaufort)")
            ax1.set_xlabel("Datum en Tijd")
            ax1.set_ylabel("Temperatuur / Windsnelheid")
            ax1.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

            # Bewolking en Neerslag Plot
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=filtered_times, y=filtered_cloudcover, color="orange", ax=ax2, label="Bewolking (%)")
            sns.lineplot(x=filtered_times, y=filtered_precipitation, color="purple", ax=ax2, label="Neerslag (mm)")
            ax2.set_xlabel("Datum en Tijd")
            ax2.set_ylabel("Bewolking / Neerslag")
            ax2.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

            # Weergeven van de grafieken
            st.pyplot(fig)
            st.pyplot(fig2)
    else:
        st.error("Er zijn geen historische weergegevens gevonden.")
