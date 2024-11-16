import streamlit as st
import requests
import datetime
from datetime import timedelta
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import seaborn as sns

# Functie om geografische locatie (latitude, longitude) op te halen
def get_lat_lon(location):
    geolocator = Nominatim(user_agent="weather-app")
    location = geolocator.geocode(location)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Functie om windrichting om te zetten naar de Nederlandse naam
def degrees_to_direction(degrees):
    if degrees is None:
        return ''
    directions = ['N', 'NNO', 'NO', 'ONO', 'O', 'OZO', 'ZO', 'ZZO', 'Z', 'ZZW', 'ZW', 'WZW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]

# Functie om snelheid in km/u om te zetten naar de Beaufort-schaal
def kmh_to_beaufort(kmh):
    if kmh < 1:
        return 0
    elif 1 <= kmh <= 5:
        return 1
    elif 6 <= kmh <= 11:
        return 2
    elif 12 <= kmh <= 19:
        return 3
    elif 20 <= kmh <= 28:
        return 4
    elif 29 <= kmh <= 38:
        return 5
    elif 39 <= kmh <= 49:
        return 6
    elif 50 <= kmh <= 61:
        return 7
    elif 62 <= kmh <= 74:
        return 8
    elif 75 <= kmh <= 88:
        return 9
    elif 89 <= kmh <= 102:
        return 10
    elif 103 <= kmh <= 117:
        return 11
    else:
        return 12

# Haal historische weergegevens op
def fetch_weather_data(lat, lon, start_date, end_date):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,cloudcover,cloudcover_low,cloudcover_mid,cloudcover_high,precipitation,visibility"
        f"&timezone=Europe/Berlin"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Fout bij het ophalen van weergegevens: {response.status_code}")
        return None

# Standaard locatie instellen voor België - Bredene
default_location = "Bredene, België"
latitude, longitude = get_lat_lon(default_location)

if latitude is None or longitude is None:
    st.error("Kan geen locatie vinden. Zorg ervoor dat je locatie correct is.")
else:
    # Huidige datum instellen
    selected_date = datetime.datetime.now() - timedelta(days=1)

    # Invoer voor de gebruiker
    start_hour = "08:00"
    end_hour = "16:00"

    # Verkrijg de historische gegevens
    historical_data = fetch_weather_data(latitude, longitude, selected_date - timedelta(days=8), selected_date)

    if historical_data:
        hourly = historical_data['hourly']
        times = [datetime.datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M") for i in range(len(hourly['time']))]
        temperatures = hourly.get('temperature_2m', [])
        wind_speeds = [kmh_to_beaufort(speed) for speed in hourly.get('wind_speed_10m', [])]
        wind_directions = [degrees_to_direction(deg) if deg is not None else '' for deg in hourly.get('wind_direction_10m', [])]
        cloudcover = hourly.get('cloudcover', [])
        cloudcover_low = hourly.get('cloudcover_low', [])
        cloudcover_mid = hourly.get('cloudcover_mid', [])
        cloudcover_high = hourly.get('cloudcover_high', [])
        precipitation = hourly.get('precipitation', [])

        # Filteren op geselecteerde datum en tijdsbereik
        start_datetime = datetime.datetime.combine(selected_date, datetime.datetime.strptime(start_hour, "%H:%M").time())
        end_datetime = datetime.datetime.combine(selected_date, datetime.datetime.strptime(end_hour, "%H:%M").time())

        # Historische gegevens tonen
        with st.expander("Historische Gegevens - Kort Overzicht"):
            for i in range(len(times)):
                if start_datetime <= times[i] <= end_datetime:
                    if (i < len(temperatures) and i < len(precipitation) and
                        i < len(cloudcover) and i < len(cloudcover_low) and 
                        i < len(cloudcover_mid) and i < len(cloudcover_high) and
                        i < len(wind_directions) and i < len(wind_speeds)):
                        weather_info = f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf"
                        st.code(weather_info)
                    else:
                        st.warning(f"Gegevens ontbreken voor tijdstip {times[i].strftime('%H:%M')}")

        # Grafieken tonen
        with st.expander("Historische Weergegevens - Grafieken"):
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

        # Kaart met marker
        with st.expander("Locatie op Kaart"):
            import folium
            m = folium.Map(location=[latitude, longitude], zoom_start=12)
            folium.Marker([latitude, longitude], popup=default_location).add_to(m)

            # Voeg de kaart toe aan de Streamlit app
            st.map(m)
