# app.py
import streamlit as st
from invoer import show_input_form  # Invoerformulier en functies
from data import show_data_expander  # Data-uitbreiding (voor data weergave)
from maps import show_map_expander  # Kaart-uitbreiding voor kaartweergave

# Titel van het project
st.markdown('<div class="project-title">Migration Weather Data</div>', unsafe_allow_html=True)

# Toon het invoerformulier
show_input_form()  # Formulier uit invoer.py

# Toon de data-expander
show_data_expander()  # Expander voor data-weergave uit data.py

# Toon de kaart-expander
show_map_expander()  # Expander voor kaartweergave uit maps.py
