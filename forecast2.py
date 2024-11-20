import streamlit as st
import requests

def show_forecast2_expander():
    """
    Haalt gegevens op van de Open-Meteo API en toont deze in een Streamlit-expander.
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
            temperature = hourly.get("temperature_2m", [])
            precipitation = hourly.get("precipitation", [])
            
            if temperature and precipitation:
                st.write("📊 Eerste paar uurlijkse gegevens:")
                for hour, (temp, prec) in enumerate(zip(temperature[:5], precipitation[:5])):
                    st.write(f"Uur {hour}: Temperatuur: {temp}°C, Neerslag: {prec}mm")
            else:
                st.write("Geen uurlijkse gegevens beschikbaar.")
