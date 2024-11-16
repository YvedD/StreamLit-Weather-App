# Functie om weergegevens op te halen
def fetch_weather_data(lat, lon, start, end):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start}&end_date={end}"
        f"&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,cloudcover,cloudcover_low,cloudcover_mid,cloudcover_high,precipitation,visibility"
        f"&timezone=Europe/Berlin"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Fout bij het ophalen van weergegevens: {response.status_code}")
        return None

# Haal historische gegevens op
historical_data = fetch_weather_data(latitude, longitude, selected_date - timedelta(days=8), selected_date)

if historical_data:
    hourly = historical_data['hourly']
    times = [datetime.strptime(hourly['time'][i], "%Y-%m-%dT%H:%M") for i in range(len(hourly['time']))]
    temperatures = hourly.get('temperature_2m', [])
    wind_speeds = [kmh_to_beaufort(speed) for speed in hourly.get('wind_speed_10m', [])]
    wind_directions = [degrees_to_direction(deg) if deg is not None else '' for deg in hourly.get('wind_direction_10m', [])]
    cloudcover = hourly.get('cloudcover', [])
    cloudcover_low = hourly.get('cloudcover_low', [])
    cloudcover_mid = hourly.get('cloudcover_mid', [])
    cloudcover_high = hourly.get('cloudcover_high', [])
    precipitation = hourly.get('precipitation', [])

    # Filteren op geselecteerde datum en tijdsbereik
    start_datetime = datetime.combine(selected_date, datetime.strptime(start_hour, "%H:%M").time())
    end_datetime = datetime.combine(selected_date, datetime.strptime(end_hour, "%H:%M").time())

    # Expander voor kort overzicht van historische gegevens
    with st.expander("Historische Gegevens - Kort Overzicht"):
        for i in range(len(times)):
            if start_datetime <= times[i] <= end_datetime:
                # Controleer of de waarden geldig zijn voordat ze worden weergegeven
                if (i < len(temperatures) and i < len(precipitation) and 
                    i < len(cloudcover) and i < len(cloudcover_low) and 
                    i < len(cloudcover_mid) and i < len(cloudcover_high) and 
                    i < len(wind_directions) and i < len(wind_speeds)):
                    weather_info = f"{times[i].strftime('%H:%M')} : Temp.: {temperatures[i]:.1f} °C - Neersl.: {precipitation[i]:.1f} mm - Bew.Tot.: {cloudcover[i]}% (LOW: {cloudcover_low[i]}%, MID: {cloudcover_mid[i]}%, HI: {cloudcover_high[i]}%) - Wind: {wind_directions[i]} {wind_speeds[i]}Bf"
                    st.code(weather_info)
                else:
                    st.warning(f"Gegevens ontbreken voor tijdstip {times[i].strftime('%H:%M')}")

    # Grafieken voor de historische gegevens
    with st.expander("Historische Weergegevens - Grafieken"):
        sns.set(style="whitegrid")

        filtered_times = [time for time in times if start_datetime <= time <= end_datetime]
        filtered_temperatures = [temperatures[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]
        filtered_wind_speeds = [wind_speeds[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]
        filtered_cloudcover = [cloudcover[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]
        filtered_precipitation = [precipitation[i] for i in range(len(times)) if start_datetime <= times[i] <= end_datetime]

        # Temperatuur en Windsnelheid Plot
        fig, ax1 = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=filtered_times, y=filtered_temperatures, color="blue", ax=ax1, label="Temperatuur (°C)")
        sns.lineplot(x=filtered_times, y=filtered_wind_speeds, color="green", ax=ax1, label="Windsnelheid (Beaufort)")
        ax1.set_xlabel("Datum en Tijd")
        ax1.set_ylabel("Temperatuur / Windsnelheid")
        ax1.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

        # Bewolking en Zichtbaarheid Plot
        fig, ax2 = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=filtered_times, y=filtered_cloudcover, color="orange", ax=ax2, label="Bewolking (%)")
        sns.lineplot(x=filtered_times, y=filtered_precipitation, color="purple", ax=ax2, label="Neerslag (mm)")
        ax2.set_xlabel("Datum en Tijd")
        ax2.set_ylabel("Bewolking en Neerslag")
        ax2.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

        st.pyplot(fig)
