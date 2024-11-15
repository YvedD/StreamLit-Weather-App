import streamlit as st
from geopy.geocoders import Nominatim
import folium
from datetime import datetime
from streamlit_folium import st_folium
import requests

# Functie om decimale coördinaten om te zetten naar graad, minuut, seconde formaat
def decimal_to_dms(degrees):
    g = int(degrees)
    minutes = (degrees - g) * 60
    m = int(minutes)
    seconds = (minutes - m) * 60
    s = round(seconds, 1)
    return g, m, s

# Functie om de coördinaten van een locatie op te halen, met landkeuze
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Functie om de coördinaten naar het gewenste formaat om te zetten
def format_coordinates(lat, lon):
    lat_d, lat_m, lat_s = decimal_to_dms(abs(lat))
    lon_d, lon_m, lon_s = decimal_to_dms(abs(lon))
    
    lat_direction = "N" if lat >= 0 else "S"
    lon_direction = "E" if lon >= 0 else "W"
    
    return f"{lat_d}°{lat_m}'{lat_s}\"{lat_direction} {lon_d}°{lon_m}'{lon_s}\"{lon_direction}"

# Functie om de kaart weer te geven met de locatie
def plot_location_on_map(lat, lon, zoom_start=2):
    map = folium.Map(location=[lat, lon], zoom_start=zoom_start)
    folium.Marker([lat, lon], popup=f"Locatie: {lat}, {lon}").add_to(map)
    return map

# Functie voor het ophalen van historische data (dummy)
def get_weather_data(start_date, end_date, lat, lon):
    # Voorbeeld: genereren van dummy data
    times = [datetime.now() for _ in range(5)]
    temperatures = [15.0, 16.5, 17.2, 15.8, 14.0]
    cloudcovers = [10, 20, 50, 30, 40]
    wind_speeds = [5, 6, 7, 4, 5]
    wind_directions = [90, 180, 270, 0, 45]
    visibility = [10000, 12000, 8000, 10000, 9000]
    precipitation = [0.0, 1.0, 0.0, 0.5, 0.0]
    
    return times, temperatures, cloudcovers, wind_speeds, wind_directions, visibility, precipitation

# Functie voor het ophalen van voorspellingen (dummy)
def get_forecast(lat, lon):
    # Voorbeeld: genereren van dummy forecast data
    forecast_times = [datetime.now() for _ in range(3)]
    forecast_temperatures = [16.5, 17.2, 18.0]
    forecast_cloudcovers = [30, 40, 50]
    forecast_wind_speeds = [4, 5, 6]
    forecast_wind_directions = [90, 180, 270]
    forecast_visibility = [10000, 12000, 10000]
    forecast_precipitation = [0.0, 0.2, 0.0]
    
    return forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_wind_speeds, forecast_wind_directions, forecast_visibility, forecast_precipitation

# Functie om de windrichting om te zetten naar Nederlands
def wind_direction_to_dutch(direction):
    directions = {
        'N': 'N', 'NNE': 'NNO', 'NE': 'NO', 'ENE': 'ONO', 'E': 'O', 'ESE': 'OZO', 'SE': 'ZO', 'SSE': 'ZZO',
        'S': 'Z', 'SSW': 'ZZW', 'SW': 'ZW', 'WSW': 'WZW', 'W': 'W', 'WNW': 'WNW', 'NW': 'NW', 'NNW': 'NNW'
    }
    index = round(direction / 22.5) % 16
    direction_name = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][index]
    return directions.get(direction_name, 'Onbekend')

# Streamlit app
def main():
    st.title("Weather Data Viewer")

    # Invoer: locatie, land, start en stopdatum
    country_name = st.selectbox("Kies een land:", ["Belgium", "Netherlands", "Germany", "France", "Luxembourg", "Spain", "Italy"])
    location_name = st.text_input("Voer de naam van de plaats in:")
    start_date = st.date_input("Kies een startdatum")
    end_date = st.date_input("Kies een einddatum")

    # Wanneer op de knop wordt gedrukt
    if st.button("Gegevens opzoeken"):
        if location_name and country_name:
            latitude, longitude = get_coordinates(location_name, country_name)
            
            if latitude and longitude:
                # Toon de coördinaten van de locatie
                st.write("GPS Coördinaten:", format_coordinates(latitude, longitude))

                # Toon de kaart van de locatie
                st.subheader("Kaart van de locatie")
                map = plot_location_on_map(latitude, longitude)
                st_folium(map, width=700, height=500)

                # Haal de historische data op
                times, temperatures, cloudcovers, wind_speeds, wind_directions, visibility, precipitation = get_weather_data(start_date, end_date, latitude, longitude)

                # Toon de historische data in een expander
                with st.expander("Historische gegevens", expanded=True):
                    all_data = ""
                    for time, temp, cloud, wind_dir, wind_speed, vis, precip in zip(times, temperatures, cloudcovers, wind_directions, wind_speeds, visibility, precipitation):
                        time_str = time.strftime("%H:%M")
                        wind_direction = wind_direction_to_dutch(wind_dir)
                        line = f"{time_str}: Temp. {temp:.1f}°C, Bew. {cloud}%, Neersl. {precip}mm, Wind {wind_direction} {wind_speed:.1f} km/h, Vis. {vis/1000:.1f} km"
                        all_data += line + "\n"
                    st.code(all_data)  # Kopieerbare historische gegevens

                # Toon de voorspellingen in een expander
                forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_wind_speeds, forecast_wind_directions, forecast_visibility, forecast_precipitation = get_forecast(latitude, longitude)
                with st.expander("3-daagse voorspellingen", expanded=True):
                    forecast_text = ""
                    for forecast_time, temp, cloud, wind_speed, wind_dir, vis, precip in zip(forecast_times, forecast_temperatures, forecast_cloudcovers, forecast_wind_speeds, forecast_wind_directions, forecast_visibility, forecast_precipitation):
                        forecast_date = forecast_time.strftime("%Y-%m-%d")
                        time_str = forecast_time.strftime("%H:%M")
                        wind_direction = wind_direction_to_dutch(wind_dir)
                        line = f"{forecast_date} {time_str}: Temp. {temp:.1f}°C, Bew. {cloud}%, Neersl. {precip}mm, Wind {wind_direction} {wind_speed:.1f} km/h, Vis. {vis/1000:.1f} km"
                        forecast_text += line + "\n"
                    st.text(forecast_text)  # Niet kopieerbaar voor voorspellingen

            else:
                st.error("Locatie niet gevonden.")
        else:
            st.error("Vul een locatie en land in om gegevens op te zoeken.")

if __name__ == "__main__":
    main()
