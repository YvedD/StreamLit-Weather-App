import streamlit as st
import requests
import math

# Functie om de windrichting om te zetten naar de juiste kompasrichting
def wind_direction_to_compass(degrees):
    directions = [
        "North", "North-North-East", "North-East", "East-North-East", "East", 
        "East-South-East", "South-East", "South-South-East", "South", "South-South-West", 
        "South-West", "West-South-West", "West", "West-North-West", "North-West", "North-North-West"
    ]
    index = int((degrees + 11.25) / 22.5)
    return directions[index % 16]

# Functie om de windsnelheid om te zetten naar de Beaufort schaal
def wind_speed_to_beaufort(speed_kmh):
    if speed_kmh < 1:
        return 0
    elif 1 <= speed_kmh < 6:
        return 1
    elif 6 <= speed_kmh < 12:
        return 2
    elif 12 <= speed_kmh < 19:
        return 3
    elif 19 <= speed_kmh < 29:
        return 4
    elif 29 <= speed_kmh < 39:
        return 5
    elif 39 <= speed_kmh < 50:
        return 6
    elif 50 <= speed_kmh < 61:
        return 7
    elif 61 <= speed_kmh < 75:
        return 8
    elif 75 <= speed_kmh < 89:
        return 9
    elif 89 <= speed_kmh < 103:
        return 10
    elif 103 <= speed_kmh < 118:
        return 11
    else:
        return 12

# Functie om de Open-Meteo API aan te roepen en data op te halen
def fetch_weather_data(latitude, longitude, start_date, end_date, timezone):
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_80m,wind_direction_80m&timezone={timezone}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# Functie om de gegevens mooi weer te geven in de expander
def show_data_expander():
    country = st.session_state.get("country", "Unknown")
    location = st.session_state.get("location", "Unknown")
    selected_date = st.session_state.get("selected_date", "Unknown")
    start_hour = st.session_state.get("start_hour", "Unknown")
    end_hour = st.session_state.get("end_hour", "Unknown")
    latitude = st.session_state.get("latitude", 0.0)
    longitude = st.session_state.get("longitude", 0.0)
    timezone = st.session_state.get("timezone", "Europe/Berlin")
    sunrise = st.session_state.get("sunrise", "Unknown")
    sunset = st.session_state.get("sunset", "Unknown")

    with st.expander("Location Data", expanded=True):
        st.write(f"**Location:** {location}")
        st.write(f"**Country:** {country}")
        st.write(f"**Date Selected:** {selected_date}")
        st.write(f"**Latitude:** {latitude}")
        st.write(f"**Longitude:** {longitude}")
        st.write(f"**Sunrise:** {sunrise}")
        st.write(f"**Sunset:** {sunset}")
        formatted_coords = f"{abs(latitude):.2f}°{'N' if latitude >= 0 else 'S'} {abs(longitude):.2f}°{'E' if longitude >= 0 else 'W'}"
        st.write(f"**Formatted Coordinates:** {formatted_coords}")

    weather_data = fetch_weather_data(latitude, longitude, selected_date, selected_date, timezone)

    if weather_data:
        with st.expander("Weather Data", expanded=True):
            hourly = weather_data['hourly']
            st.write(f"### Weather Data for {selected_date}")

            for i, time in enumerate(hourly['time']):
                st.write(f"#### Time: {time}")
                temperature = hourly['temperature_2m'][i]
                precipitation = hourly['precipitation'][i]
                cloud_cover = hourly['cloud_cover'][i]
                wind_speed = hourly['wind_speed_80m'][i]
                wind_direction = hourly['wind_direction_80m'][i]
                visibility_meters = hourly['visibility'][i]

                # Zet de zichtbaarheid om naar kilometers en rond af naar een geheel getal
                visibility_km = round(visibility_meters / 1000)
                
                wind_direction_compass = wind_direction_to_compass(wind_direction)
                wind_beaufort = wind_speed_to_beaufort(wind_speed)

                st.write(f"**Temperature:** {temperature}°C")
                st.write(f"**Precipitation:** {precipitation} mm")
                st.write(f"**Cloud Cover:** {cloud_cover}%")
                st.write(f"**Visibility:** {visibility_km} km")
                st.write(f"**Wind Speed:** {wind_speed} km/h")
                st.write(f"**Wind Direction:** {wind_direction_compass} ({wind_direction}°)")
                st.write(f"**Wind Beaufort:** {wind_beaufort} Bf")
                st.write("---")
