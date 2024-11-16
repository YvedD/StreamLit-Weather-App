import tkinter as tk
from tkinter import ttk, messagebox
import requests
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster
from io import BytesIO
from PIL import Image, ImageTk
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Functie om een kaart te maken en een marker op de locatie te zetten
def update_map(location_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(location_name)
    
    if location is None:
        messagebox.showerror("Fout", f"Locatie '{location_name}' niet gevonden.")
        return None

    # Maak de kaart met een marker voor de opgegeven locatie
    map_center = [location.latitude, location.longitude]
    m = folium.Map(location=map_center, zoom_start=6)
    folium.Marker(location=map_center, popup=location_name, tooltip="Locatie").add_to(m)
    
    # Converteer kaart naar een afbeelding om in de GUI weer te geven
    data = BytesIO()
    m.save(data, close_file=False)
    data.seek(0)
    return Image.open(data)

# Functie om windrichting om te zetten naar afkortingen
def degrees_to_direction(degrees):
    directions = ['N', 'NNO', 'NO', 'ONO', 'O', 'OZO', 'ZO', 'ZZO', 'Z', 'ZZW', 'ZW', 'WZW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]

# Functie om windsnelheid om te zetten naar de Beaufort-schaal
def kmh_to_beaufort(kmh):
    if kmh < 1:
        return 0
    elif kmh <= 5:
        return 1
    elif kmh <= 11:
        return 2
    elif kmh <= 19:
        return 3
    elif kmh <= 28:
        return 4
    elif kmh <= 38:
        return 5
    elif kmh <= 49:
        return 6
    elif kmh <= 61:
        return 7
    elif kmh <= 74:
        return 8
    elif kmh <= 88:
        return 9
    elif kmh <= 102:
        return 10
    elif kmh <= 117:
        return 11
    else:
        return 12

# Functie om weergegevens op te halen en te tonen
def get_weather():
    location_name = location_entry.get().strip()
    start_hour = start_hour_combobox.get()
    end_hour = end_hour_combobox.get()

    if not location_name or not start_hour or not end_hour:
        messagebox.showerror("Fout", "Vul alstublieft alle velden in.")
        return

    # Verwijder eerdere resultaten uit de listbox
    listbox.delete(0, tk.END)

    # Toon kaart met marker
    map_image = update_map(location_name)
    if map_image:
        map_image_tk = ImageTk.PhotoImage(map_image)
        map_label.config(image=map_image_tk)
        map_label.image = map_image_tk

    # Haal weergegevens op en toon in listbox (deze sectie blijft nagenoeg hetzelfde als eerder)
    # ...

# Functie om geselecteerde weergegevens te tonen
def show_weather(event):
    selection = event.widget.curselection()
    if not selection:
        return

    index = selection[0]
    location_name = event.widget.get(index)
    data = weather_data.get(location_name)

    if data is None or isinstance(data, str):
        messagebox.showerror("Fout", f"Geen weergegevens beschikbaar voor {location_name}.")
        return

    hourly = data['hourly']
    hours = list(range(len(hourly['temperature_2m'])))
    temperatures = hourly['temperature_2m']
    wind_speeds = [kmh_to_beaufort(speed) for speed in hourly['wind_speed_10m']]
    wind_directions = hourly['wind_direction_10m']
    cloudcover = hourly.get('cloudcover', [])
    precipitation = hourly.get('precipitation', [])
    visibility = hourly.get('visibility', [])

    # Alleen wijzigingen in windrichting weergeven
    wind_directions_text = []
    previous_direction = None
    for deg in wind_directions:
        current_direction = degrees_to_direction(deg)
        if current_direction != previous_direction:
            wind_directions_text.append(current_direction)
            previous_direction = current_direction
        else:
            wind_directions_text.append('')  # Geen label weergeven

    # Plotten met Seaborn
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=hours, y=temperatures, label='Temperatuur (°C)')
    sns.lineplot(x=hours, y=wind_speeds, label='Windsnelheid (Beaufort)')
    sns.lineplot(x=hours, y=cloudcover, label='Bewolkingsgraad (%)')
    sns.lineplot(x=hours, y=visibility, label='Zichtbaarheid (km)')
    sns.lineplot(x=hours, y=precipitation, label='Neerslag (mm)')

    plt.title(f"Weerdata voor {location_name}")
    plt.xlabel('Uren vanaf start')
    plt.ylabel('Waarden')
    plt.legend(loc='upper right')
    plt.grid(True)

    # Voeg windrichtingen toe als tekstlabels op de x-as
    for i in range(len(hours)):
        if wind_directions_text[i]:  # Alleen labels als er een verandering is
            plt.text(hours[i], wind_speeds[i], wind_directions_text[i], fontsize=8, rotation=45)

    plt.show()

# Tkinter GUI
root = tk.Tk()
root.title("Weerdata Opvragen")

# Lijst met volle uren voor de combobox
hours_list = [f"{hour:02d}:00" for hour in range(24)]

# Kaart weergeven bovenaan in de GUI
map_label = tk.Label(root)
map_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# Labels en invoervelden
tk.Label(root, text="Locatie:").grid(row=1, column=0, padx=10, pady=10)
location_entry = tk.Entry(root, width=30)
location_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Begin Uur:").grid(row=2, column=0, padx=10, pady=10)
start_hour_combobox = ttk.Combobox(root, values=hours_list, state="readonly", width=5)
start_hour_combobox.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Eind Uur:").grid(row=3, column=0, padx=10, pady=10)
end_hour_combobox = ttk.Combobox(root, values=hours_list, state="readonly", width=5)
end_hour_combobox.grid(row=3, column=1, padx=10, pady=10)

# Listbox om resultaten te tonen
listbox = tk.Listbox(root, height=10, width=50)
listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
listbox.bind('<<ListboxSelect>>', show_weather)

# Knop om weergegevens op te halen
tk.Button(root, text="Haal Weerdata Op", command=get_weather).grid(row=5, column=0, columnspan=2, pady=10)

# Variabele om weergegevens op te slaan
weather_data = {}

# Start de GUI
root.mainloop()
