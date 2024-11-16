import streamlit as st
from geopy.geocoders import Nominatim
import requests
import folium
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Functie om windrichtingen om te zetten naar afkortingen
def degrees_to_direction(degrees):
    directions = ['N', 'NNO', 'NO', 'ONO', 'O', 'OZO', 'ZO', 'ZZO', 'Z', 'ZZW', 'ZW', 'WZW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
def kmh_to_beaufort(kmh):
    if kmh < 1:
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

# Streamlit-setup
st.title("Weerdata Opvragen")

# Invoervelden voor locatie en datumbereik
location_name = st.text_input("Voer een locatie in (bijv. Amsterdam)")
start_date = st.date_input("Startdatum", value=datetime.today() - timedelta(days=8))
end_date = start_date + timedelta(days=1)

# Tijdsselectie voor volle uren
hours = [f"{hour:02d}:00" for hour in range(24)]
start_hour = st.selectbox("Begin uur", hours)
end_hour = st.selectbox("Eind uur", hours)

# Weerdata ophalen bij klik op knop
if st.button("Haal Weerdata Op"):
    if not location_name:
        st.error("Vul alstublieft een locatie in.")
    else:
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(location_name)

        if location is None:
            st.error(f"Locatie '{location_name}' niet gevonden.")
        else:
            latitude, longitude = location.latitude, location.longitude

            # Open-Meteo API endpoint
            url = (
                f"https://archive-api.open-meteo.com/v1/archive"
                f"?latitude={latitude}&longitude={longitude}"
                f"&start_date={start_date}&end_date={end_date}"
                f"&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,cloudcover,precipitation,visibility"
                f"&timezone=Europe/Berlin"
            )

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    hourly = data['hourly']

                    # Weergegevens extraheren
                    hours_range = range(len(hourly['temperature_2m']))
                    temperatures = hourly['temperature_2m']
                    wind_speeds = [kmh_to_beaufort(speed) for speed in hourly['wind_speed_10m']]
                    wind_directions = hourly['wind_direction_10m']
                    cloudcover = hourly['cloudcover']
                    precipitation = hourly['precipitation']
                    visibility = hourly['visibility']

                    # Plotting met Seaborn en Matplotlib
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.lineplot(x=hours_range, y=temperatures, label='Temperatuur (°C)', ax=ax)
                    sns.lineplot(x=hours_range, y=wind_speeds, label='Windsnelheid (Beaufort)', ax=ax)
                    sns.lineplot(x=hours_range, y=cloudcover, label='Bewolkingsgraad (%)', ax=ax)
                    sns.lineplot(x=hours_range, y=visibility, label='Zichtbaarheid (km)', ax=ax)
                    sns.lineplot(x=hours_range, y=precipitation, label='Neerslag (mm)', ax=ax)

                    ax.set_title(f"Weerdata voor {location_name} van {start_date} tot {end_date}")
                    ax.set_xlabel("Uur van de dag")
                    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
                    plt.xticks(hours_range, hours, rotation=45)

                    st.pyplot(fig)

                    # Kaart met marker
                    m = folium.Map(location=[latitude, longitude], zoom_start=10)
                    folium.Marker(
                        [latitude, longitude],
                        popup=f"{location_name} (Lat: {latitude}, Lon: {longitude})",
                        icon=folium.Icon(color="red")
                    ).add_to(m)

                    # Kaart weergeven in Streamlit
                    st_folium(m, width=700, height=500)
                else:
                    st.error(f"Fout bij ophalen van gegevens: {response.status_code}")
            except Exception as e:
                st.error(f"Er is een fout opgetreden: {str(e)}")
