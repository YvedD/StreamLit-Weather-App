import streamlit as st
import datetime
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Functie om de coördinaten van de locatie op te halen
def get_coordinates(location_name, country_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(f"{location_name}, {country_name}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Functie om de coördinaten om te zetten naar graad, minuut, seconde formaat
def decimal_to_dms(degrees):
    g = int(degrees)
    minutes = (degrees - g) * 60
    m = int(minutes)
    seconds = (minutes - m) * 60
    s = round(seconds, 1)
    return g, m, s

# Functie om de windrichting om te zetten naar een tekstuele waarde
def wind_direction_to_dutch(degree):
    if degree >= 0 and degree < 22.5:
        return 'Noord'
    elif degree >= 22.5 and degree < 67.5:
        return 'Noord-Oost'
    elif degree >= 67.5 and degree < 112.5:
        return 'Oost'
    elif degree >= 112.5 and degree < 157.5:
        return 'Zuid-Oost'
    elif degree >= 157.5 and degree < 202.5:
        return 'Zuid'
    elif degree >= 202.5 and degree < 247.5:
        return 'Zuid-West'
    elif degree >= 247.5 and degree < 292.5:
        return 'West'
    elif degree >= 292.5 and degree < 337.5:
        return 'Noord-West'
    else:
        return 'Noord'

# Functie om de windsnelheid om te zetten naar km/h
def convert_wind_speed_to_kmh(speed_mps):
    return round(speed_mps * 3.6, 1)

# Functie om de zichtbaarheid om te zetten naar kilometers met 1 decimaal
def convert_visibility_to_km(visibility_m):
    return round(visibility_m / 1000, 1)

# Functie om historische gegevens op te halen van de Open-Meteo API
def fetch_weather_data(latitude, longitude, start_time, end_time):
    historical_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_time.strftime('%Y-%m-%d')}&end_date={end_time.strftime('%Y-%m-%d')}&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_direction_10m&timezone=Europe%2FBerlin"
    response = requests.get(historical_url)
    data = response.json()

    historical_data = []
    if 'hourly' in data:
        for i in range(len(data['hourly']['temperature_2m'])):
            timestamp = start_time + datetime.timedelta(hours=i)
            temp = data['hourly']['temperature_2m'][i]
            cloud = data['hourly']['cloud_cover'][i]
            precip = data['hourly']['precipitation'][i]
            wind_speed = convert_wind_speed_to_kmh(data['hourly']['wind_speed_10m'][i])
            wind_dir = wind_direction_to_dutch(data['hourly']['wind_direction_10m'][i])
            vis = convert_visibility_to_km(data['hourly']['visibility'][i])
            
            historical_data.append({
                "timestamp": timestamp,
                "temp": temp,
                "cloud": cloud,
                "precip": precip,
                "wind_dir": wind_dir,
                "wind_speed": wind_speed,
                "vis": vis
            })
    return historical_data

# Functie om weersvoorspellingen op te halen van de Open-Meteo API
def fetch_forecast_data(latitude, longitude):
    forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m_max,temperature_2m_min,precipitation_sum,cloudcover_mean,wind_speed_10m_max,wind_direction_10m_max,visibility_mean&timezone=Europe%2FBerlin&forecast_days=3"
    response = requests.get(forecast_url)
    data = response.json()

    forecast_data = []
    if 'hourly' in data:
        for i in range(len(data['hourly']['temperature_2m_max'])):
            forecast_data.append({
                "hour": f"Uur {i+1}",
                "temp_max": data['hourly']['temperature_2m_max'][i],
                "temp_min": data['hourly']['temperature_2m_min'][i],
                "precip": data['hourly']['precipitation_sum'][i],
                "cloud": data['hourly']['cloudcover_mean'][i],
                "wind_speed": convert_wind_speed_to_kmh(data['hourly']['wind_speed_10m_max'][i]),
                "wind_dir": wind_direction_to_dutch(data['hourly']['wind_direction_10m_max'][i]),
                "vis": convert_visibility_to_km(data['hourly']['visibility_mean'][i])
            })
    return forecast_data

# Functie om de locatie op een kaart te tonen
def plot_location_on_map(lat, lon, zoom_start=10):
    map = folium.Map(location=[lat, lon], zoom_start=zoom_start)
    folium.Marker([lat, lon], popup=f"Locatie: {lat}, {lon}").add_to(map)
    return map

# Gebruik van session_state om gegevens en status te behouden
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = None
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = None
if 'location' not in st.session_state:
    st.session_state.location = ""

# Hoofdapplicatie
def main():
    st.title("Weerapplicatie voor Locaties")

    # Invoervelden voor land, locatie, datum, beginuur en einduur
    country = st.selectbox("Kies een land", ["Belgium", "Nederland", "Frankrijk", "Duitsland", "Luxemburg"], index=0)
    location_name = st.text_input("Voer de naam van de plaats in:")
    date = st.date_input("Kies een datum", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())
    
    # Invoervelden voor begin- en einduur
    start_hour = st.selectbox("Kies een beginuur", list(range(0, 24)), index=8)  # Standaard 08:00
    end_hour = st.selectbox("Kies een einduur", list(range(0, 24)), index=15)   # Standaard 15:00

    # Bereken het start- en eindtijdstip
    start_time = datetime.datetime.combine(date, datetime.time(start_hour, 0))
    end_time = datetime.datetime.combine(date, datetime.time(end_hour, 0))

    # Opzoeken knop
    if st.button("Opzoeken"):
        if location_name:
            # Haal de coördinaten op van de ingevoerde locatie
            latitude, longitude = get_coordinates(location_name, country)
            if latitude and longitude:
                st.session_state.coordinates = (latitude, longitude)

                # Haal de historische gegevens en voorspellingen op
                st.session_state.historical_data = fetch_weather_data(latitude, longitude, start_time, end_time)
                st.session_state.forecast_data = fetch_forecast_data(latitude, longitude)

                st.session_state.location = location_name
            else:
                st.error("Locatie niet gevonden.")

    # Het tonen van de expanders
    if st.session_state.historical_data:
        with st.expander("Weatherdata", expanded=True):
            st.write("Historische gegevens:")
            st.write("Kopieer per regel")
            for data in st.session_state.historical_data:
                st.write(f"{data['timestamp']}: Temp: {data['temp']}°C, Cloud: {data['cloud']}%, Precip: {data['precip']}mm, Wind: {data['wind_dir']} {data['wind_speed']} km/h, Vis: {data['vis']} km")

    if st.session_state.coordinates:
        with st.expander("Map of location", expanded=True):
            map = plot_location_on_map(st.session_state.coordinates[0], st.session_state.coordinates[1])
            st_folium(map, width=700, height=500)

    if st.session_state.forecast_data:
        with st.expander("3 day's Forecast for this location", expanded=True):
            st.write("Weersvoorspellingen voor de komende drie dagen:")
            for data in st.session_state.forecast_data:
                st.write(f"{data['hour']}: Temp Max: {data['temp_max']}°C, Temp Min: {data['temp_min']}°C, Precip: {data['precip']}mm, Cloud: {data['cloud']}%, Wind: {data['wind_speed']} km/h, Windrichting: {data['wind_dir']}, Vis: {data['vis']} km")

if __name__ == "__main__":
    main()
