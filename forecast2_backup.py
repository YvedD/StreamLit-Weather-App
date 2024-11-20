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

# Functie om de afbeelding te draaien op basis van de windrichting
def rotate_wind_icon(degree):
    # Laad het icoon vanuit een lokale bestandspad
    wind_icon_path = "wind1.png"
    
    # Open de afbeelding met PIL
    image = Image.open(wind_icon_path)
    
    # Draai de afbeelding volgens de windrichting
    rotated_image = image.rotate(360 - degree, expand=True)  # Draai het icoon om de juiste richting te krijgen
    
    # Schaal de afbeelding naar 16x16 pixels
    rotated_image = rotated_image.resize((16, 16))
    
    return rotated_image

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
                data = []  # List voor de gegevens die we gaan toevoegen aan de tabel
                for i in range(len(times)):
                    # Haal datum en tijd op uit de tijdstempel
                    timestamp = times[i]
                    date, time = timestamp.split("T")
                    if date != current_date:
                        current_date = date
                        # Voeg een nieuwe datum als titel in de tabel
                        data.append([f"**{current_date}**", "", "", "", "", "", "", "", "", ""])

                    # Verkrijg de windrichting
                    wind_dir_10 = wind_direction_10m[i] if i < len(wind_direction_10m) else "N/B"
                    wind_dir_compass_10 = wind_direction_to_compass(wind_dir_10)

                    # Draai de afbeelding op basis van de windrichting
                    rotated_wind_icon = rotate_wind_icon(wind_dir_10)

                    # Voeg gegevens toe aan de lijst voor de tabel
                    data.append([
                        time,  # Tijd
                        f"{temperature[i]}°C",  # Temperatuur
                        f"{precipitation[i]} mm",  # Neerslag
                        f"{cloud_cover[i]}% (L {cloud_low[i]}%, M {cloud_mid[i]}%, H {cloud_high[i]}%)",  # Bewolking
                        f"{visibility[i]} m",  # Zichtbaarheid
                        wind_speed_to_beaufort(wind_speed_10m[i]),  # Windsnelheid @ 10m
                        wind_speed_to_beaufort(wind_speed_80m[i]),  # Windsnelheid @ 80m
                        wind_dir_compass_10,  # Windrichting
                        "",  # Lege kolom voor het icoon
                        rotated_wind_icon  # Het gedraaide icoon
                    ])

                # Zet de data om in een pandas DataFrame voor mooie weergave
                df = pd.DataFrame(data, columns=[
                    f"🕒 Tijd", f"🌡️ Temperatuur", f"🌧️ Neerslag", f"☁️ Bewolking", f"👁️ Zichtbaarheid", 
                    f"💨 Windsnelheid @ 10m", f"💨 Windsnelheid @ 80m", f"🧭 Windrichting", "Icoon", "Icoon afbeelding"
                ])

                # Toon de tabel
                st.dataframe(df)

            else:
                st.write("Geen uurlijkse gegevens beschikbaar.")
