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
start_hour = st.selectbox("Startuur:", hours, index=8)  # begin om 08:00
end_hour = st.selectbox("Einduur:", hours, index=16)  # eind om 16:00

# Dummy string voor initiële waarde, totdat gebruiker iets wijzigt
dummy_string = f"{country} - {location_name} - {selected_date} - {start_hour} tot {end_hour}"

# Wanneer gebruiker gegevens wijzigt, vervang de dummy string
if country != "België" or location_name != "Bredene" or selected_date != (datetime.now().date() - timedelta(days=1)) or start_hour != "08:00" or end_hour != "16:00":
    dummy_string = f"{country} - {location_name} - {selected_date} - {start_hour} tot {end_hour}"

# Toon de dummy string totdat de gebruiker wijzigingen aanbrengt
st.write(f"Gegevens voor: {dummy_string}")

# Initialiseer geolocator
geolocator = Nominatim(user_agent="weather_app")
location = geolocator.geocode(f"{location_name}, {country}")

if location:
    latitude, longitude = location.latitude, location.longitude

    # Expander voor kaartweergave
    with st.expander("Kaartweergave van locatie"):
        # Zorg ervoor dat de locatie correct wordt weergegeven
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        folium.Marker([latitude, longitude], popup=f"{location_name}, {country}").add_to(m)
        
        # Geef de kaart weer in Streamlit
        st_folium(m, width=700, height=500)

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
    historical_data = fetch_weather_data(latitude, longitude, selected_date - timedelta(days=8), selected_date)

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

        # Expander voor kort overzicht van historische gegevens
        with st.expander("Historische Gegevens - Kort Overzicht"):
            for i in range(len(times)):
                if start_datetime <= times[i] <= end_datetime:
                    weather_info = f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf"
                    st.code(weather_info)

        # Grafieken voor de historische gegevens
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

            # Bewolking en Zichtbaarheid Plot
            fig, ax2 = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=filtered_times, y=filtered_cloudcover, color="orange", ax=ax2, label="Bewolking (%)")
            sns.lineplot(x=filtered_times, y=filtered_precipitation, color="purple", ax=ax2, label="Neerslag (mm)")
            ax2.set_xlabel("Datum en Tijd")
            ax2.set_ylabel("Bewolking en Neerslag")
            ax2.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

            st.pyplot(fig)
