import streamlit as st
import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta

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
def wind_speed_to_beaufort(speed):
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

# Streamlit interface
def main():
    # Gebruikersinterface
    st.title("Weersvoorspelling voor Jouw Locatie")
    
    location_name = st.text_input("Voer de naam van de plaats in:", "Amsterdam")
    date = st.text_input("Selecteer de datum:", "")
    start_time = st.text_input("Starttijd", "HH:MM")
    end_time = st.text_input("Eindtijd", "HH:MM")

    # Voer de hoofdlogica uit als de gebruiker alle velden heeft ingevuld
    if location_name and date and start_time and end_time:
        try:
            # Haal de coördinaten op
            latitude, longitude = get_coordinates(location_name)
            st.write(f"Gegevens ophalen voor {location_name} (latitude: {latitude}, longitude: {longitude}) op {date}")

            # Verkrijg de juiste API URL en parameters
            url, params = get_api_url_and_params(str(date), latitude, longitude)

            # API-aanroep
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

            # Converteer zichtbaarheid van meters naar kilometers
            filtered_visibility_km = [vis / 1000 if vis is not None else 0 for vis in filtered_visibility]

            # Formatteer neerslag als 0.00mm
            filtered_precipitation = [f"{precip:.1f}" if precip is not None else "0.0" for precip in filtered_precipitation]

            # Resultaten tonen in de Streamlit-app
            st.write(f"### Weersgegevens voor {location_name} op {date} van {start_time} tot {end_time}:")

            weather_data = {
                "Tijd": filtered_times,
                "Temperatuur (°C)": filtered_temperatures,
                "Neerslag (mm)": filtered_precipitation,
                "Bewolking (%)": filtered_cloudcovers,
                "Luchtvochtigheid laag (%)": filtered_cloudcover_low,
                "Luchtvochtigheid middel (%)": filtered_cloudcover_mid,
                "Luchtvochtigheid hoog (%)": filtered_cloudcover_high,
                "Windrichting": wind_direction_names,
                "Windkracht (Bf)": wind_beauforts,
                "Zichtbaarheid (km)": filtered_visibility_km,
            }

            weather_df = pd.DataFrame(weather_data)
            st.table(weather_df)

        except requests.exceptions.RequestException as e:
            st.error(f"Fout bij API-aanroep: {e}")
        except ValueError as e:
            st.error(f"Fout: {e}")
        except KeyError as e:
            st.error(f"Fout bij verwerken van gegevens: {e}")
        except Exception as e:
            st.error(f"Onverwachte fout: {e}")

if __name__ == "__main__":
    main()
