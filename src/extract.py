# src/extract.py (COMPLETO Y FUNCIONAL)
import requests
import pandas as pd
from os import getenv
from dotenv import load_dotenv
from typing import Optional, Dict
import os


load_dotenv() 
# Asegúrate de que esta clave exista en tu .env
API_KEY = getenv("OPENWEATHER_API_KEY") 

# =======================================================================
# 1. FUNCIONES DE EXTRACCIÓN (Fetch)
# =======================================================================

def fetch_openweather_forecast(url: str, lat: float, lon: float) -> Optional[Dict]:
    """
    Obtiene el pronóstico de 5 días / 3 horas de OpenWeatherMap.
    Devuelve el JSON completo o None si falla.
    """
    if not API_KEY:
        print("--- ERROR: OPENWEATHER_API_KEY no configurada.")
        return None
        
    try:
        # Nota: OpenWeather usa 'lat' y 'lon'
        response = requests.get(url, params={
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric', # Obtener temperatura en Celsius
            'lang': 'es'
        }, timeout=10)
        
        response.raise_for_status()  # Lanza excepción para códigos de error HTTP
        
        data = response.json()
        if data.get('cod') == '200':
            print(f"  --- EXITO Extracción exitosa de OpenWeatherMap.")
            return data
        else:
            print(f"  ---  ALERTA OpenWeatherMap devolvió código: {data.get('cod')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ---  ERROR de conexión/API de OpenWeatherMap: {e}")
        return None

def fetch_openmeteo_forecast(url: str, lat: float, lon: float) -> Optional[Dict]:
    """
    Obtiene el pronóstico de 7 días / 1 hora de Open-Meteo.
    Devuelve el JSON completo o None si falla.
    """
    try:
        # Nota: Open-Meteo usa 'latitude' y 'longitude'
        response = requests.get(url, params={
            'latitude': lat,
            'longitude': lon,
            'hourly': 'temperature_2m,relative_humidity_2m',
            'forecast_days': 2 # Solo necesitamos hoy y mañana para la alerta
        }, timeout=10)
        
        response.raise_for_status() 
        
        data = response.json()
        if 'hourly' in data:
            print(f"  --- EXITO Extracción exitosa de Open-Meteo (Fallback).")
            return data
        else:
            print(f"  --- ALERTA Open-Meteo no devolvió datos horarios.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  --- ERROR de conexión/API de Open-Meteo: {e}")
        return None

# =======================================================================
# 2. FUNCIONES DE CARGA (Load)
# =======================================================================

def load_historical_data(file_path: str) -> pd.DataFrame:
    """
    Carga el archivo CSV histórico (para el umbral) y limpia las columnas.
    """
    if not os.path.exists(file_path):
        print(f"  --- ERROR: No se encontró el archivo histórico en la ruta: {file_path}")
        return pd.DataFrame() 
        
    try:
        df_historical = pd.read_csv(file_path, parse_dates=['time'])
        
        # Limpieza de nombres de columnas (quita unidades como (C) o (%))
        df_historical.columns = df_historical.columns.str.replace(r' \(.*\)', '', regex=True)
        df_historical.columns = df_historical.columns.str.lower().str.strip()

        required_cols = ['time', 'temperature_2m', 'relative_humidity_2m']
        if not all(col in df_historical.columns for col in required_cols):
             print(f"FALLO: El CSV histórico no contiene todas las columnas requeridas tras la limpieza.")
             return pd.DataFrame()

        # Asegurar el formato de tiempo
        df_historical['time'] = pd.to_datetime(df_historical['time'])

        print(f"  --- EXITO Histórico cargado exitosamente: {len(df_historical)} registros.")
        return df_historical
        
    except Exception as e:
        print(f"  --- ERROR al cargar el histórico: {e}")
        return pd.DataFrame()

def load_user_data(file_path: str) -> pd.DataFrame:
    """
    Carga la lista de usuarios (coordenadas y correos) para los envíos masivos.
    """
    if not os.path.exists(file_path):
        print(f"  --- ERROR: No se encontró el archivo de usuarios en la ruta: {file_path}")
        return pd.DataFrame()
    try:
        df_users = pd.read_csv(file_path)
        
        # Convertir a float para evitar errores en las llamadas a la API
        df_users['latitude'] = pd.to_numeric(df_users['latitude'], errors='coerce')
        df_users['longitude'] = pd.to_numeric(df_users['longitude'], errors='coerce')

        print(f"  --- EXITO Base de datos de {len(df_users)} usuarios cargada.")
        return df_users
    except Exception as e:
        print(f"  --- ERROR al cargar usuarios: {e}")
        return pd.DataFrame()