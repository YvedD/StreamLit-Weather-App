import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import streamlit as st
import io

# CSS voor marges en breedte van de uitvoer
st.markdown(
    """
    <style>
    .output-container {
        max-width: 95%; /* Verhoog de breedte van de uitvoer */
        margin: 0 auto;
        padding: 10px;
        word-wrap: break-word;
    }
    .stText, .stMarkdown {
        max-width: 95%;
    }
    .stTextInput, .stDateInput, .stTimeInput {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Functie om de coördinaten op te halen
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Location '{location_name}' not found")

# Functie om windrichting om te zetten naar Nederlandse benamingen
def wind_direction_to_dutch(direction):
    if pd.isna(direction):
        return 'Onbekend'
    directions = {
        'N': 'N', 'NNE': 'NNO', 'NE': 'NO', 'ENE': 'ONO',
        'E': 'O', 'ESE': 'OZO', 'SE': 'ZO', 'SSE': 'ZZO',
        'S': 'Z', 'SSW': 'ZZW', 'SW': 'ZW', 'WSW': 'WZW',
        'W': 'W', 'WNW': 'WNW', 'NW': 'NW', 'NNW': 'NNW'
    }
    index = round(direction / 22.5) % 16
    direction_name = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][index]
    return directions.get(direction_name, 'Onbekend')

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
def wind_speed_to_beaufort(speed_kmh):
    speed = speed_kmh / 3.6  # km/u naar m/s
    if pd.isna(speed) or speed < 0.3:
        return 0
    elif speed < 1.6:
        return 1
    elif speed < 3.4:
        return 2
    elif speed < 5.5:
        return 3
    elif speed < 8.0:
        return 4
    elif speed < 10.7:
        return 5
    elif speed < 13.8:
        return 6
    elif speed < 17.2:
        return 7
    elif speed < 20.8:
        return 8
    elif speed < 24.5:
        return 9
    elif speed < 28.2:
        return 10
    elif speed < 32.1:
        return 11
    else:
        return 12

# Functie om te bepalen welke API te gebruiken (historisch of forecast)
def get_api_url_and_params(date, latitude, longitude):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    if date == today or date == yesterday:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "apparent_temperature", "cloudcover", "cloudcover_low", "cloudcover_mid",
                       "cloudcover_high", "wind_speed_10m", "wind_direction_10m", "visibility", "precipitation"],
            "timezone": "Europe/Berlin",
            "past_days": 1 if date == yesterday else 0
        }
    else:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date,
            "end_date": date,
            "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "precipitation", "cloudcover",
                       "cloudcover_low", "cloudcover_mid", "cloudcover_high", "visibility"],
            "timezone": "Europe/Berlin"
        }

    return url, params

# Functie om de weersvoorspelling voor de komende drie dagen op te halen
def get_forecast(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
                   "visibility", "wind_speed_10m", "wind_direction_10m"],
        "timezone": "Europe/Berlin",
        "forecast_days": 3
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    hourly = data.get("hourly", {})
    times = pd.to_datetime(hourly.get("time", []))
    temperatures = np.array(hourly.get("temperature_2m", []))
    cloudcovers = np.array(hourly.get("cloud_cover", []))
    cloudcover_low = np.array(hourly.get("cloud_cover_low", []))
    cloudcover_mid = np.array(hourly.get("cloud_cover_mid", []))
    cloudcover_high = np.array(hourly.get("cloud_cover_high", []))
    wind_speeds = np.array(hourly.get("wind_speed_10m", []))
    wind_directions = np.array(hourly.get("wind_direction_10m", []))
    visibility = np.array(hourly.get("visibility", []))
    precipitation = np.array(hourly.get("precipitation", []))
    
    return times, temperatures, cloudcovers, cloudcover_low, cloudcover_mid, cloudcover_high, wind_speeds, wind_directions, visibility, precipitation

# Streamlit app
def main():
    st.title("Weather Data Viewer")

    # Maak de invoervelden breder met st.columns
    col1, col2 = st.columns([3, 3])  # Kolommen: 3 keer de breedte voor invoer, 2 keer de breedte voor andere

    with col1:
        location_name = st.text_input("Voer de naam van de plaats in:")
        date = st.date_input("Voer de datum in:").strftime("%Y-%m-%d")

    with col2:
        start_time = st.time_input("Voer de starttijd in:").strftime("%H:%M")
        end_time = st.time_input("Voer de eindtijd in:").strftime("%H:%M")

    if st.button("Gegevens ophalen"):
        try:
            # Coördinaten ophalen
            latitude, longitude = get_coordinates(location_name)
            st.write(f"Gegevens voor {location_name} (latitude: {latitude}, longitude: {longitude}) op {date}")

            # Verkrijg de juiste API URL en parameters
            url, params = get_api_url_and_params(date, latitude, longitude)

            # API-aanroep voor historisch weer
            response = requests.get(url, params=params)
            response.raise_for_status()

            # Verkrijg de gegevens uit de JSON-respons
            data = response.json()
            hourly = data.get("hourly", {})
            times = pd.to_datetime(hourly.get("time", []))
            temperatures = np.array(hourly.get("temperature_2m", []))
            cloudcovers = np.array(hourly.get("cloudcover", []))
            cloudcover_low = np.array(hourly.get("cloudcover_low", []))
            cloudcover_mid = np.array(hourly.get("cloudcover_mid", []))
            cloudcover_high = np.array(hourly.get("cloudcover_high", []))
            wind_speeds = np.array(hourly.get("wind_speed_10m", []))
            wind_directions = np.array(hourly.get("wind_direction_10m", []))
            visibility = np.array(hourly.get("visibility", []))
            precipitation = np.array(hourly.get("precipitation", []))

            # Filter de gegevens op basis van de ingevoerde tijdsperiode
            start_datetime = pd.to_datetime(f"{date} {start_time}")
            end_datetime = pd.to_datetime(f"{date} {end_time}")
            mask = (times >= start_datetime) & (times <= end_datetime)

            filtered_times = times[mask]
            filtered_temperatures = temperatures[mask]
            filtered_cloudcovers = cloudcovers[mask]
            filtered_cloudcover_low = cloudcover_low[mask]
            filtered_cloudcover_mid = cloudcover_mid[mask]
            filtered_cloudcover_high = cloudcover_high[mask]
            filtered_wind_speeds = wind_speeds[mask]
            filtered_wind_directions = wind_directions[mask]
            filtered_visibility = visibility[mask]
            filtered_precipitation = precipitation[mask]

            # Verwerk de windrichting en windkracht
            wind_direction_names = [wind_direction_to_dutch(direction) for direction in filtered_wind_directions]
            wind_beauforts = [wind_speed_to_beaufort(speed) for speed in filtered_wind_speeds]

            # Converteer zichtbaarheid van meters naar kilometers, gebruik 0 als standaard bij None
            filtered_visibility_km = [vis / 1000 if vis is not None else 0 for vis in filtered_visibility]

            # Verkrijg de 3-daagse voorspelling
            forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_cloudcover_low, forecast_cloudcover_mid, forecast_cloudcover_high, forecast_wind_speeds, forecast_wind_directions, forecast_visibility, forecast_precipitation = get_forecast(latitude, longitude)

            # Maak een container voor de uitvoer en pas de breedte aan via CSS
            with st.container():
                st.markdown('<div class="output-container">', unsafe_allow_html=True)

                # Toon de historische data
                for time, temp, cloud, cloud_low, cloud_mid, cloud_high, wind_dir, wind_bf, vis, precip in zip(
                        filtered_times, filtered_temperatures, filtered_cloudcovers, filtered_cloudcover_low,
                        filtered_cloudcover_mid, filtered_cloudcover_high, wind_direction_names, wind_beauforts,
                        filtered_visibility_km, filtered_precipitation):
                    time_str = time.strftime("%H:%M")
                    line = f"{time_str}:Temp.{temp:.1f}°C-Neersl.{precip}mm-Bew.{cloud}%(L:{cloud_low}%,M:{cloud_mid}%,H:{cloud_high}%)-{wind_dir}{wind_bf}Bf-Visi.{vis:.1f}km"
                    st.code(line)

                # Toon de voorspelling per uur voor de komende drie dagen
                st.subheader("3-daagse voorspelling per uur")
                for forecast_time, temp, cloud, cloud_low, cloud_mid, cloud_high, wind_dir, wind_bf, vis, precip in zip(
                        forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_cloudcover_low,
                        forecast_cloudcover_mid, forecast_cloudcover_high, forecast_wind_speeds, forecast_wind_directions,
                        forecast_visibility, forecast_precipitation):
                    # Haal de datum uit de tijd van de voorspelling
                    forecast_date = forecast_time.date()
                    time_str = forecast_time.strftime("%H:%M")
                    line = f"{forecast_date}: {time_str}: Temp.{temp:.1f}°C-Neersl.{precip}mm-Bew.{cloud}%(L:{cloud_low}%,M:{cloud_mid}%,H:{cloud_high}%)-{wind_dir}{wind_bf}Bf-Visi.{vis:.1f}km"
                    st.text(line)

                st.markdown('</div>', unsafe_allow_html=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Fout bij API-aanroep: {e}")
        except ValueError as e:
            st.error(f"Fout: {e}")
        except KeyError as e:
            st.error(f"Fout bij verwerken van gegevens: {e}")
        except Exception as e:
            st.error(f"Onverwachte fout: {e}")

# Voer de main functie uit
if __name__ == "__main__":
    main()
