import streamlit as st
import requests

# Functie om windsnelheid (km/u) om te zetten naar de Beaufort-schaal
def wind_speed_to_beaufort(speed_kmh):
    if speed_kmh is None:
        return "N/B"
    beaufort_scale = [
        (1, "0 (stil)"), (5, "1 (zwak)"), (11, "2 (zwak)"), (19, "3 (matig)"),
        (28, "4 (matig)"), (38, "5 (vrij krachtig)"), (49, "6 (krachtig)"),
        (61, "7 (hard)"), (74, "8 (stormachtig)"), (88, "9 (storm)"),
        (102, "10 (zware storm)"), (117, "11 (zeer zware storm)"), (float("inf"), "12 (orkaan)")
    ]
    for threshold, description in beaufort_scale:
        if speed_kmh <= threshold:
            return description

# Functie om windrichting (°) om te zetten naar kompasrichtingen
def wind_direction_to_compass(degree):
    if degree is None:
        return "N/B"
    compass_points = [
        "N", "NNO", "NO", "ONO", "O", "OZO", "ZO", "ZZO", "Z", "ZZW", "ZW", "WZW", "W", "WNW", "NW", "NNW"
    ]
    index = round(degree / 22.5) % 16
    return compass_points[index]

# Functie om weergegevens te tonen
def show_forecast2_expander():
    """
    Haalt gegevens op van de Open-Meteo API en toont deze in een Streamlit-expander.
    Gegevens worden netjes geformatteerd met conversies voor windsnelheid en richting.
    Elke nieuwe dag begint met een kop 'Datum: '.
    """
    # URL van de Open-Meteo API
    API_URL = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=51.2349&longitude=2.9756&hourly=temperature_2m,precipitation,"
        "cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,"
        "wind_speed_10m,wind_speed_80m,wind_direction_10m,wind_direction_80m&"
        "daily=sunrise,sunset&timezone=Europe%2FBerlin&past_days=1"
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
    st.title("Weerinformatie - Open-Meteo API")
    st.write("Klik op de expander hieronder om de gegevens te bekijken.")

    weather_data = fetch_weather_data(API_URL)

    if weather_data:
        with st.expander("Toon weergegevens"):
            st.subheader("Algemene Weerdata")
            
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
            wind_direction_10m = hourly.get("wind_direction_10m", [])

            if times:
                st.write("📊 Gedetailleerde uurlijkse voorspelling:")
                current_date = None
                for i in range(len(times)):
                    # Haal datum en tijd op uit de tijdstempel
                    timestamp = times[i]
                    date, time = timestamp.split("T")  # Split naar datum en tijd
                    if date != current_date:
                        # Toon nieuwe dagtitel als de datum verandert
                        current_date = date
                        st.write(f"### 📅 Datum: {current_date}")

                    # Controleer of alle gegevens beschikbaar zijn, anders geef 'N/B' aan
                    temp = temperature[i] if i < len(temperature) else "N/B"
                    prec = precipitation[i] if i < len(precipitation) else "N/B"
                    cloud = cloud_cover[i] if i < len(cloud_cover) else "N/B"
                    cloud_l = cloud_low[i] if i < len(cloud_low) else "N/B"
                    cloud_m = cloud_mid[i] if i < len(cloud_mid) else "N/B"
                    cloud_h = cloud_high[i] if i < len(cloud_high) else "N/B"
                    vis = visibility[i] if i < len(visibility) else "N/B"
                    wind_speed = wind_speed_10m[i] if i < len(wind_speed_10m) else "N/B"
                    wind_speed_bf = wind_speed_to_beaufort(wind_speed)
                    wind_dir = wind_direction_10m[i] if i < len(wind_direction_10m) else "N/B"
                    wind_dir_compass = wind_direction_to_compass(wind_dir)

                    # Weergave van gegevens in een nette regel per uur
                    st.write(
                        f"🕒 {time} | 🌡️ Temp: {temp}°C | 🌧️ Neerslag: {prec} mm | "
                        f"☁️ Bewolking: {cloud}% (Laag: {cloud_l}%, Midden: {cloud_m}%, Hoog: {cloud_h}%) | "
                        f"👁️ Zicht: {vis} m | 💨 Wind: {wind_speed_bf} (Beaufort), {wind_dir_compass} ({wind_dir}°)"
                    )
            else:
                st.write("Geen uurlijkse gegevens beschikbaar.")
