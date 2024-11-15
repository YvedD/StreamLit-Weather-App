import streamlit as st

# Jouw bestaande code (even gesimplificeerd voor het doel van de popup)
def main():
    st.title("Weather Data Viewer")

    # Invoer voor plaatsnaam en landkeuze
    country_name = st.selectbox("Kies een Europees land:", ["Nederland", "België", "Frankrijk", "Duitsland", "Luxemburg"])
    location_name = st.text_input(f"Voer de naam van de plaats in in {country_name}:")
    date = st.date_input("Voer de datum in:").strftime("%Y-%m-%d")
    start_time = st.time_input("Voer de starttijd in:").strftime("%H:%M")
    end_time = st.time_input("Voer de eindtijd in:").strftime("%H:%M")

    # Knop om gegevens op te halen
    if st.button("Gegevens ophalen"):
        # Simuleer het ophalen van gegevens (in jouw geval bijvoorbeeld API-aanroep)
        st.write(f"Gegevens ophalen voor {location_name}, {country_name} op {date} van {start_time} tot {end_time}")
        
        # Pop-up effect met HTML en CSS (overlay)
        st.markdown("""
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        padding: 20px; background-color: rgba(0, 0, 0, 0.8); color: white;
                        border-radius: 10px; z-index: 9999;">
                <h2>Hello World!</h2>
                <p>Dit is een pop-up venster die zichtbaar wordt na het ophalen van de gegevens.</p>
            </div>
        """, unsafe_allow_html=True)

# Voer de main functie uit
if __name__ == "__main__":
    main()
