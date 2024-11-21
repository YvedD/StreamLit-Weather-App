import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests
from dateutil.parser import parse
from streamlit_echarts import st_echarts
from data import convert_visibility  # Zorg ervoor dat je de juiste module hebt geïmporteerd voor zichtbaarheid

# Functie om lokale tijdzone te bepalen
def get_local_timezone(latitude, longitude):
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lat=latitude, lng=longitude)
    if not timezone_str:
        st.error("Tijdzone niet gevonden voor de opgegeven locatie.")
        return None
    return pytz.timezone(timezone_str)

def show_weather_data_with_echart_expander():
    """
    Haalt gegevens op van de Open-Meteo API en toont deze in een Streamlit-expander
    en bouwt een EChart met temperatuur en neerslag.
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
        with st.expander("Weersvoorspelling / Forecast Data"):
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
                        f"""
                        <table>
                            <tr>
                                <td>{time}</td>
                                <td>{temperature[i]} °C</td>
                                <td>{precipitation[i]} mm</td>
                                <td>☁️L {cloud_low[i]}%</td>
                                <td>☁️M {cloud_mid[i]}%</td>
                                <td>☁️H {cloud_high[i]}%</td>
                                <td>🌬️ {wind_speed_10m[i]} km/h - {wind_icon_svg}</td>
                                <td>🌫️ {visibility_km} km</td>
                            </tr>
                        </table>
                        """, unsafe_allow_html=True
                    )

                    # Voeg data toe voor de grafiek
                    times_filtered.append(time)
                    temperatures_filtered.append(temperature[i])
                    precipitation_filtered.append(precipitation[i])

            # Maak een EChart grafiek met temperatuur en neerslag
            echart_option = {
                "tooltip": {
                    "trigger": "axis"
                },
                "legend": {
                    "data": ["Temperatuur", "Neerslag"]
                },
                "xAxis": {
                    "type": "category",
                    "boundaryGap": False,
                    "data": times_filtered
                },
                "yAxis": [
                    {"type": "value", "name": "Temperatuur (°C)", "position": "left"},
                    {"type": "value", "name": "Neerslag (mm)", "position": "right"}
                ],
                "series": [
                    {
                        "name": "Temperatuur",
                        "type": "line",
                        "data": temperatures_filtered,
                        "yAxisIndex": 0,
                        "smooth": True,
                        "itemStyle": {
                            "color": "#FF6347"
                        }
                    },
                    {
                        "name": "Neerslag",
                        "type": "bar",
                        "data": precipitation_filtered,
                        "yAxisIndex": 1,
                        "itemStyle": {
                            "color": "#1E90FF"
                        }
                    }
                ]
            }

            # Toon de EChart
            st_echarts(options=echart_option, height="400px")
