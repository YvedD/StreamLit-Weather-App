import streamlit as st

# Locatie invoerveld (Stad)
location = st.text_input("Locatie (stad):")

# Datum invoerveld in YYYY-MM-DD formaat
date = st.date_input("Datum:", value=None)

# Tijden invoervelden in HH:MM formaat
start_time = st.time_input("Starttijd:", value=None)
end_time = st.time_input("Eindtijd:", value=None)

# Weergave van de ingevoerde gegevens
st.write("Ingevoerde gegevens:")
st.write(f"Locatie: {location}")
st.write(f"Datum: {date}")
st.write(f"Starttijd: {start_time}")
st.write(f"Eindtijd: {end_time}")
