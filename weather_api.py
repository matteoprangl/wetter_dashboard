import requests
import pandas as pd

def get_weather_forecast(lat, lon, city_name):
    """
    Holt das aktuelle Wetter und die Vorhersage für gegebene Koordinaten von Open-Meteo.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,relative_humidity_2m"
    
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    data = response.json()
    
    # Wir wandeln die stündlichen Daten in ein sauberes Pandas DataFrame um
    hourly_data = data.get("hourly", {})
    df = pd.DataFrame({
        "Zeit": pd.to_datetime(hourly_data.get("time")),
        "Temperatur (°C)": hourly_data.get("temperature_2m"),
        "Regen (mm)": hourly_data.get("precipitation"),
        "Luftfeuchtigkeit (%)": hourly_data.get("relative_humidity_2m")
    })
    
    return df