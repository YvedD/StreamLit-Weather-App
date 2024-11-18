import requests
import streamlit as st
from datetime import datetime, timedelta  # Voeg timedelta toe voor het verwerken van datums

# Functie om historische weergegevens op te halen via Open-Meteo API
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
        data = response.json()
        return data
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van weergegevens: {e}")
        return None

# Functie om windrichting te converteren van graden naar windrichtingen
def get_wind_direction(degrees, language="Nederlands"):
    directions_dutch = [
        ("N", 0), ("NNO", 22.5), ("NO", 45), ("ONO", 67.5),
        ("O", 90), ("OZO", 112.5), ("ZO", 135), ("ZZO", 157.5),
        ("Z", 180), ("ZZW", 202.5), ("ZW", 225), ("WZW", 247.5),
        ("W", 270), ("WNW", 292.5), ("NW", 315), ("NNW", 337.5)
    ]
    
    for direction, angle in directions_dutch:
        if degrees < angle:
            return direction
    return directions_dutch[0][0]  # Default if no match, return the first direction

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
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

# Functie om de zichtbaarheid om te rekenen naar kilometers en af te ronden op 0.5 km
def convert_visibility(visibility_meters):
    visibility_km = visibility_meters / 1000  # Converteer naar kilometers
    return round(visibility_km * 2) / 2  # Afgerond op 0.5 km

# Functie om de API-gegevens te tonen in een expander in de Streamlit UI
def show_data_expander():
    # Haal de taalkeuze op uit de session_state
    language = st.session_state.get("language", "Nederlands")  # Standaard Nederlands

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
    start_hour = sunrise if start_hour == "00:00" else start_hour
    end_hour = sunset if end_hour == "00:00" else end_hour

    # Toon weergegevens in een expander
    with st.expander("Weergegevens voor deze locatie en tijdspanne"):
        # Voeg een keuzemenu toe voor weergave-optie
        display_option = st.radio("Kies weergavemethode:", ("Per uur (afzonderlijk)", "Volledig blok (alles in één)"))
        
        # Informatie ophalen uit de data
        hourly_data = weather_data["hourly"]
        times = hourly_data["time"]
        temperatures = hourly_data["temperature_2m"]
        precipitation = hourly_data["precipitation"]
        cloudcover = hourly_data["cloud_cover"]
        cloudcover_low = hourly_data["cloud_cover_low"]
        cloudcover_mid = hourly_data["cloud_cover_mid"]
        cloudcover_high = hourly_data["cloud_cover_high"]
        visibility = hourly_data["visibility"]
        wind_speeds = hourly_data["wind_speed_80m"]
        wind_directions = hourly_data["wind_direction_80m"]
        
        # Lijst voor het verzamelen van de weergegevensregels
        weather_info_lines = []
        
        # Verwerken van weergegevens per uur binnen geselecteerde periode
        for i, time in enumerate(times):
            hour = datetime.fromisoformat(time).strftime("%H:%M")
            if start_hour <= hour <= end_hour:
                # Zet windrichting om naar de juiste vertaling op basis van de taalkeuze
                wind_direction = get_wind_direction(wind_directions[i], language)
                # Zet windsnelheid om naar Beaufort schaal
                beaufort = wind_speed_to_beaufort(wind_speeds[i])
                # Zet zichtbaarheid om naar kilometers en afgerond op 0.5 km
                visibility_km = convert_visibility(visibility[i])
                
                # Weergegevens formatten
                weather_info = (
                    f"{hour}|Temp:{temperatures[i]:.1f}°C|Precip:{precipitation[i]:.1f} mm|"
                    f"Clouds:{cloudcover[i]}%(L:{cloudcover_low[i]}%,M:{cloudcover_mid[i]}%,H:{cloudcover_high[i]}%)|"
                    f"Wnd:{wind_direction} {beaufort}Bf|Vis:{visibility_km} km"
                )
                
                # Toevoegen aan de lijst van weergegevensregels
                weather_info_lines.append(weather_info)

        # Conditie op basis van de weergavekeuze
        if display_option == "Per uur (afzonderlijk)":
            # Toon elke regel afzonderlijk
            for line in weather_info_lines:
                st.code(line)
        else:
            # Toon alle regels in één blok
            st.code("\n".join(weather_info_lines))

