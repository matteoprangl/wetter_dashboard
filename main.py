import streamlit as st
from weather_api import get_weather_forecast

st.title("🌤️ Mein persönliches Wetter-Dashboard")
st.write("Willkommen zu deinem eigenständigen Python-Projekt! Hier analysieren und visualisieren wir Live-Wetterdaten.")

# Sidebar für die Auswahl
st.sidebar.header("Einstellungen")
city = st.sidebar.selectbox(
    "Wähle eine Stadt:",
    ["Wien", "Berlin", "Zürich", "London", "New York"]
)

# Koordinaten-Zuordnung für die Auswahl
coordinates = {
    "Wien": (48.2082, 16.3738),
    "Berlin": (52.52, 13.405),
    "Zürich": (47.3769, 8.5417),
    "London": (51.5074, -0.1278),
    "New York": (40.7128, -74.0060)
}

lat, lon = coordinates[city]

# Daten laden
with st.spinner(f"Lade Wetterdaten für {city}..."):
    df = get_weather_forecast(lat, lon, city)

if df is not None:
    st.success(f"Daten für {city} erfolgreich geladen!")
    
    # Metriken / Kennzahlen oben anzeigen
    current_temp = df["Temperatur (°C)"].iloc[0]
    st.metric(label=f"Aktuelle Temperatur in {city}", value=f"{current_temp} °C")
    
    # Interaktives Diagramm für die Temperatur
    st.subheader("📈 Temperaturverlauf der nächsten Tage")
    st.line_chart(df.set_index("Zeit")["Temperatur (°C)"])
    
    # Rohdaten auf Wunsch anzeigen
    with st.expander("Rohdaten anzeigen"):
        st.dataframe(df)
else:
    st.error("Fehler beim Abrufen der Wetterdaten.")