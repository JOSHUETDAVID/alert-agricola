# src/constants.py

# --- CONFIGURACIÓN DE LA UBICACIÓN ---
LATITUD_MONTERIA = 8.7296
LONGITUD_MONTERIA = -75.8650

# --- ENDPOINTS DE API (Primario) ---
URL_OPENWEATHER_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
URL_OPENMETEO_FORECAST = "https://api.open-meteo.com/v1/forecast"

# --- RUTAS DE ARCHIVOS ---
DATA_FILE_PATH_FORECAST = "data/raw/openweather_forecast.csv"
DATA_FILE_PATH_HISTORICAL = "data/raw/openmeteo_historical_monteria.csv"
DATA_FILE_PATH_USERS = "data/users.csv"