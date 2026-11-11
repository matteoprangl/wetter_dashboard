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

# --- ORTSAUSWAHL ---
st.title("⛅ Wetter")

staedte = {
    "Wien": (48.2082, 16.3738),
    "Graz": (47.0707, 15.4395),
    "Linz": (48.3069, 14.2858),
    "Salzburg": (47.8095, 13.0550),
    "Innsbruck": (47.2692, 11.4041),
    "Berlin": (52.5200, 13.4050),
    "Zürich": (47.3769, 8.5417)
}

selected_city = st.selectbox("📍 Standort wählen:", list(staedte.keys()))
lat, lon = staedte[selected_city]

# Wetter-Daten laden
data = get_weather_data(lat, lon)

if data:
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

    # --- OBEN: AKTUELLES WETTER ---
    current_temp = round(df_hourly.loc[0, "Temperatur"])
    current_code = df_hourly.loc[0, "Code"]
    emoji, beschreibung = get_weather_description(current_code)

    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"<h1 style='text-align: center; margin:0;'>{emoji}</h1>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"### {selected_city}")
        st.markdown(f"**{current_temp}°C** &bull; {beschreibung}")
    st.markdown("---")

    # --- SESSION STATE FÜR DIE DETAILANSICHT ---
    # Das merkt sich, welchen Tag der Nutzer angeklickt hat, wie eine echte App-Navigation
    if "selected_day" not in st.session_state:
        st.session_state.selected_day = None

    # Wenn ein Tag ausgewählt wurde, zeigen wir die Detail-Ansicht im "Swipe-Stil"
    if st.session_state.selected_day is not None:
        tag_datum = st.session_state.selected_day
        tag_str = pd.to_datetime(tag_datum).strftime("%A, %d. %b %Y")
        
        # Zurück-Button
        if st.button("⬅️ Zurück zur 14-Tage-Übersicht"):
            st.session_state.selected_day = None
            st.rerun()

        st.subheader(f"📅 Details für {tag_str}")
        st.caption("Stündlicher Verlauf im Überblick:")

        # Filtere die Stunden für diesen Tag
        df_stunden_heute = df_hourly[df_hourly["Zeit"].dt.date == tag_datum]

        if not df_stunden_heute.empty:
            # Wir bauen kleine Kacheln/Spalten für jede Stunde nebeneinander (wie ein Swipe-Bereich)
            # Damit es übersichtlich bleibt, zeigen wir alle 3 Stunden einen kompakten Block oder horizontal
            cols = st.columns(len(df_stunden_heute))
            
            # Da 24 Spalten nebeneinander auf dem Handy zu klein wären, 
            # lösen wir es über eine schicke, kompakte Horizontaltabelle oder Kachel-Container:
            for idx, row in df_stunden_heute.iterrows():
                uhrzeit = row["Zeit"].strftime("%H:%M")
                temp = round(row["Temperatur"])
                regen = row["Regen-Chance"]
                code = row["Code"]
                h_emoji, _ = get_weather_description(code)
                
                # Jede Stunde bekommt eine kleine, moderne Karte nebeneinander/untereinander in Blöcken
                with st.container():
                    col_u, col_i, col_t, col_r = st.columns([2, 1, 1, 1])
                    col_u.write(f"⏰ **{uhrzeit} Uhr**")
                    col_i.write(h_emoji)
                    col_t.write(f"🌡️ **{temp}°C**")
                    col_r.write(f"🌧️ {regen}%")
                    st.divider()
        else:
            st.info("Keine Daten für diesen Tag.")

    else:
        # --- DIE 14-TAGE-ÜBERSICHT (KACHELN) ---
        st.subheader("📅 14-Tage-Vorschau")
        st.caption("Klicke auf einen Tag, um die Stunden-Ansicht zu öffnen:")

        for index, row in df_daily.iterrows():
            tag_datum = row["Datum"].date()
            tag_str = row["Datum"].strftime("%a, %d. %b") # z.B. Mo, 16. Nov
            max_t = round(row["Max Temp"])
            min_t = round(row["Min Temp"])
            day_code = row["Code"]
            day_emoji, day_desc = get_weather_description(day_code)
            
            # Jede Zeile ist jetzt ein schicker Klick-Button, der sich wie eine App anfühlt
            col_kachel_1, col_kachel_2 = st.columns([3, 1])
            with col_kachel_1:
                st.markdown(f"**{day_emoji} {tag_str}** &nbsp;&nbsp; `{min_t}°C` ➔ `**{max_t}°C**` &nbsp; *({day_desc}*)")
            with col_kachel_2:
                if st.button("Details ➔", key=f"btn_{index}"):
                    st.session_state.selected_day = tag_datum
                    st.rerun()
            
            st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)

else:
    st.error("Fehler beim Laden der Wetterdaten.")
