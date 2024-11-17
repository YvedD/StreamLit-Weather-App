import streamlit as st
from invoer import show_input_form
from maps import show_map_expander

def main():
    latitude, longitude, location = show_input_form()  # Verkrijg invoer van de gebruiker
    show_map_expander()  # Toon de kaart

if __name__ == "__main__":
    main()
