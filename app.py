import streamlit as st
from datetime import datetime, timedelta
import requests
import folium
from streamlit_folium import st_folium

# Functie om weergegevens op te halen op basis van locatie en datum
def fetch_weather_data(lat, lon, date):
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

# Lijst van Europese landen voor de dropdown
european_countries = [
    "Albanië", "Andorra", "Armenië", "Oostenrijk", "Azerbeidzjan", "Wit-Rusland", "België", "Bosnië en Herzegovina",
    "Bulgarije", "Kroatië", "Cyprus", "Tsjechië", "Denemarken", "Estland", "Finland", "Frankrijk", "Georgië",
    "Duitsland", "Griekenland", "Hongarije", "IJsland", "Ierland", "Italië", "Kazachstan", "Kosovo", "Letland",
    "Liechtenstein", "Litouwen", "Luxemburg", "Malta", "Moldavië", "Monaco", "Montenegro", "Nederland", "Noorwegen",
    "Polen", "Portugal", "Roemenië", "Rusland", "San Marino", "Servië", "Slowakije", "Slovenië", "Spanje", "Zweden",
    "Zwitserland", "Turkije", "Oekraïne", "Verenigd Koninkrijk", "Vaticaanstad", "Noord-Macedonië"
]

# Standaardwaarden voor locatie en datum
default_country = "België"
default_location = "Bredene"
latitude = 51.2389
longitude = 2.9724
selected_date = datetime.now() - timedelta(days=1)

# Titel en instructies
st.title("Historische Weergegevens - Open-Meteo API")

# Invoeropties voor de gebruiker
country = st.selectbox("Selecteer land", european_countries, index=european_countries.index(default_country))
location = st.text_input("Locatie", value=default_location)
selected_date = st.date_input("Datum", value=selected_date)
start_hour = st.selectbox("Beginuur", [f"{hour:02d}:00" for hour in range(24)], index=8)
end_hour = st.selectbox("Einduur", [f"{hour:02d}:00" for hour in range(24)], index=16)

# Update coördinaten voor nieuwe locaties indien nodig
if country == "België" and location.lower() == "bredene":
    latitude, longitude = 51.2389, 2.9724
# Voeg hier meer locaties toe als gewenst, of integreer met een externe service om dynamisch locaties om te zetten naar coördinaten

# Weerdata ophalen
weather_data = fetch_weather_data(latitude, longitude, selected_date)

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
with st.expander("Historische Weergegevens - Kort Overzicht"):
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
                weather_info = (
                    f"{hour} : Temp.: {temperatures[i]:.1f} °C - "
                    f"Neersl.: {precipitation[i]:.1f} mm - "
                    f"Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, "
                    f"MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - "
                    f"Wind: {wind_directions[i]}° {wind_speeds[i]} km/u"
                )
                st.code(weather_info, language="")

# Expander voor kaartweergave met marker
with st.expander("Kaartweergave"):
    map_folium = folium.Map(location=[latitude, longitude], zoom_start=12)
    folium.Marker([latitude, longitude], popup=f"{location} ({latitude}, {longitude})").add_to(map_folium)
    st_folium(map_folium, width=700)
