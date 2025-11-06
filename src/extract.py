# src/extract.py
import requests
import pandas as pd
from os import getenv
from dotenv import load_dotenv
from typing import Optional, Dict # <--- IMPORTANTE: Importar Optional y Dict
import os

# Carga las variables del archivo .env al entorno
load_dotenv() 

# La API Key se obtiene de forma segura
API_KEY = getenv("OPENWEATHER_API_KEY")

# === CORRECCIÓN CLAVE: La firma de la función ahora es honesta ===
# Devolverá un diccionario (Dict) si es exitosa, o None si falla.
def fetch_openweather_forecast(url: str, lat: float, lon: float) -> Optional[Dict]:
    """
    Obtiene el pronóstico de 5 días de OpenWeatherMap.
    Su única responsabilidad es hacer la petición y devolver los datos crudos.
    """
    if not API_KEY:
        raise ValueError("ERROR CRÍTICO: La API_KEY no está cargada.")

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"  # Para obtener la temperatura en Celsius
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Lanza un HTTPError si la respuesta es 4xx o 5xx
        
        data = response.json()
        
        # Devolvemos el diccionario crudo (Dict)
        return data

    except requests.exceptions.RequestException as e:
        print(f"FALLO CRÍTICO DE EXTRACCIÓN (OpenWeather): {e}")
        # Retornamos None, lo cual ahora es válido gracias a 'Optional[Dict]'
        return None

# =======================================================================
# 2. FUNCIÓN DE EXTRACCIÓN FALLBACK (Open-Meteo)
# =======================================================================

def fetch_openmeteo_forecast(url: str, lat: float, lon: float) -> Optional[Dict]:
    """
    Obtiene el pronóstico de Open-Meteo como proveedor de fallback.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "forecast_days": 5, 
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return data

    except requests.exceptions.RequestException as e:
        print(f"FALLO CRÍTICO DE EXTRACCIÓN (Open-Meteo Fallback): {e}")
        return None

# =======================================================================
# 3. FUNCIÓN DE CARGA DE DATOS HISTÓRICOS (Load Local File)
# =======================================================================

def load_historical_data(file_path: str) -> pd.DataFrame:
    """
    Carga el archivo CSV histórico de Open-Meteo desde el disco.
    Esta es la función L (Load) en el contexto de un archivo local.
    """
    if not os.path.exists(file_path):
        print(f" ERROR: No se encontró el archivo histórico en la ruta: {file_path}")
        return pd.DataFrame() # Devuelve un DataFrame vacío si el archivo no existe
        
    try:
        # Usamos parse_dates para asegurar que la columna 'time' sea tipo datetime
        df_historical = pd.read_csv(
            file_path, 
            parse_dates=['time']
        )
        print(f"EXITO: Histórico cargado exitosamente: {len(df_historical)} registros.")
        return df_historical
        
    except Exception as e:
        print(f" ERROR al cargar el histórico: {e}")
        return pd.DataFrame()
    
def load_user_data(file_path: str) -> pd.DataFrame:
    """
    Carga la lista de usuarios (coordenadas y correos) para los envíos masivos.
    """
    if not os.path.exists(file_path):
        print(f"❌ ERROR: No se encontró el archivo de usuarios en la ruta: {file_path}")
        return pd.DataFrame()
    try:
        df_users = pd.read_csv(file_path)
        print(f"-- EXITO -- Base de datos de {len(df_users)} usuarios cargada.")
        return df_users
    except Exception as e:
        print(f"-- FRACASO -- ERROR al cargar usuarios: {e}")
        return pd.DataFrame()