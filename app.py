import streamlit as st
from datetime import datetime, timedelta
import requests
import folium
from streamlit_folium import st_folium

# Functie om weergegevens op te halen op basis van locatie en datum
def fetch_weather_data(lat, lon, date, start_hour, end_hour):
    api_url = (
        f"https://historical-forecast-api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={date.strftime('%Y-%m-%d')}&end_date={date.strftime('%Y-%m-%d')}"
        "&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,"
        "cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_direction_80m"
        "&daily=sunrise,sunset&timezone=Europe%2FBerlin"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van weergegevens: {e}")
        return None

# Functie om GPS-coördinaten op te halen via geocoding service
def get_gps_coordinates(location):
    api_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1&limit=1"
    try:
        response = requests.get(api_url)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error("Locatie niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van GPS-coördinaten: {e}")
        return None, None

# Functie om windrichting om te zetten naar richtingen zoals NW
def get_wind_direction(degrees):
    directions = [
        ("N", 0), ("NNO", 22.5), ("NO", 45), ("ONO", 67.5),
        ("O", 90), ("ZO", 112.5), ("Z", 135), ("ZZO", 157.5),
        ("ZSW", 180), ("SW", 202.5), ("WZW", 225), ("W", 247.5),
        ("WNW", 270), ("NW", 292.5), ("NNW", 315)
    ]
    for direction, angle in directions:
        if degrees < angle:
            return direction
    return "N"  # Default if no match

# Functie om windkracht om te rekenen naar de Beaufortschaal
def wind_speed_to_beaufort(speed_kmh):
    # Beaufortschaal berekening
    thresholds = [
        1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117, float("inf")
    ]
    for beaufort, threshold in enumerate(thresholds):
        if speed_kmh <= threshold:
            return beaufort
    return 12  # Return maximum Beaufort

# Functie om de voorspelling voor morgen op te halen
def fetch_tomorrow_forecast(lat, lon):
    api_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation,cloud_cover"
        "&daily=sunrise,sunset&timezone=Europe%2FBerlin&forecast_days=2"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van de weersvoorspelling: {e}")
        return None

# Standaardwaarden voor locatie en datum
default_country = "België"
default_location = "Bredene"
latitude = 51.2389
longitude = 2.9724
selected_date = datetime.now().date() - timedelta(days=1)

# Formulier voor het invoeren van gegevens
country = st.selectbox("Selecteer land", ["België"], index=0)  # Aanpassing voor slechts één land
location = st.text_input("Locatie", value=default_location)
selected_date = st.date_input("Datum", value=selected_date)
start_hour = st.selectbox("Beginuur", [f"{hour:02d}:00" for hour in range(24)], index=8)
end_hour = st.selectbox("Einduur", [f"{hour:02d}:00" for hour in range(24)], index=16)

# Weergeven van geselecteerde locatie- en tijdgegevens
st.write(f"**Land**: {country}, **Locatie**: {location} ({latitude}, {longitude})")
st.write(f"**Zonsopgang**: {sunrise}, **Zonsondergang**: {sunset}")

# Verkrijg de GPS-coördinaten voor de nieuwe locatie
latitude, longitude = get_gps_coordinates(location)

# Weerdata ophalen
weather_data = fetch_weather_data(latitude, longitude, selected_date, start_hour, end_hour)

# Expander met kopieerbare weergegevens per uur met uitgebreide informatie
with st.expander("Weergegevens voor deze locatie en tijdspanne"):
    if weather_data:
        hourly_data = weather_data["hourly"]
        times = hourly_data["time"]
        temperatures = hourly_data["temperature_2m"]
        precipitation = hourly_data["precipitation"]
        cloudcover = hourly_data["cloud_cover"]
        cloudcover_low = hourly_data["cloud_cover_low"]
        cloudcover_mid = hourly_data["cloud_cover_mid"]
        cloudcover_high = hourly_data["cloud_cover_high"]
        visibility = hourly_data["visibility"]
        wind_speeds = hourly_data["wind_speed_10m"]
        wind_directions = hourly_data["wind_direction_80m"]

        # Toon gegevens met st.code per uur binnen geselecteerde periode
        for i, time in enumerate(times):
            hour = datetime.fromisoformat(time).strftime("%H:%M")
            if start_hour <= hour <= end_hour:
                weather_info = (
                    f"{hour}: Temp: {temperatures[i]:.1f}°C, "
                    f"Neerslag: {precipitation[i]:.1f}mm, Bewolking: {cloudcover[i]}%, "
                    f"Low: {cloudcover_low[i]}%, Mid: {cloudcover_mid[i]}%, High: {cloudcover_high[i]}%, "
                    f"Windrichting: {get_wind_direction(wind_directions[i])}, "
                    f"Windkracht (Beaufort): {wind_speed_to_beaufort(wind_speeds[i])}, "
                    f"Zichtbaarheid: {visibility[i] / 1000:.1f} km"
                )
                st.code(weather_info, language="text")
    else:
        st.write("Geen weergegevens gevonden voor de geselecteerde locatie en tijd.")

# Expander voor kaartweergave
with st.expander("Kaartweergave van locatie"):
    # Toon kaart met markering op de gekozen locatie
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], tooltip=location).add_to(m)
    st_folium(m, width=700, height=500)

# Expander voor weersvoorspelling voor morgen (enkel relevant als datum vandaag is)
with st.expander("Voorspelling voor morgen"):
    if selected_date == datetime.now().date():
        forecast_data = fetch_tomorrow_forecast(latitude, longitude)
        if forecast_data:
            hourly_data = forecast_data["hourly"]
            tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%A %d %B %Y")
            st.write(f"**{tomorrow}:**")
            
            # Toon voorspelling op specifieke tijdstippen: ochtend, middag, avond, nacht
            time_indices = {"06:00": "Ochtend", "12:00": "Middag", "18:00": "Avond", "00:00": "Nacht"}
            for j, time in enumerate(hourly_data["time"]):
                forecast_hour = datetime.fromisoformat(time).strftime("%H:%M")
                if forecast_hour in time_indices:
                    period = time_indices[forecast_hour]
                    temperature = hourly_data["temperature_2m"][j]
                    precipitation = hourly_data["precipitation"][j]
                    cloudcover = hourly_data["cloud_cover"][j]
                    st.write(
                        f"{period}: Temp: {temperature}°C - Neerslag: {precipitation}mm - Bewolking: {cloudcover}%"
                    )
    else:
        st.write("Voorspelling beschikbaar voor morgen indien datum gelijk is aan vandaag.")
