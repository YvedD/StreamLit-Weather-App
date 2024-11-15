import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import streamlit as st

# Lijst van Europese landen
european_countries = [
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belgium", "Bosnia and Herzegovina", "Bulgaria", 
    "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany", 
    "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania", 
    "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", 
    "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", 
    "Sweden", "Switzerland", "Ukraine", "United Kingdom"
]

# Functie om coördinaten op te halen
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Location '{location_name}, {country_name}' not found")

# Functie om windrichting om te zetten naar Nederlandse benamingen
def wind_direction_to_dutch(direction):
    directions = {
        'N': 'N', 'NNE': 'NNO', 'NE': 'NO', 'ENE': 'ONO', 'E': 'O', 'ESE': 'OZO', 'SE': 'ZO', 'SSE': 'ZZO',
        'S': 'Z', 'SSW': 'ZZW', 'SW': 'ZW', 'WSW': 'WZW', 'W': 'W', 'WNW': 'WNW', 'NW': 'NW', 'NNW': 'NNW'
    }
    index = round(direction / 22.5) % 16
    direction_name = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][index]
    return directions.get(direction_name, 'Onbekend')

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

# Functie om de weergegevens voor de komende 3 dagen op te halen
def get_weather_data(date, latitude, longitude):
    url, params = get_api_url_and_params(date, latitude, longitude)
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    hourly = data.get("hourly", {})

    times = pd.to_datetime(hourly.get("time", []))
    temperatures = np.array(hourly.get("temperature_2m", []))
    cloudcovers = np.array(hourly.get("cloudcover", []))
    wind_speeds = np.array(hourly.get("wind_speed_10m", []))
    wind_directions = np.array(hourly.get("wind_direction_10m", []))
    visibility = np.array(hourly.get("visibility", []))
    precipitation = np.array(hourly.get("precipitation", []))
    
    return times, temperatures, cloudcovers, wind_speeds, wind_directions, visibility, precipitation

# Functie om voorspellingen voor de komende drie dagen op te halen
def get_forecast(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "cloudcover", "wind_speed_10m", "wind_direction_10m", "visibility"],
        "timezone": "Europe/Berlin"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    hourly = data.get("hourly", {})
    
    # Data inlezen
    times = pd.to_datetime(hourly.get("time", []))
    temperatures = np.array(hourly.get("temperature_2m", []))
    cloudcovers = np.array(hourly.get("cloudcover", []))
    wind_speeds = np.array(hourly.get("wind_speed_10m", []))
    wind_directions = np.array(hourly.get("wind_direction_10m", []))
    visibility = np.array(hourly.get("visibility", []))
    precipitation = np.array(hourly.get("precipitation", []))
    
    return times, temperatures, cloudcovers, wind_speeds, wind_directions, visibility, precipitation

# Streamlit app
def main():
    st.title("Weather Data Viewer")

    # Landkeuze
    country_name = st.selectbox("Kies een Europees land:", european_countries)

    # Invoerveld voor plaatsnaam
    location_name = st.text_input(f"Voer de naam van de plaats in in {country_name}:")

    # Datum en tijd invoeren
    date = st.date_input("Voer de datum in:").strftime("%Y-%m-%d")
    start_time = st.time_input("Voer de starttijd in:").strftime("%H:%M")
    end_time = st.time_input("Voer de eindtijd in:").strftime("%H:%M")

    # Knop om de gegevens op te halen
    if st.button("Gegevens ophalen"):
        # Pop-up met de boodschap "Hello World"
        st.markdown("""
            <div id="popup" style="position: fixed; top: 20%; left: 50%; transform: translate(-50%, -20%);
                        padding: 15px; background-color: rgba(0, 0, 0, 0.8); color: white;
                        border-radius: 10px; z-index: 9999; width: 300px; height: 200px; overflow: auto; cursor: move;">
                <h2>Hello World!</h2>
                <p>Je hebt zojuist op de knop gedrukt en nu worden je weergegevens opgehaald...</p>
            </div>
            <style>
                #popup {
                    cursor: move;
                    position: absolute;
                    top: 100px;
                    left: 50%;
                    transform: translate(-50%, 0);
                    width: 300px;
                    padding: 10px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5);
                }
            </style>
            <script>
                var popup = document.getElementById("popup");
                popup.onmousedown = function(event) {
                    var shiftX = event.clientX - popup.getBoundingClientRect().left;
                    var shiftY = event.clientY - popup.getBoundingClientRect().top;

                    function moveAt(pageX, pageY) {
                        popup.style.left = pageX - shiftX + 'px';
                        popup.style.top = pageY - shiftY + 'px';
                    }

                    moveAt(event.pageX, event.pageY);

                    document.onmousemove = function(event) {
                        moveAt(event.pageX, event.pageY);
                    };

                    popup.onmouseup = function() {
                        document.onmousemove = null;
                        popup.onmouseup = null;
                    };
                };

                popup.ondragstart = function() {
                    return false;
                };
            </script>
        """, unsafe_allow_html=True)

        try:
            # Coördinaten ophalen
            latitude, longitude = get_coordinates(location_name, country_name)
            st.write(f"Gegevens voor {location_name}, {country_name} (latitude: {latitude}, longitude: {longitude}) op {date}")

            # Weerdata ophalen
            times, temperatures, cloudcovers, wind_speeds, wind_directions, visibility, precipitation = get_weather_data(date, latitude, longitude)

            # Filter de tijdsdata op basis van start- en eindtijd
            start_datetime = pd.to_datetime(f"{date} {start_time}")
            end_datetime = pd.to_datetime(f"{date} {end_time}")
            mask = (times >= start_datetime) & (times <= end_datetime)

            filtered_times = times[mask]
            filtered_temperatures = temperatures[mask]
            filtered_cloudcovers = cloudcovers[mask]
            filtered_wind_speeds = wind_speeds[mask]
            filtered_wind_directions = wind_directions[mask]
            filtered_visibility = visibility[mask]
            filtered_precipitation = precipitation[mask]

            for time, temp, cloud, wind_dir, wind_speed, vis, precip in zip(
                    filtered_times, filtered_temperatures, filtered_cloudcovers, filtered_wind_directions, 
                    filtered_wind_speeds, filtered_visibility, filtered_precipitation):
                time_str = time.strftime("%H:%M")
                st.write(f"{time_str}: Temp. {temp:.1f}°C, Bew. {cloud}%, Neersl. {precip}mm, Wind {wind_direction_to_dutch(wind_dir)} {wind_speed:.1f} km/h, Vis. {vis/1000:.1f} km")
            
            # 3-daagse voorspelling ophalen en weergeven
            forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_wind_speeds, forecast_wind_directions, forecast_visibility, forecast_precipitation = get_forecast(latitude, longitude)

            st.subheader("3-daagse voorspelling per uur")
            for forecast_time, temp, cloud, wind_speed, wind_dir, vis, precip in zip(
                    forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_wind_speeds,
                    forecast_wind_directions, forecast_visibility, forecast_precipitation):
                forecast_date = forecast_time.strftime("%Y-%m-%d")
                time_str = forecast_time.strftime("%H:%M")
                st.write(f"{forecast_date} {time_str}: Temp. {temp:.1f}°C, Bew. {cloud}%, Neersl. {precip}mm, Wind {wind_direction_to_dutch(wind_dir)} {wind_speed:.1f} km/h, Vis. {vis/1000:.1f} km")

        except requests.exceptions.RequestException as e:
            st.error(f"Fout bij API-aanroep: {e}")
        except ValueError as e:
            st.error(f"Fout: {e}")

# Voer de main functie uit
if __name__ == "__main__":
    main()
