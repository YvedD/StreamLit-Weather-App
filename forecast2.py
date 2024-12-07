
# Forecast2.py module (onderdeel van "Migration Weather-app")

import streamlit as st
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz
import requests
from dateutil.parser import parse
from data import convert_visibility


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
                <line x1="50" y1="25" x2="50" y2="85" stroke="blue" stroke-width="12"/>
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
    beperkt tot de tijden van zonsopgang en zonsondergang van vandaag.
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

    # Bepaal de filtertijden van vandaag (gebruik deze voor ALLE dagen)
    sunrise_time_today = local_timezone.localize(
        datetime.strptime(sunrise, '%H:%M').replace(year=today.year, month=today.month, day=today.day)
    )
    sunset_time_today = local_timezone.localize(
        datetime.strptime(sunset, '%H:%M').replace(year=today.year, month=today.month, day=today.day)
    )
    filter_start_time = sunrise_time_today - timedelta(hours=1)
    filter_end_time = sunset_time_today + timedelta(hours=1)

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

    def fetch_weather_data(url):
        # Definieer de headers binnen de functie
        headers = {
            "User-Agent": "StreamlitWeatherApp/1.0 (mailto:ydsdsy@gmail.com)"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Controleer op HTTP-fouten
            return response.json()  # Geef de JSON-gegevens terug
        except requests.exceptions.HTTPError as http_err:
            st.error(f"HTTP fout opgetreden: {http_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            st.error(f"Fout bij het verbinden met de API: {req_err}")
            return None

    # Haal de weersgegevens op met fetch_weather_data
    weather_data = fetch_weather_data(API_URL)  # Deze regel voegt de missende initialisatie toe.

    # Controleer of er gegevens zijn opgehaald
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
            # Rest van je code om gegevens weer te geven...

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
                for i in range(len(times)):
                    # Haal datum en tijd op uit de tijdstempel
                    timestamp = times[i]
                    try:
                        datetime_obj = parse(timestamp).astimezone(local_timezone)
                    except ValueError:
                        st.error(f"Ongeldige tijdstempel ontvangen: {timestamp}")
                        continue

                    # Gebruik sunrise/sunset filtering van vandaag
                    if not (filter_start_time.time() <= datetime_obj.time() <= filter_end_time.time()):
                        continue

                    date, time = datetime_obj.strftime('%Y-%m-%d'), datetime_obj.strftime('%H:%M')
                    if date != current_date:
                        current_date = date
                        st.markdown(f"### **Datum: {current_date}**")

                    # Verkrijg windgegevens
                    wind_dir_10 = wind_direction_10m[i] if i < len(wind_direction_10m) else None
                    wind_icon_svg = create_wind_icon(wind_dir_10)
                    # functie om de zichtbaarheid in kilometers om te zetten
                    #zichtbaarheid_km = convert_visibility(visibility[i])

                    # Toon gegevens in een tabelrij
                    st.markdown(
                        f"""
                        <table>
                        <tr>
                            <td>🕒<br>{time}<br> </td>
                            <td>🌡️<br>{temperature[i]}°C<br> </td>
                            <td>🌧️<br>{precipitation[i]}mm<br> </td>
                            <td>☁️<br>Total<br>{cloud_cover[i]}%</td>
                            <td>☁️<br>Low<br>{cloud_low[i]}%</td>
                            <td>☁️<br>Mid<br>{cloud_mid[i]}%</td>
                            <td>☁️<br>High<br>{cloud_high[i]}%</td>
                            <td>👁️<br>{convert_visibility(visibility[i])}Km<br> </td>
                            <td>💨<br>@10m<br>{wind_speed_to_beaufort(wind_speed_10m[i])}Bf</td>
                            <td>💨<br>@80m<br>{wind_speed_to_beaufort(wind_speed_80m[i])}Bf</td>
                            <td>{wind_icon_svg}<br>{wind_direction_to_compass(wind_direction_10m[i])}<br> </td>
                        </tr>
                        </table>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.write("Geen uurlijkse gegevens beschikbaar.")
