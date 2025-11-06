# src/transform.py
from turtle import st
import numpy as np
import pandas as pd
from typing import Optional, Dict

# --- 1. FUNCIÓN DE LIMPIEZA / PREPARACIÓN DE DATOS (LISKOV) ---

def standardize_and_clean_data(raw_data: Dict, source: str) -> Optional[pd.DataFrame]:
    """
    Convierte el diccionario crudo (OpenWeather o OpenMeteo) a un DataFrame estándar 
    para cumplir con Liskov (ambos outputs deben ser sustituibles).
    
    Columnas Objetivo (Target): ['time', 'temperature_2m', 'relative_humidity_2m']
    """
    if not raw_data:
        return None
        
    if source == "OpenWeatherMap":
        # Mapeo de datos de OpenWeather a nuestro estándar
        list_data = raw_data.get('list', [])
        records = []
        for item in list_data:
            records.append({
                'time': item.get('dt_txt'),
                'temperature_2m': item.get('main', {}).get('temp'),
                'relative_humidity_2m': item.get('main', {}).get('humidity')
            })
        df = pd.DataFrame(records)
        
    elif source == "OpenMeteo":
        # Mapeo de datos de OpenMeteo a nuestro estándar
        hourly_data = raw_data.get('hourly', {})
        df = pd.DataFrame({
            'time': hourly_data.get('time', []),
            'temperature_2m': hourly_data.get('temperature_2m', []),
            'relative_humidity_2m': hourly_data.get('relative_humidity_2m', [])
        })

    else:
        print(f"Advertencia: Fuente de datos desconocida: {source}")
        return None

    # Limpieza básica y garantía de tipo de dato
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df['temperature_2m'] = pd.to_numeric(df['temperature_2m'], errors='coerce')
    df['relative_humidity_2m'] = pd.to_numeric(df['relative_humidity_2m'], errors='coerce')
    
    # Eliminar filas con valores nulos generados por errores de conversión
    df.dropna(subset=['time', 'temperature_2m', 'relative_humidity_2m'], inplace=True)
    
    return df


# --- 2. FUNCIÓN DE CÁLCULO DE ITH ---

def calculate_ith(df, temp_col , hum_col: str) -> pd.DataFrame:
    """
    Calcula el Índice de Temperatura y Humedad (ITH) utilizando la fórmula
    proporcionada por el usuario (versión adaptada a grados Celsius).
    Fórmula: ITH = (1.8*T + 32) - (0.55 - 0.55*HR%/100) * (1.8*T - 26)
    """
    if df.empty or temp_col not in df.columns or hum_col not in df.columns:
        print("Advertencia: DataFrame vacío o columnas ITH faltantes. Retornando sin ITH.")
        return df

    # 1. Extraer los arrays de NumPy
    temp_c = df[temp_col].values
    hum_rel = df[hum_col].values

    # 2. CALCULAR EL ITH CON LA FÓRMULA CORREGIDA
    
    # Paréntesis 1: (1.8 * T + 32)
    ith = (1.8 * temp_c + 32) - (0.55 - 0.55 * hum_rel / 100) * (1.8 * temp_c - 26)

    
    df['ITH'] = ith
    
    return df
