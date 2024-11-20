import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Functie om de afbeelding te draaien afhankelijk van de windrichting
def rotate_wind_icon(degree):
    """
    Draait de afbeelding op basis van de windrichting in graden.
    """
    wind_icon_url = "https://github.com/YvedD/StreamLit-Weather-App/raw/main/noord_transp.png"
    response = requests.get(wind_icon_url)
    
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img = img.rotate(-degree, expand=True)  # Draai de afbeelding met de windrichting in graden
        return img
    else:
        st.error("Kon het windicoon niet ophalen.")
        return None

# Functie om windrichting (°) om te zetten naar kompasrichtingen
def wind_direction_to_compass(degree):
    compass_points = [
        "N", "NNO", "NO", "ONO", "O", "OZO", "ZO", "ZZO", "Z", "ZZW", "ZW", "WZW", "W", "WNW", "NW", "NNW"
    ]
    index = round(degree / 22.5) % 16
    return compass_points[index]

# Functie om weergegevens te tonen
def show_forecast2_expander():
    """
    Haalt gegevens op van de Open-Meteo API en toont deze in een Streamlit-expander.
    """
    # URL van de Open-Meteo API
    API_URL = (
        "https://api.open-meteo.com/v1/forecast?latitude=51.2349&longitude=2.9756&hourly=temperature_2m,precipitation,"
        "cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_10m,wind_speed_80m,"
        "wind_direction_10m&daily=sunrise,sunset&timezone=Europe%2FBerlin&past_days=1&forecast_days=5"
    )

    # Haal gegevens op van de API
    #@st.cache_data
    def fetch_weather_data(url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Kan de weergegevens niet ophalen. Controleer de API URL.")
            return None

    # UI-componenten
    st.title("**Forecast/Voorspelling** (-1d+5d) - Open-Meteo API")
    weather_data = fetch_weather_data(API_URL)

    if weather_data:
        with st.expander("Forecastdata / voorspelling weergegevens"):
            st.write("🌡️Temperature | 🌧️Precipation | ☁️Cloudcover (total/low/mid/high) | 👁️Visibility | 💨Windspeed @ 10m | 💨Windspeed @80m | Winddirection")
            
            # Toon uurlijkse gegevens
            hourly = weather_data.get("hourly", {})
            times = hourly.get("time", [])
            temperature = hourly.get("temperature_2m", [])
            precipitation = hourly.get("precipitation", [])
            cloud_cover = hourly.get("cloud_cover", [])
            visibility = hourly.get("visibility", [])
            wind_speed_10m = hourly.get("wind_speed_10m", [])
            wind_speed_80m = hourly.get("wind_speed_80m", [])
            wind_direction_10m = hourly.get("wind_direction_10m", [])

            if times:
                st.write("📊 Gedetailleerde uurlijkse voorspelling:")
                current_date = None
                for i in range(len(times)):
                    # Haal datum en tijd op uit de tijdstempel
                    timestamp = times[i]
                    date, time = timestamp.split("T")
                    if date != current_date:
                        current_date = date
                        st.write(f"### 📅 Datum: {current_date}")

                    # Verkrijg de windrichting
                    wind_dir_10 = wind_direction_10m[i] if i < len(wind_direction_10m) else "N/B"
                    wind_dir_compass_10 = wind_direction_to_compass(wind_dir_10)

                    # Draai het windpijl-icoon op basis van de windrichting
                    rotated_wind_icon = rotate_wind_icon(wind_dir_10)

                    # Weergave van gegevens in een nette regel per uur
                    st.write(
                        f"🕒 {time} | 🌡️ {temperature[i]}°C | 🌧️ {precipitation[i]} mm | "
                        f"👁️ {visibility[i]} m | 💨@10m {wind_speed_10m[i]} km/h ({wind_dir_compass_10})"
                    )
                    
                    # Toon het gedraaide icoon
                    if rotated_wind_icon:
                        st.image(rotated_wind_icon, width=50)

            else:
                st.write("Geen uurlijkse gegevens beschikbaar.")
