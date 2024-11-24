import streamlit as st
from datetime import datetime, timedelta, time

# Functie om de slider in te stellen voor de start- en eindtijden
def create_time_slider(start_hour, end_hour):
    # De slider retourneert een tuple van de start- en eindtijden
    appointment = st.slider(
        "Selecteer het tijdsinterval:",
        min_value=time(0, 0),  # Begin om 00:00
        max_value=time(23, 59),  # Eindig om 23:00
        value=(start_hour, end_hour),  # De standaardwaarden worden ingesteld op civiele zonsopgang en zonsondergang
        step=timedelta(hours=1),  # Stappen van één uur
        format="HH:mm",  # Weergeven in het formaat uur:minuten
    )

    # Toon de geselecteerde tijden boven de slider
    st.write(f"Startuur: {appointment[0].strftime('%H:%M')}")
    st.write(f"Einduur: {appointment[1].strftime('%H:%M')}")
    
    return appointment

# Hoofdfunctie om de app te starten
def main():
    # Voorbeeld start- en eindtijden op basis van de civiele zonsopgang en zonsondergang (zoals hierboven opgehaald)
    civil_sunrise_local = time(6, 30)  # Starttijd van de civiele zonsopgang (voorbeeld)
    civil_sunset_local = time(20, 45)  # Eindtijd van de civiele zonsondergang (voorbeeld)

    # Sidebar configuratie
    with st.sidebar:
        st.title("Locatie-instellingen")
        
        # Selecteer de datum via de sidebar
        selected_date = st.date_input("Selecteer een datum", value=datetime.now().date())

        # Locatiegegevens kunnen ook aangepast worden in de sidebar
        default_country = st.text_input("Land", value="België")
        default_location = st.text_input("Locatie", value="Bredene")
        latitude = st.number_input("Latitude", value=51.2389)
        longitude = st.number_input("Longitude", value=2.9724)

        # Voeg de tijdsinterval slider toe met de civiele zonsopgang en zonsondergang als standaard
        appointment = create_time_slider(civil_sunrise_local, civil_sunset_local)

    # Maak tabs aan voor de verschillende secties
    tab1, tab2, tab3 = st.tabs(["Weatherdata", "Temperature Forecast", "Multiday Forecast"])

    # Tab 1: Weatherdata
    with tab1:
        st.subheader("Weatherdata")
        st.write("Weatherdata tab - Toon actuele weersomstandigheden")

    # Tab 2: Temperature Forecast
    with tab2:
        st.subheader("Temperature Forecast")
        st.write("Temperature Forecast tab - Toon temperatuurvoorspellingen")

    # Tab 3: Multiday Forecast
    with tab3:
        st.subheader("Multiday Forecast")
        st.write("Multiday Forecast tab - Toon meerdaagse weersvoorspellingen")

if __name__ == "__main__":
    main()
