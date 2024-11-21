import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import pandas as pd

# Functie om windrichting om te zetten naar kompasrichting
def wind_direction_to_compass(degree):
    compass_points = [
        "N", "NNO", "NO", "ONO", "O", "OZO", "ZO", "ZZO", "Z", "ZZW", "ZW", "WZW", "W", "WNW", "NW", "NNW"
    ]
    index = round(degree / 22.5) % 16
    return compass_points[index]

# Functie om windsnelheid om te zetten naar Beaufort
def wind_speed_to_beaufort(speed_kmh):
    if speed_kmh is None:
        return "N/B"
    beaufort_scale = [
        (1, "0"), (5, "1"), (11, "2"), (19, "3"),
        (28, "4"), (38, "5"), (49, "6"),
        (61, "7"), (74, "8"), (88, "9"),
        (102, "10"), (117, "11"), (float("inf"), "12")]
    for threshold, description in beaufort_scale:
        if speed_kmh <= threshold:
            return description

# Functie om de SVG-pijl te maken voor de windrichting
def create_wind_icon(degree):
    if degree is None:
        return "N/B"
    
    # Bereken de windrichting in graden voor de pijl (de pijl wijst de andere kant op, dus 180 graden verschuiven)
    arrow_degree = (degree + 180) % 360

    # SVG voor de pijl, deze wordt geroteerd naar de juiste richting
    arrow_svg = f"""
    <svg width="20" height="20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <g transform="rotate({arrow_degree}, 50, 50)">
            <polygon points="50,5 60,35 50,25 40,35" fill="blue"/>
            <line x1="50" y1="25" x2="50" y2="85" stroke="blue" stroke-width="8"/>
        </g>
    </svg>
    """
    return arrow_svg

# Functie om weergegevens weer te geven
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
    st.title("**Forecast/Voorspelling** (-1d+5d) - by Open-Meteo API")
    weather_data = fetch_weather_data(API_URL)

    if weather_data:
        with st.expander("Forecastdata / Voorspelling weergegevens"):
            # Toon dagelijkse gegevens
            daily = weather_data.get("daily", {})
            sunrise = daily.get("sunrise", ["Niet beschikbaar"])[0]
            sunset = daily.get("sunset", ["Niet beschikbaar"])[0]
            st.write(f"Sunrise / Zonsopgang: {sunrise} - Sunset / Zonsondergang: {sunset}")

            # Toon uurlijkse gegevens
            hourly = weather_data.get("hourly", {})
            times = hourly.get("time", [])
            temperature = hourly.get("temperature_2m", [])
            precipitation = hourly.get("precipitation", [])
            cloud_cover = hourly.get("cloud_cover", [])
            cloud_low = hourly.get("cloud_cover_low", [])
            cloud_mid = hourly.get("cloud_cover_mid", [])
            cloud_high = hourly.get("cloud_cover_high", [])
            visibility = hourly.get("visibility", [])
            wind_speed_10m = hourly.get("wind_speed_10m", [])
            wind_speed_80m = hourly.get("wind_speed_80m", [])
            wind_direction_10m = hourly.get("wind_direction_10m", [])

            if times:
                current_date = None
                st.write("<style>table {width: 100%;}</style>", unsafe_allow_html=True)  # CSS-styling
                for i in range(len(times)):
                    # Haal datum en tijd op uit de tijdstempel
                    timestamp = times[i]
                    date, time = timestamp.split("T")
                    if date != current_date:
                        current_date = date
                        st.markdown(f"### **Datum: {current_date}**")

                    # Verkrijg de windrichting in graden
                    wind_dir_10 = wind_direction_10m[i] if i < len(wind_direction_10m) else None
                    wind_dir_compass_10 = wind_direction_to_compass(wind_dir_10)

                    # Maak de SVG-pijl voor de windrichting
                    wind_icon_svg = create_wind_icon(wind_dir_10)

                    # Toon gegevens als een tabelrij met HTML voor de SVG-pijl
                    st.markdown(
                        f"""
                        <table>
                        <tr>
                            <td>🕒 {time}</td>
                            <td>🌡️ {temperature[i]}°C</td>
                            <td>🌧️ {precipitation[i]} mm</td>
                            <td>☁️ {cloud_cover[i]}% (L {cloud_low[i]}%, M {cloud_mid[i]}%, H {cloud_high[i]}%)</td>
                            <td>👁️ {visibility[i]} m</td>
                            <td>💨 @10m {wind_speed_to_beaufort(wind_speed_10m[i])}</td>
                            <td>💨 @80m {wind_speed_to_beaufort(wind_speed_80m[i])}</td>
                            <td>🧭 {wind_dir_compass_10}</td>
                            <td>{wind_icon_svg}</td>
                        </tr>
                        </table>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.write("Geen uurlijkse gegevens beschikbaar.")

# Voer de applicatie uit
show_forecast2_expander()
