# data.py
import streamlit as st

def show_data_expander(latitude, longitude, location_name="Unknown Location"):
    with st.expander("Data", expanded=True):
        st.write(f"Showing data for {location_name} at coordinates ({latitude}, {longitude})")
        # Voeg hier jouw logica toe voor het ophalen en weergeven van historische weersgegevens of andere data
