import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests
from dateutil.parser import parse
from streamlit_echarts import st_echarts

# Functie om lokale tijdzone te bepalen
def get_local_timezone(latitude, longitude):
    from timezonefinder import TimezoneFinder
    tz_finder = TimezoneFinder()
    timezone_str = tz_finder.timezone_at(lat=latitude, lng=longitude)
    if not timezone_str:
        st.error("Tijdzone niet gevonden voor de opgegeven locatie.")
        return None
    return pytz.timezone(timezone_str)

def show_weather_chart_expander():
    """
    Haalt gegevens op van de Open-Meteo API en toont een EChart grafiek.
    """
    latitude = st.session_state.get("latitude")
    longitude = st.session_state.get("longitude")
    sunrise = st.session_state.get("sunrise")
    sunset = st.session_state.get("sunset")

    if not (latitude and longitude and sunrise and sunset):
        st.error("Locatiegegevens of zonsopgang/zonsondergang ontbreken. Stel eerst de locatie in.")
        return

    local_timezone = get_local_timezone(latitude, longitude)
    if not local_timezone:
        return

    API_URL = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,precipitation"
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

    weather_data = fetch_weather_data(API_URL)

    if weather_data:
        # Zonsopgang en zonsondergang omzetten naar datetime
        sunrise_time = local_timezone.localize(
            datetime.strptime(sunrise, '%H:%M').replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        )
        sunset_time = local_timezone.localize(
            datetime.strptime(sunset, '%H:%M').replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        )
        filter_start_time = sunrise_time - timedelta(hours=1)
        filter_end_time = sunset_time + timedelta(hours=1)

        # Uurlijkse gegevens ophalen en filteren
        hourly = weather_data.get("hourly", {})
        times = hourly.get("time", [])
        temperature = hourly.get("temperature_2m", [])
        precipitation = hourly.get("precipitation", [])

        times_filtered = []
        temperatures_filtered = []
        precipitation_filtered = []

        if times:
            for i in range(len(times)):
                # Haal datum en tijd op uit de tijdstempel
                timestamp = times[i]
                try:
                    datetime_obj = parse(timestamp).astimezone(local_timezone)
                except ValueError:
                    continue

                # Filter gegevens buiten het gewenste bereik
                if not (filter_start_time <= datetime_obj <= filter_end_time):
                    continue

                # Voeg gefilterde data toe aan de lijsten
                times_filtered.append(datetime_obj.strftime('%H:%M'))
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
        with st.expander("Grafiek Weerdata (EChart)"):
            st_echarts(options=echart_option, height="400px")
