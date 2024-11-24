import streamlit as st
import requests
import json
from invoer import show_input_form
from maps import show_map_expander
from data import show_data_expander  # Importeer de data-expander
from forecast2 import show_forecast2_expander
from forecast1 import show_forecast1_expander
from forecastchart import show_weather_chart_expander

# Configuratie van de pagina
st.set_page_config(
    layout="wide", 
    page_title="Migration Weather app",
    menu_items={
        "About": "Migration Weather App - Gebruik gegevens om weersomstandigheden te analyseren!"
    }
)

# CSS om ongewenste interface-elementen te verbergen
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Verberg het menu met de drie puntjes */
    header {visibility: hidden;}   /* Verberg de bovenste header */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Functie om het land van de gebruiker op basis van IP-adres op te halen
def get_country_from_ip():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        country = data.get('country', 'Unknown')
        return country
    except Exception as e:
        print(f"Error retrieving country from IP: {e}")
        return "Unknown"

# Functie om geolocatie op te halen via JavaScript (HTML5 geolocatie)
def get_location_js():
    st.markdown("""
        <script type="text/javascript">
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    window.parent.postMessage({latitude, longitude}, "*");
                });
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        </script>
    """, unsafe_allow_html=True)

# Hoofdprogramma
def main():
    # Zoek de locatie op bij het openen van de app (IP-geolocatie voor desktop)
    if "latitude" not in st.session_state or "longitude" not in st.session_state:
        country = get_country_from_ip()  # IP-geolocatie ophalen
        st.session_state.country = country
        st.session_state.latitude = 51.2389  # Standaardlocatie voor België (Bredene)
        st.session_state.longitude = 2.9724

    # Voeg geolocatie via JavaScript toe voor mobiele apparaten
    if st.session_state.get("latitude") == 51.2389 and st.session_state.get("longitude") == 2.9724:
        get_location_js()  # Ophaal en verstuur de locatie via JS (voor mobiele apparaten)

    # Tabs aanmaken
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Invoer", 
        "Kaart", 
        "Data", 
        "Forecast 1", 
        "Forecast 2"
    ])

    # Tab 1: Invoer
    with tab1:
        st.subheader("Invoer")
        latitude, longitude, location = show_input_form()

    # Tab 2: Kaart
    with tab2:
        st.subheader("Kaart")
        if latitude and longitude:
            # Toon de kaart met de juiste locatie
            #show_map_expander()
        else:
            st.error("Geen geldige locatiecoördinaten ingevoerd.")

    # Tab 3: Data
    with tab3:
        st.subheader("Data")
        #show_data_expander()  # Toon de data-expander

    # Tab 4: Forecast 1
    with tab4:
        st.subheader("Weersvoorspelling - Methode 1")
        #show_forecast1_expander()

    # Tab 5: Forecast 2
    with tab5:
        st.subheader("Weersvoorspelling - Methode 2")
        #show_forecast2_expander()

    # Optioneel: Voeg meer tabs toe indien nodig
    # Met bijvoorbeeld een tabblad voor een Echart:
    # with tab6:
    #     st.subheader("Weerkaart")
    #     show_weather_chart_expander()

if __name__ == "__main__":
    main()
