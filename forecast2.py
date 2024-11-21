import streamlit as st
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz
import requests
from dateutil.parser import parse
from data import convert_visibility  # Zorg ervoor dat je de juiste module hebt geïmporteerd voor zichtbaarheid
from streamlit_echarts import st_echarts

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

    # SVG voor de pijl, gecentreerd in een box
    arrow_svg = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
        <svg width="30" height="30" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <g transform="rotate({arrow_degree}, 50, 50)">
                <polygon points="50,5 60,35 50,25 40,35" fill="blue"/>
                <line x1="50" y1="25" x2="50" y2="85" stroke="blue" stroke-width="4"/>
            </g>
        </svg>
    </div>
    """
    return arrow_svg

# Functie om lokale tijdzone te bepalen
def get_local_timezone(latitude, longitude):
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lat=latitude, lng=longitude)
    if not timezone_str:
        st.error("Tijdzone niet gevonden voor de opgegeven locatie.")
        return None
    return pytz.timezone(timezone_str)

def show_forecast2_expander():
    """
    Haalt gegevens op van de Open-Meteo API en toont deze in een Streamlit-expander,
    beperkt tot de tijd één uur vóór zonsopgang en één uur na zonsondergang.
    """
    latitude = st.session_state.get("latitude")
    longitude = st.session_state.get("longitude")
    location = st.session_state.get("location")
    sunrise = st.session_state.get("sunrise")
    sunset = st.session_state.get("sunset")

    if not (latitude and longitude and location and sunrise and sunset):
        st.error("Locatiegegevens of zonsopkomst/zonsondergang ontbreken. Stel eerst de locatie in.")
        return

    local_timezone = get_local_timezone(latitude, longitude)
    if not local_timezone:
        return

    today = datetime.now(local_timezone)
    past_day = today - timedelta(days=1)
    forecast_days = 5

    API_URL = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,precipitation,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,"
        "visibility,wind_speed_10m,wind_speed_80m,wind_direction_10m"
        "&daily=sunrise,sunset"
        f"&timezone={local_timezone.zone}"
        "&past_days=1"
        "&forecast_days=5"
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

    st.title(f"**Weersvoorspelling voor {location}** (-1d/+5d)")

    weather_data = fetch_weather_data(API_URL)

    if weather_data:
        with st.expander("Forecastdata / Weersvoorspelling"):
            # Styling voor een compactere tabel
            st.markdown(
                """
                <style>
                    table {width: 100%; border-collapse: collapse;}
                    td, th {padding: 5px; text-align: center; font-size: 0.85em;}
                    tr {height: 40px;}
                </style>
                """, unsafe_allow_html=True
            )

            # Zonsopgang en zonsondergang omzetten naar datetime
            sunrise_time = local_timezone.localize(
                datetime.strptime(sunrise, '%H:%M').replace(year=today.year, month=today.month, day=today.day)
            )
            sunset_time = local_timezone.localize(
                datetime.strptime(sunset, '%H:%M').replace(year=today.year, month=today.month, day=today.day)
            )
            filter_start_time = sunrise_time - timedelta(hours=1)
            filter_end_time = sunset_time + timedelta(hours=1)

            # Toon dagelijkse gegevens
            daily = weather_data.get("daily", {})
            st.write(f"🌅 Zonsopgang: {sunrise} - 🌇 Zonsondergang: {sunset}")

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

            times_filtered = []
            temperatures_filtered = []
            precipitation_filtered = []

            if times:
                current_date = None
                for i in range(len(times)):
                    # Haal datum en tijd op uit de tijdstempel
                    timestamp = times[i]
                    try:
                        datetime_obj = parse(timestamp).astimezone(local_timezone)
                    except ValueError:
                        st.error(f"Ongeldige tijdstempel ontvangen: {timestamp}")
                        continue

                    # Filter gegevens buiten het gewenste bereik
                    if not (filter_start_time <= datetime_obj <= filter_end_time):
                        continue

                    date, time = datetime_obj.strftime('%Y-%m-%d'), datetime_obj.strftime('%H:%M')
                    if date != current_date:
                        current_date = date
                        st.markdown(f"### **Datum: {current_date}**")

                    # Verkrijg windgegevens
                    wind_dir_10 = wind_direction_10m[i] if i < len(wind_direction_10m) else None
                    wind_icon_svg = create_wind_icon(wind_dir_10)

                    # Verkrijg zichtbaarheid in kilometers
                    visibility_km = convert_visibility(visibility[i]) if visibility[i] is not None else "N/B"

                    # Toon gegevens in een tabelrij
                    st.markdown(
                        f
