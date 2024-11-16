# invoer.py
import streamlit as st
from datetime import datetime
import requests

def get_sun_times(latitude, longitude, date):
    """
    Functie om de zonsopgang en zonsondergang te verkrijgen voor een gegeven locatie (latitude, longitude) en datum.
    """
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=sunrise,sunset&timezone=Europe%2FBerlin"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        sunrise = data['daily']['sunrise'][0]  # Eerste element voor de opgegeven datum
        sunset = data['daily']['sunset'][0]    # Eerste element voor de opgegeven datum
        return sunrise, sunset
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van zonsopkomst en zonsondergang: {e}")
        return None, None

def gebruikers_invoer():
    # Standaardwaarden voor België en Bredene
    default_land = "België"
    default_locatie = "Bredene"
    default_latitude = 51.2389
    default_longitude = 2.9724
    default_date = datetime.now().date()

    # Dropdown voor Europese landen (je kunt meer landen toevoegen)
    landen = ["België", "Nederland", "Duitsland", "Frankrijk"]  # Voeg meer landen toe als gewenst
    land = st.selectbox("Selecteer een land", landen, index=0)
    
    # Tekstveld voor locatie
    locatie = st.text_input("Geef een locatie op", value=default_locatie)
    
    # Datumveld met datumpicker
    datum = st.date_input("Kies een datum", value=default_date)
    
    # Dropdown voor beginuur en einduur
    uren = [f"{hour:02d}:00" for hour in range(24)]
    begin_uur = st.selectbox("Beginuur", uren, index=8)
    eind_uur = st.selectbox("Einduur", uren, index=16)

    # Verkrijg GPS-coördinaten voor de locatie (standaard Bredene)
    latitude, longitude = default_latitude, default_longitude
    if locatie.lower() != default_locatie.lower():
        latitude, longitude = get_gps_coordinates(locatie)

    # Haal zonsopkomst en zonsondergang op voor de gekozen datum
    sunrise, sunset = get_sun_times(latitude, longitude, datum)

    # Retourneer alle invoervelden en tijden
    return land, locatie, datum, begin_uur, eind_uur, latitude, longitude, sunrise, sunset

def get_gps_coordinates(location):
    """
    Haal de GPS-coördinaten op voor een gegeven locatie via Nominatim.
    """
    api_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1&limit=1"
    try:
        response = requests.get(api_url)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            st.error("Locatie niet gevonden.")
            return None, None
    except requests.RequestException as e:
        st.error(f"Fout bij het ophalen van GPS-coördinaten: {e}")
        return None, None
