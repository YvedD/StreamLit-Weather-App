import streamlit as st
from invoer import show_input_form
from data import show_data_expander  # Gebruik de hernoemde functie uit data.py

# Titel van de project
st.markdown('<div class="project-title">Migration Weather Data</div>', unsafe_allow_html=True)

# Toon de invoer
show_input_form()  # Roep de invoer functie aan uit invoer.py

# Toon de nieuwe expander (Under Construction)
show_data_expander()  # Roep de functie voor de expander uit data.py
