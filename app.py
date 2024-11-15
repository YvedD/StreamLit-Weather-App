import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import streamlit as st

# Functie om coördinaten op te halen
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Locatie '{location_name}' in {country_name} niet gevonden")

# Functie om windrichting om te zetten naar Nederlandse benamingen
def wind_direction_to_dutch(direction):
    directions = {
        'N': 'N', 'NNE': 'NNO', 'NE': 'NO', 'ENE': 'ONO', 'E': 'O', 'ESE': 'OZO', 'SE': 'ZO', 'SSE': 'ZZO',
        'S': 'Z', 'SSW': 'ZZW', 'SW': 'ZW', 'WSW': 'WZW', 'W': 'W', 'WNW': 'WNW', 'NW': 'NW', 'NNW': 'NNW'
    }
    index = round(direction / 22.5) % 16
    direction_name = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][index]
    return directions.get(direction_name, 'Onbekend')

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
def wind_speed_to_beaufort(speed_kmh):
    speed = speed_kmh / 3.6
    beaufort_scale = [(0.3, 0), (1.6, 1), (3.4, 2), (5.5, 3), (8.0, 4), (10.7, 5), (13.8, 6), (17.2, 7), 
                      (20.8, 8), (24.5, 9), (28.2, 10), (32.1, 11)]
    for threshold, bf in beaufort_scale:
        if speed < threshold:
            return bf
    return 12

# Functie om de juiste API URL en parameters op te halen
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

# Functie om voorspelling voor de komende drie dagen op te halen
def get_forecast(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", 
                   "cloud_cover_high", "visibility", "wind_speed_10m", "wind_direction_10m"],
        "timezone": "Europe/Berlin",
        "forecast_days": 3
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    hourly = data.get("hourly", {})
    
    # Data inlezen
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

    countries = ['België', 'Nederland', 'Frankrijk', 'Duitsland', 'Verenigd Koninkrijk', 'Spanje', 'Italië', 
                 'Turkije', 'Rusland', 'China', 'India', 'Japan', 'Zuid-Korea', 'Saudi-Arabië', 'Iran', 'Israël', 
                 'Egypte', 'Marokko', 'Algerije', 'Tunesië', 'Libië']
    
    # Invoervelden voor locatie en land
    country_name = st.selectbox("Kies het land:", countries, index=countries.index("België"))
    location_name = st.text_input(f"Voer de naam van de plaats in in {country_name}:")
    date = st.date_input("Kies de datum voor historische gegevens:", datetime.today()).strftime("%Y-%m-%d")
    start_time = st.time_input("Starttijd:", datetime(2023, 1, 1, 12, 0)).strftime("%H:%M")
    end_time = st.time_input("Eindtijd:", datetime(2023, 1, 1, 12, 0)).strftime("%H:%M")

    if st.button("Gegevens ophalen"):
        try:
            # Coördinaten ophalen
            latitude, longitude = get_coordinates(location_name, country_name)
            st.write(f"Gegevens voor {location_name}, {country_name} (latitude: {latitude}, longitude: {longitude}) op {date}")

            # Verkrijg de juiste API URL en parameters
            url, params = get_api_url_and_params(date, latitude, longitude)

            # API-aanroep voor historische gegevens
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            hourly = data.get("hourly", {})

            # Data filteren op basis van opgegeven tijden
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
            filtered_visibility_km = [vis / 1000 if vis is not None else 0 for vis in visibility[mask]]
            filtered_precipitation = precipitation[mask]

            all_data = ""
            for time, temp, cloud, cloud_low, cloud_mid, cloud_high, wind_dir, wind_speed, vis, precip in zip(
                    filtered_times, filtered_temperatures, filtered_cloudcovers, filtered_cloudcover_low,
                    filtered_cloudcover_mid, filtered_cloudcover_high, filtered_wind_directions, filtered_wind_speeds,
                    filtered_visibility_km, filtered_precipitation):
                time_str = time.strftime("%H:%M")
                line = f"{time_str}: Temp.{temp:.1f}°C-Neersl.{precip}mm-Bew.{cloud}% (L:{cloud_low}%, M:{cloud_mid}%, H:{cloud_high}%)-{wind_direction_to_dutch(wind_dir)} {wind_speed_to_beaufort(wind_speed)}Bf-Visi.{vis:.1f}km<br>"
                all_data += line  # Voeg de <br> tag toe aan het einde van elke regel

            # Toon alle data met <br> tags voor automatische harde returns
            st.markdown(all_data, unsafe_allow_html=True)  # Gebruik markdown om <br> te verwerken als echte lijnonderbrekingen

            if st.button("Kopieer alle data"):
                st.code(all_data)

            # 3-daagse voorspelling ophalen en weergeven
            st.subheader("3-daagse voorspelling per uur")
            forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_cloudcover_low, forecast_cloudcover_mid, \
            forecast_cloudcover_high, forecast_wind_speeds, forecast_wind_directions, forecast_visibility, forecast_precipitation = get_forecast(latitude, longitude)

            forecast_text = ""
            for forecast_time, temp, cloud, cloud_low, cloud_mid, cloud_high, wind_speed, wind_dir, vis, precip in zip(
                    forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_cloudcover_low,
                    forecast_cloudcover_mid, forecast_cloudcover_high, forecast_wind_speeds, forecast_wind_directions,
                    forecast_visibility, forecast_precipitation):

                forecast_date = forecast_time.strftime("%Y-%m-%d")
                time_str = forecast_time.strftime("%H:%M")
                wind_bf = wind_speed_to_beaufort(wind_speed)
                vis_km = vis / 1000 if vis <= 100000 else 0
                line = f"{forecast_date} {time_str}: Temp.{temp:.1f}°C-Neersl.{precip}mm-Bew.{cloud}% (L:{cloud_low}%, M:{cloud_mid}%, H:{cloud_high}%)-{wind_direction_to_dutch(wind_dir)} {wind_bf}Bf-Visi.{vis_km:.1f}km<br>"
                forecast_text += line  # Voeg de <br> tag toe aan de voorspelling

            st.markdown(forecast_text, unsafe_allow_html=True)  # Gebruik markdown om de voorspelling te tonen met <br> tags

        except requests.exceptions.RequestException as e:
            st.error(f"Fout bij API-aanroep: {e}")
        except ValueError as e:
            st.error(f"Fout: {e}")
