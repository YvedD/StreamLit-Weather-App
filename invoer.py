# invoer.py
import streamlit as st
from datetime import datetime

def gebruikers_invoer():
    # Dropdown voor Europese landen
    landen = ["België", "Nederland", "Duitsland", "Frankrijk"]  # En meer landen
    land = st.selectbox("Selecteer een land", landen, index=0)
    
    # Tekstveld voor locatie
    locatie = st.text_input("Geef een locatie op", value="Bredene")
    
    # Datumveld met datumpicker
    datum = st.date_input("Kies een datum", value=datetime.now().date())
    
    # Dropdown voor beginuur en einduur
    uren = [f"{hour:02d}:00" for hour in range(24)]
    begin_uur = st.selectbox("Beginuur", uren, index=8)
    eind_uur = st.selectbox("Einduur", uren, index=16)
    
    # Retourneer alle invoervelden
    return land, locatie, datum, begin_uur, eind_uur
