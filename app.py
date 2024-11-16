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
location_name = st.text_input("Stad/Locatie (bijv. Amsterdam):", "Bredene")
selected_date = st.date_input("Selecteer de datum:", datetime.now().date())

# Volle uren selecties
hours = [f"{str(i).zfill(2)}:00" for i in range(24)]
start_hour = st.selectbox("Startuur:", hours, index=0)
end_hour = st.selectbox("Einduur:", hours, index=23)

# Bereken de start- en einddatums voor historische gegevens (8 dagen terug)
start_date = selected_date - timedelta(days=8)
end_date = selected_date

# Initialiseer geolocator
geolocator = Nominatim(user_agent="weather_app")
location = geolocator.geocode(f"{location_name}, {country}")

if location:
    latitude, longitude = location.latitude, location.longitude

    # Maak een nieuwe expander voor de historische weergegevens op één rij
    with st.expander("Historische Weergegevens - Kort Overzicht"):
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

        # Historische gegevens ophalen
        historical_data = fetch_weather_data(latitude, longitude, start_date, end_date)
        if historical_data:
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
            start_datetime = datetime.combine(selected_date, datetime.strptime(start_hour, "%H:%M").time())
            end_datetime = datetime.combine(selected_date, datetime.strptime(end_hour, "%H:%M").time())

            # Tekstueel overzicht per uur op één rij
            for i in range(len(times)):
                if start_datetime <= times[i] <= end_datetime:
                    st.write(f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf")
                    
    # Locatie Overzicht
    with st.expander("Locatie Overzicht"):
        # Kaart met marker
        st.header("Locatie op kaart")
        map_obj = folium.Map(location=[latitude, longitude], zoom_start=6)
        folium.Marker([latitude, longitude], tooltip=location_name, icon=folium.Icon(color="red")).add_to(map_obj)
        st_folium(map_obj, width=700, height=400)

    # Historische gegevens grafieken
    with st.expander("Historische Weergegevens - Grafieken"):
        if historical_data:
            sns.set(style="whitegrid")
            
            # Filter alleen tijden binnen de geselecteerde datum en tijdsbereik voor grafieken
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

            # Bewolking en Zichtbaarheid Plot
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=filtered_times, y=filtered_cloudcover, color="gray", ax=ax2, label="Bewolkingsgraad (%)")
            sns.lineplot(x=filtered_times, y=filtered_precipitation, color="purple", ax=ax2, label="Neerslag (mm)")
            ax2.set_xlabel("Datum en Tijd")
            ax2.set_ylabel("Bewolkingsgraad / Neerslag")
            ax2.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

            st.pyplot(fig)
            st.pyplot(fig2)
