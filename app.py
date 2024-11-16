import streamlit as st
import requests
import folium
from datetime import datetime, timedelta
from streamlit_folium import st_folium

# Functie om weergegevens op te halen
def fetch_weather_data(latitude, longitude, date):
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,
        "hourly": "temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,"
                  "visibility,wind_speed_10m,wind_direction_80m",
        "daily": "sunrise,sunset",
        "timezone": "Europe/Berlin"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Fout bij het ophalen van weergegevens")
        return None

# Functie om de weergegevens correct te verwerken en weer te geven
def process_weather_data(data, start_hour, end_hour):
    if not data:
        return None
    hourly_data = data['hourly']
    daily_data = data['daily']
    
    times = hourly_data['time']
    temperatures = hourly_data['temperature_2m']
    precipitation = hourly_data['precipitation']
    cloudcover = hourly_data['cloud_cover']
    cloudcover_low = hourly_data['cloud_cover_low']
    cloudcover_mid = hourly_data['cloud_cover_mid']
    cloudcover_high = hourly_data['cloud_cover_high']
    wind_speeds = hourly_data['wind_speed_10m']
    wind_directions = hourly_data['wind_direction_80m']
    
    # Zonsopgang en zonsondergang
    sunrise = daily_data['sunrise'][0][-5:]
    sunset = daily_data['sunset'][0][-5:]
    
    # Start en eindtijd index vinden
    start_idx = times.index(f"{selected_date}T{start_hour}:00")
    end_idx = times.index(f"{selected_date}T{end_hour}:00") + 1

    # Weerdata output opbouwen
    weather_info = []
    for i in range(start_idx, end_idx):
        info = (f"{times[i][-5:]} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - "
                f"Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - "
                f"Wind: {convert_wind_direction(wind_directions[i])} {convert_to_beaufort(wind_speeds[i])}Bf")
        weather_info.append(info)
    return sunrise, sunset, weather_info

# Functie voor windrichting conversie
def convert_wind_direction(degrees):
    directions = ['N', 'NNO', 'NO', 'ONO', 'O', 'OZO', 'ZO', 'ZZO', 'Z', 'ZZW', 'ZW', 'WZW', 'W', 'WNW', 'NW', 'NNW']
    idx = round(degrees / 22.5) % 16
    return directions[idx]

# Functie om wind in km/u om te zetten naar de Beaufort-schaal
def convert_to_beaufort(wind_speed_kmh):
    beaufort_scale = [0, 1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117]
    for i, speed in enumerate(beaufort_scale):
        if wind_speed_kmh < speed:
            return i - 1
    return 12

# Functie om een kaart te genereren
def generate_map(latitude, longitude):
    # Creëer de folium kaart
    m = folium.Map(location=[latitude, longitude], zoom_start=12, width='100%', height='100%')
    # Voeg een marker toe voor de locatie
    folium.Marker([latitude, longitude], popup="Bredene").add_to(m)
    return m

# Standaardinstellingen
default_country = "België"
latitude = 51.2389
longitude = 2.9724
selected_date = (datetime.now() - timedelta(days=1)).date()
default_start_hour = "08:00"
default_end_hour = "16:00"

# Land selecteren
country = st.selectbox("Selecteer land:", ["België", "Nederland", "Duitsland", "Frankrijk", "Luxemburg"], index=0)

# Datum, startuur en einduur instellen
selected_date = st.date_input("Datum", selected_date)
start_hour = st.selectbox("Beginuur", [f"{str(i).zfill(2)}:00" for i in range(24)], index=int(default_start_hour[:2]))
end_hour = st.selectbox("Einduur", [f"{str(i).zfill(2)}:00" for i in range(24)], index=int(default_end_hour[:2]))

# Weergegevens ophalen en verwerken
data = fetch_weather_data(latitude, longitude, selected_date)
sunrise, sunset, weather_info = process_weather_data(data, start_hour[:2], end_hour[:2])

# Toon locatie-informatie en zonsopgang/zonsopgang tijden
if sunrise and sunset:
    st.markdown(
        f"**Land:** {country}  \n"
        f"**Locatie:** Bredene ({latitude}, {longitude})  \n"
        f"**Zonsopgang:** {sunrise}  \n"
        f"**Zonsondergang:** {sunset}  \n"
    )

# Historische weergegevens in een expander
with st.expander("Weergegevens voor de gevraagde tijdsperiode", expanded=True):
    if weather_info:
        for info in weather_info:
            st.code(info, language="")

# Kaartweergave in een tweede expander
with st.expander("Kaartweergave van deze locatie", expanded=True):
    st.markdown("<style>div.stContainer {max-width: 100%;}</style>", unsafe_allow_html=True)  # Houd kaart binnen de expander
    map_folium = generate_map(latitude, longitude)
    st_folium(map_folium, width=700)  # Experimenteer met breedte om de kaart perfect te laten passen
