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

# Lijst van Europese landen voor de dropdown
european_countries = [
    "Albanië", "Andorra", "Armenië", "Oostenrijk", "Azerbeidzjan", "Wit-Rusland", "België", "Bosnië en Herzegovina",
    "Bulgarije", "Kroatië", "Cyprus", "Tsjechië", "Denemarken", "Estland", "Finland", "Frankrijk", "Georgië",
    "Duitsland", "Griekenland", "Hongarije", "IJsland", "Ierland", "Italië", "Kazachstan", "Kosovo", "Letland",
    "Liechtenstein", "Litouwen", "Luxemburg", "Malta", "Moldavië", "Monaco", "Montenegro", "Nederland", "Noorwegen",
    "Polen", "Portugal", "Roemenië", "Rusland", "San Marino", "Servië", "Slowakije", "Slovenië", "Spanje", "Zweden",
    "Zwitserland", "Turkije", "Oekraïne", "Verenigd Koninkrijk", "Vaticaanstad", "Noord-Macedonië"
]

# Functie om de windrichting om te zetten naar de "NW" notatie
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

# Functie om de windsnelheid om te zetten naar de Beaufort-schaal
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

# Functie om de 3-daagse weersvoorspelling op te halen
def fetch_3_day_forecast(lat, lon):
    api_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,"
        "visibility,wind_speed_10m,wind_direction_10m&daily=sunrise,sunset&timezone=Europe%2FBerlin&forecast_days=3"
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
selected_date = datetime.now() - timedelta(days=1)

# Titel en instructies
st.title("Historische Weergegevens - Open-Meteo API")

# Formulier voor het invoeren van gegevens
country = st.selectbox("Selecteer land", european_countries, index=european_countries.index(default_country))
location = st.text_input("Locatie", value=default_location)
selected_date = st.date_input("Datum", value=selected_date)
start_hour = st.selectbox("Beginuur", [f"{hour:02d}:00" for hour in range(24)], index=8)
end_hour = st.selectbox("Einduur", [f"{hour:02d}:00" for hour in range(24)], index=16)

# Verkrijg de GPS-coördinaten voor de nieuwe locatie
latitude, longitude = get_gps_coordinates(location)

# Weerdata ophalen
weather_data = fetch_weather_data(latitude, longitude, selected_date, start_hour, end_hour)

# Begin- en einduur op basis van zonsopgang en zonsondergang
if weather_data:
    sunrise = datetime.fromisoformat(weather_data["daily"]["sunrise"][0]).strftime("%H:%M")
    sunset = datetime.fromisoformat(weather_data["daily"]["sunset"][0]).strftime("%H:%M")
    start_hour = sunrise if start_hour == "08:00" else start_hour
    end_hour = sunset if end_hour == "16:00" else end_hour
else:
    sunrise, sunset = "08:00", "16:00"

# Weergeven van geselecteerde locatie- en tijdgegevens
st.write(f"**Land**: {country}, **Locatie**: {location} ({latitude}, {longitude})")
st.write(f"**Zonsopgang**: {sunrise}, **Zonsondergang**: {sunset}")

# Expander met kopieerbare weergegevens per uur
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
        wind_speeds = hourly_data["wind_speed_10m"]
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
                    f"{hour}: Temp:{temperatures[i]:.1f}°C - Neersl:{precipitation[i]:.1f}mm - Bew.Tot:{cloudcover[i]}%"
                    f" (L:{cloudcover_low[i]}%, M:{cloudcover_mid[i]}%, H:{cloudcover_high[i]}%) - Wind:{wind_direction} {beaufort}Bf"
                )
                st.code(weather_info)

# Expander voor de kaartweergave
with st.expander("Kaartweergave van deze locatie"):
    if latitude and longitude:
        map_folium = folium.Map(location=[latitude, longitude], zoom_start=12)
        folium.Marker([latitude, longitude], popup=location).add_to(map_folium)
        st_folium(map_folium, width=700)

# Derde expander voor de 3-daagse weersvoorspelling
with st.expander("3-daagse weersvoorspelling"):
    forecast_data = fetch_3_day_forecast(latitude, longitude)
    if forecast_data:
        daily_forecasts = forecast_data["daily"]
        hourly_data = forecast_data["hourly"]
        
        for i, day in enumerate(daily_forecasts["time"]):
            date = datetime.fromisoformat(day).strftime("%A %d %B %Y")
            sunrise = datetime.fromisoformat(daily_forecasts["sunrise"][i]).strftime("%H:%M")
            sunset = datetime.fromisoformat(daily_forecasts["sunset"][i]).strftime("%H:%M")
            
            # Alleen uren binnen de zonsopgang en zonsondergang weergeven
            st.write(f"**{date}:**")
            for j, time in enumerate(hourly_data["time"]):
                hour = datetime.fromisoformat(time).strftime("%H:%M")
                if sunrise <= hour <= sunset:
                    temperature = hourly_data["temperature_2m"][j]
                    precipitation = hourly_data["precipitation"][j]
                    cloudcover = hourly_data["cloud_cover"][j]
                    cloudcover_low = hourly_data["cloud_cover_low"][j]
                    cloudcover_mid = hourly_data["cloud_cover_mid"][j]
                    cloudcover_high = hourly_data["cloud_cover_high"][j]
                    wind_direction = get_wind_direction(hourly_data["wind_direction_10m"][j])
                    wind_speed = wind_speed_to_beaufort(hourly_data["wind_speed_10m"][j])

                    st.write(f"{hour}: Temp: {temperature}°C - Precip: {precipitation}mm - "
                             f"Cloud Cover: {cloudcover}% (Low: {cloudcover_low}%, Mid: {cloudcover_mid}%, High: {cloudcover_high}%) - "
                             f"Wind: {wind_direction} {wind_speed}Bf")
