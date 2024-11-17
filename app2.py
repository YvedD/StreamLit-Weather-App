import streamlit as st
from invoer import show_input_form
from data import show_data_expander  # Gebruik de hernoemde functie uit data.py
from maps import show_map_expander  # Importeer de kaartfunctie uit maps.py

# Titel van het project
st.markdown('<div class="project-title">Migration Weather Data</div>', unsafe_allow_html=True)

# Toon de invoer
show_input_form()  # Roep de invoerfunctie aan uit invoer.py

# Toon de data-expander
show_data_expander()  # Roep de functie voor de data-expander aan uit data.py

# Toon de kaart-expander
show_map_expander()  # Roep de kaartfunctie aan uit maps.py
