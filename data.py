import streamlit as st
import requests
from datetime import datetime
import pytz  # Zorg ervoor dat 'pytz' is geïnstalleerd om tijdzoneondersteuning te bieden

# Functie om historische weerdata op te halen
def fetch_historical_weather_data(lat, lon, date, start_hour, end_hour):
    api_url = (
        f"https://historical-forecast-api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={date.strftime('%Y-%m-%d')}&end_date={date.strftime('%Y-%m-%d')}"
        "&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,"
        "cloud_cover_mid,cloud_cover_high,visibility,wind_speed_80m,wind_direction_80m"
        "&daily=sunrise,sunset&timezone=Europe%2FBerlin"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van weergegevens: {e}")
        return None

# Functie om de windrichting in kompasrichting om te zetten
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

# Functie om windsnelheid om te zetten naar Beaufort-schaal
def wind_speed_to_beaufort(speed):
    if speed < 1:
        return 0
    elif speed <= 5:
        return 1
    elif speed <= 11:
        return 2
    elif speed <= 19:
        return 3
    elif speed <= 28:
        return 4
    elif speed <= 38:
        return 5
    elif speed <= 49:
        return 6
    elif speed <= 61:
        return 7
    elif speed <= 74:
        return 8
    elif speed <= 88:
        return 9
    elif speed <= 102:
        return 10
    return 11  # Orkaan

# Functie om weergegevens te tonen in een expander
def display_weather_data():
    # Haal benodigde sessiegegevens op
    lat = st.session_state.get("latitude")
    lon = st.session_state.get("longitude")
    date = st.session_state.get("selected_date")
    start_hour = st.session_state.get("start_hour", "08:00")
    end_hour = st.session_state.get("end_hour", "16:00")

    # Controleer of vereiste gegevens beschikbaar zijn
    if not (lat and lon and date):
        st.warning("Ontbrekende locatie- of datumgegevens.")
        return

    # Weerdata ophalen
    weather_data = fetch_historical_weather_data(lat, lon, date, start_hour, end_hour)
    if not weather_data:
        return

    # Zonsopgang en zonsondergang instellen
    sunrise = datetime.fromisoformat(weather_data["daily"]["sunrise"][0]).strftime("%H:%M")
    sunset = datetime.fromisoformat(weather_data["daily"]["sunset"][0]).strftime("%H:%M")
    start_hour = sunrise if start_hour == "08:00" else start_hour
    end_hour = sunset if end_hour == "16:00" else end_hour

    # Toon weergegevens in een expander
    with st.expander("Weergegevens voor deze locatie en tijdspanne"):
        hourly_data = weather_data["hourly"]
        times = hourly_data["time"]
        temperatures = hourly_data["temperature_2m"]
        precipitation = hourly_data["precipitation"]
        cloudcover = hourly_data["cloud_cover"]
        cloudcover_low = hourly_data["cloud_cover_low"]
        cloudcover_mid = hourly_data["cloud_cover_mid"]
        cloudcover_high = hourly_data["cloud_cover_high"]
        wind_speeds = hourly_data["wind_speed_80m"]
        wind_directions = hourly_data["wind_direction_80m"]

        # Tonen van weergegevens per uur binnen geselecteerde periode
        for i, time in enumerate(times):
            hour = datetime.fromisoformat(time).strftime("%H:%M")
            if start_hour <= hour <= end_hour:
                # Zet windrichting om naar NW-formaat
                wind_direction = get_wind_direction(wind_directions[i])
                # Zet windsnelheid om naar Beaufort schaal
                beaufort = wind_speed_to_beaufort(wind_speeds[i])
                
                weather_info = (
                    f"{hour}: Temp: {temperatures[i]:.1f}°C - Neerslag: {precipitation[i]:.1f} mm - "
                    f"Bewolk. Tot: {cloudcover[i]}% (L: {cloudcover_low[i]}%, M: {cloudcover_mid[i]}%, H: {cloudcover_high[i]}%) - "
                    f"Wind: {wind_direction} {beaufort} Bf"
                )
                st.code(weather_info)
