import streamlit as st

def show_data_expander(latitude, longitude, location_name="Unknown Location"):
    with st.expander("Data", expanded=True):  # De expander voor de data
        st.write(f"Showing data for {location_name} at coordinates ({latitude}, {longitude})")
        # Er worden geen gegevens opgehaald, alleen de locatie en coördinaten worden weergegeven
        # Hier kan later functionaliteit worden toegevoegd als dat nodig is
