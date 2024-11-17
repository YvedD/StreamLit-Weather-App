import streamlit as st
import requests
import math
from datetime import datetime

# Functie om de windrichting om te zetten naar de juiste kompasrichting
def wind_direction_to_compass(degrees):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

# Functie om windsnelheid in Beaufort-schaal om te zetten
def wind_speed_to_beaufort(kmh):
    beaufort_limits = [0, 1, 6, 12, 20, 29, 39, 50, 62, 75, 89, 103, 118]
    for bft, limit in enumerate(beaufort_limits):
        if kmh < limit:
            return bft
    return 12  # 12 Bf voor snelheden boven de hoogste grens

# Haal gegevens op uit st.session_state()
country = st.session_state.get("country", "N/A")
location = st.session_state.get("location", "N/A")
latitude = st.session_state.get("latitude", 51.2349)
longitude = st.session_state.get("longitude", 2.9756)
selected_date = st.session_state.get("selected_date", "2023-11-01")
start_hour = st.session_state.get("start_hour", "00:00")
end_hour = st.session_state.get("end_hour", "23:59")
sunrise = st.session_state.get("sunrise", "08:00")
sunset = st.session_state.get("sunset", "18:00")

# Formateer de locatiecoördinaten in graden
formatted_coordinates = f"{abs(latitude):.2f}°{'N' if latitude >= 0 else 'S'} {abs(longitude):.2f}°{'E' if longitude >= 0 else 'W'}"

# Toon de hoofdinformatie bovenaan in de expander
st.write(f"Locatie: {location}, {country}")
st.write(f"Coördinaten: {formatted_coordinates}")
st.write(f"Geselecteerde datum: {selected_date}")
st.write(f"Zonsopkomst: {sunrise}, Zonsondergang: {sunset}")
st.write(f"Tijdspanne: {start_hour} - {end_hour}")

# API-aanroep naar Open-Meteo met de opgegeven parameters
api_url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={selected_date}&end_date={selected_date}&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,wind_speed_80m,wind_direction_80m&timezone=Europe%2FBerlin"
try:
    response = requests.get(api_url)
    response.raise_for_status()  # Controleer of de API-aanroep succesvol is
    data = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"API-aanroep mislukt: {e}")
    data = {}

# Controleer of er data is geretourneerd en verwerk deze indien beschikbaar
def show_data_expander():
    if "hourly" in data:
        # Specifieke gegevens ophalen uit de API-reactie
        temperature_data = data["hourly"]["temperature_2m"]
        precipitation_data = data["hourly"]["precipitation"]
        cloud_cover_data = data["hourly"]["cloud_cover"]
        cloud_cover_low_data = data["hourly"]["cloud_cover_low"]
        cloud_cover_mid_data = data["hourly"]["cloud_cover_mid"]
        cloud_cover_high_data = data["hourly"]["cloud_cover_high"]
        visibility_data = data["hourly"]["visibility"]
        wind_speed_data = data["hourly"]["wind_speed_80m"]
        wind_direction_data = data["hourly"]["wind_direction_80m"]
        time_data = data["hourly"]["time"]

        # Converteer de start- en eindtijd naar datetime-objecten voor vergelijking
        start_time = datetime.strptime(f"{selected_date} {start_hour}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{selected_date} {end_hour}", "%Y-%m-%d %H:%M")

        # Lijst om geformatteerde outputregels op te slaan
        formatted_output = []

        # Loop door elk uur om gegevens op te halen die binnen de opgegeven tijdspanne vallen
        for i in range(len(time_data)):
            current_time = datetime.fromisoformat(time_data[i])

            # Controleer of de huidige tijd binnen het gewenste bereik valt
            if start_time <= current_time <= end_time:
                # Tijd in het HH:MM formaat
                time_str = current_time.strftime("%H:%M")

                # Temperaturen, neerslag en bewolkingsniveaus
                temperature = round(temperature_data[i], 1)
                precipitation = round(precipitation_data[i], 1)
                cloud_cover = round(cloud_cover_data[i], 1)
                cloud_cover_low = round(cloud_cover_low_data[i], 1)
                cloud_cover_mid = round(cloud_cover_mid_data[i], 1)
                cloud_cover_high = round(cloud_cover_high_data[i], 1)

                # Zichtbaarheid omzetten van meters naar kilometers en afronden
                visibility = round(visibility_data[i] / 1000)

                # Windrichting omzetten naar kompasrichting en windsnelheid naar Beaufort-schaal
                wind_direction = wind_direction_to_compass(wind_direction_data[i])
                wind_speed_kmh = round(wind_speed_data[i], 1)
                wind_beaufort = wind_speed_to_beaufort(wind_speed_kmh)

                # Format output als één regel
                output_line = (
                    f"{time_str} Tmp: {temperature}°C-Precip: {precipitation} mm-"
                    f"Cloud: {cloud_cover}% (L:{cloud_cover_low}%,M:{cloud_cover_mid}%,H:{cloud_cover_high}%)-"
                    f"Visib:{visibility}km-Wnd: {wind_direction}: {wind_beaufort}Bf"
                )

                # Voeg deze regel toe aan de lijst met geformatteerde uitvoer
                formatted_output.append(output_line)

        # Toon alle gegevens in een kopieerbaar blok
        if formatted_output:
            st.code("\n".join(formatted_output), language="text")
        else:
            st.write("Geen data beschikbaar binnen de opgegeven tijdspanne.")

    else:
        st.error("Geen gegevens beschikbaar voor de geselecteerde datum.")

# Roep de functie aan om de data expander te tonen
show_data_expander()
