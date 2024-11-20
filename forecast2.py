import streamlit as st
import requests

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
        (1, "0 (stil)"), (5, "1 (zwak)"), (11, "2 (zwak)"), (19, "3 (matig)"),
        (28, "4 (matig)"), (38, "5 (vrij krachtig)"), (49, "6 (krachtig)"),
        (61, "7 (hard)"), (74, "8 (stormachtig)"), (88, "9 (storm)"),
        (102, "10 (zware storm)"), (117, "11 (zeer zware storm)"), (float("inf"), "12 (orkaan)")]
    for threshold, description in beaufort_scale:
        if speed_kmh <= threshold:
            return description

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
    @st.cache_data
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
            
            # Toon dagelijkse gegevens
            daily = weather_data.get("daily", {})
            sunrise = daily.get("sunrise", ["Niet beschikbaar"])[0]
            sunset = daily.get("sunset", ["Niet beschikbaar"])[0]
            
            st.write(f"🌅 Zonsopgang: {sunrise}")
            st.write(f"🌇 Zonsondergang: {sunset}")
            
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

                    # Definieer de URL voor het windicoon op basis van de windrichting
                    wind_icon_url = "https://github.com/YvedD/StreamLit-Weather-App/raw/main/noord_transp.png"

                    # Inline windpijl-icoon toevoegen met URL
                    wind_icon_html = f'<img src="{wind_icon_url}" width="16" style="vertical-align:middle;"/>'

                    # Toon alle gegevens behalve wind_dir_80m in dezelfde regel
                    st.markdown(
                        f"🕒 {time} | 🌡️ {temperature[i]}°C | 🌧️ {precipitation[i]} mm | "
                        f"☁️ {cloud_cover[i]}% (☁️L {cloud_low[i]}%,☁️M {cloud_mid[i]}%,☁️H {cloud_high[i]}%) | "
                        f"👁️ {visibility[i]} m | 💨@10m {wind_speed_to_beaufort(wind_speed_10m[i])} | "
                        f"💨@80m {wind_speed_to_beaufort(wind_speed_80m[i])} | Windrichting: {wind_dir_compass_10} "
                        f"{wind_icon_html}"
                    )

            else:
                st.write("Geen uurlijkse gegevens beschikbaar.")
