import streamlit as st
import pandas as pd
from weather_api import get_weather_data

# Seiteneinstellung für das Smartphone optimieren
st.set_page_config(page_title="Mein Wetter", page_icon="⛅", layout="centered")

# --- WMO Wetter-Code Übersetzung in Emojis & Klartext ---
def get_weather_description(code):
    weather_mapping = {
        0: ("☀️", "Klarer Himmel"),
        1: ("🌤️", "Überwiegend klar"),
        2: ("⛅", "Teilweise bewölkt"),
        3: ("☁️", "Bedeckt"),
        45: ("🌫️", "Nebel"),
        48: ("🌫️", "Reifnebel"),
        51: ("🌧️", "Leichter Nieselregen"),
        53: ("🌧️", "Mäßiger Nieselregen"),
        55: ("🌧️", "Dichter Nieselregen"),
        61: ("🌧️", "Leichter Regen"),
        63: ("🌧️", "Mäßiger Regen"),
        65: ("🌧️", "Starker Regen"),
        71: ("🌨️", "Leichter Schneefall"),
        73: ("🌨️", "Mäßiger Schneefall"),
        75: ("🌨️", "Starker Schneefall"),
        95: ("⛈️", "Gewitter")
    }
    return weather_mapping.get(code, ("🌦️", "Unbekannt"))

# --- STRECKE / ORTE AUSWÄHLEN BEIM START ---
st.title("⛅ Mein Wetter-Dashboard")

# Vordefinierte Orte zur Auswahl (kannst du beliebig erweitern)
staedte = {
    "Wien": (48.2082, 16.3738),
    "Graz": (47.0707, 15.4395),
    "Linz": (48.3069, 14.2858),
    "Salzburg": (47.8095, 13.0550),
    "Innsbruck": (47.2692, 11.4041),
    "Berlin": (52.5200, 13.4050),
    "Zürich": (47.3769, 8.5417)
}

selected_city = st.selectbox("📍 Wähle deinen Ort:", list(staedte.keys()))
lat, lon = staedte[selected_city]

# Wetter-Daten laden
data = get_weather_data(lat, lon)

if data:
    # Aktuelle Stunde herausfinden (erste Zeile der Stundendaten)
    hourly = data.get("hourly", {})
    df_hourly = pd.DataFrame({
        "Zeit": pd.to_datetime(hourly.get("time")),
        "Temperatur": hourly.get("temperature_2m"),
        "Regen-Chance": hourly.get("precipitation_probability", [0]*len(hourly.get("time"))),
        "Code": hourly.get("weather_code")
    })
    
    daily = data.get("daily", {})
    df_daily = pd.DataFrame({
        "Datum": pd.to_datetime(daily.get("time")),
        "Max Temp": daily.get("temperature_2m_max"),
        "Min Temp": daily.get("temperature_2m_min"),
        "Code": daily.get("weather_code")
    })

    # --- OBEN: AKTUELLES WETTER (HEUTE) ---
    current_temp = round(df_hourly.loc[0, "Temperatur"])
    current_code = df_hourly.loc[0, "Code"]
    emoji, beschreibung = get_weather_description(current_code)

    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"<h1 style='text-align: center;'>{emoji}</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### {selected_city}")
        st.markdown(f"**{current_temp}°C** – {beschreibung}")
    st.markdown("---")

    # --- UNTEN: 14 TAGE VORSCHAU ALS KLICKBARE KACHELN ---
    st.subheader("📅 14-Tage-Vorschau")
    st.caption("Tippe auf einen Tag, um die 24-Stunden-Details anzusehen:")

    for index, row in df_daily.iterrows():
        tag_str = row["Datum"].strftime("%A, %d. %b")
        max_t = round(row["Max Temp"])
        min_t = round(row["Min Temp"])
        day_code = row["Code"]
        day_emoji, day_desc = get_weather_description(day_code)
        
        # Jede Kachel ist ein aufklappbarer Tag
        with st.expander(f"{day_emoji}  {tag_str}   |   🌡️ {max_t}°C / {min_t}°C  ({day_desc})"):
            
            # Filtere die Stunden für diesen exakten Tag heraus
            tag_datum = row["Datum"].date()
            df_stunden_heute = df_hourly[df_hourly["Zeit"].dt.date == tag_datum]
            
            if not df_stunden_heute.empty:
                st.markdown("**Stündlicher Verlauf:**")
                
                # Tabelle für die 24 Stunden aufbereiten
                display_df = df_stunden_heute.copy()
                display_df["Uhrzeit"] = display_df["Zeit"].dt.strftime("%H:%M")
                display_df["Wetter"] = display_df["Code"].apply(lambda c: get_weather_description(c)[1])
                display_df["Temp (°C)"] = display_df["Temperatur"]
                display_df["Regen (%)"] = display_df["Regen-Chance"]
                
                display_df = display_df[["Uhrzeit", "Wetter", "Temp (°C)", "Regen (%)"]]
                
                st.dataframe(display_df.set_index("Uhrzeit"), use_container_width=True)
            else:
                st.info("Keine Stundendaten verfügbar.")

else:
    st.error("Fehler beim Laden der Wetterdaten.")
