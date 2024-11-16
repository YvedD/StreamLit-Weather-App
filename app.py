import streamlit as st
from datetime import datetime, timedelta
import requests
import folium
from streamlit_folium import st_folium

# Standaardwaarden voor locatie en datum
default_country = "België"
default_location = "Bredene"
latitude = 51.2389
longitude = 2.9724
selected_date = datetime.now() - timedelta(days=1)

# Open-Meteo API URL voor historische gegevens
api_url = (
    f"https://historical-forecast-api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}&longitude={longitude}"
    f"&start_date={selected_date.strftime('%Y-%m-%d')}&end_date={selected_date.strftime('%Y-%m-%d')}"
    "&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,"
    "cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_direction_80m"
    "&daily=sunrise,sunset&timezone=Europe%2FBerlin"
)

# Ophalen weergegevens
def fetch_weather_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van weergegevens: {e}")
        return None

weather_data = fetch_weather_data(api_url)

# Begin- en einduur instellen op basis van zonsopgang en zonsondergang
sunrise = None
sunset = None
if weather_data:
    sunrise = datetime.fromisoformat(weather_data["daily"]["sunrise"][0]).strftime("%H:%M")
    sunset = datetime.fromisoformat(weather_data["daily"]["sunset"][0]).strftime("%H:%M")
    start_hour = sunrise
    end_hour = sunset
else:
    start_hour = "08:00"
    end_hour = "16:00"

# Gebruikersinterface voor land, locatie, datum, begin- en eindtijd
st.title("Historische Weergegevens - Open-Meteo API")
st.write(f"**Land**: {default_country}, **Locatie**: {default_location} ({latitude}, {longitude})")
st.write(f"**Zonsopgang**: {sunrise}, **Zonsondergang**: {sunset}")

# Expander met kopieerbare weergegevens per uur
with st.expander("Historische Weergegevens - Kort Overzicht"):
    if weather_data:
        hourly_data = weather_data["hourly"]
        times = hourly_data["time"]
        temperatures = hourly_data["temperature_2m"]
        precipitation = hourly_data["precipitation"]
        cloudcover = hourly_data["cloud_cover"]
        cloudcover_low = hourly_data["cloud_cover_low"]
        cloudcover_mid = hourly_data["cloud_cover_mid"]
        cloudcover_high = hourly_data["cloud_cover_high"]
        wind_speeds = hourly_data["wind_speed_10m"]
        wind_directions = hourly_data["wind_direction_80m"]

        # Tonen van weergegevens voor elk uur binnen de geselecteerde periode
        for i, time in enumerate(times):
            hour = datetime.fromisoformat(time).strftime("%H:%M")
            if start_hour <= hour <= end_hour:
                weather_info = (
                    f"{hour} : Temp.: {temperatures[i]:.1f} °C - "
                    f"Neersl.: {precipitation[i]:.1f} mm - "
                    f"Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, "
                    f"MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - "
                    f"Wind: {wind_directions[i]}° {wind_speeds[i]} km/u"
                )
                st.code(weather_info, language="")

# Expander voor kaartweergave met marker
with st.expander("Kaartweergave"):
    map_folium = folium.Map(location=[latitude, longitude], zoom_start=12)
    folium.Marker([latitude, longitude], popup=f"{default_location} ({latitude}, {longitude})").add_to(map_folium)
    st_folium(map_folium, width=700)
