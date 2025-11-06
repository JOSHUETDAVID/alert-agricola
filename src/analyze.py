# src/analyze.py
import pandas as pd
import numpy as np
from typing import Tuple, Optional

# --- 1. FUNCIÓN DE CÁLCULO DE UMBRAL (LOGICA DE NEGOCIO) ---

def calculate_historical_threshold(df_historical: pd.DataFrame, ith_col: str = 'ITH') -> Optional[float]:
    """
    Calcula el umbral de riesgo (Media Histórica del ITH).
    
    Regla de Negocio: Usamos el percentil 75 (P75) para definir un umbral "Alto", 
    ya que representa un valor al que la zona ya se ha adaptado. Si el pronóstico
    supera ese valor, es un riesgo inusual.
    """
    if df_historical.empty or ith_col not in df_historical.columns:
        print("Advertencia: Histórico vacío o ITH faltante. Umbral no calculado.")
        return None
    
    # Aseguramos que la columna ITH sea numérica
    df_historical[ith_col] = pd.to_numeric(df_historical[ith_col], errors='coerce')
    
    # Calculamos el percentil 75 (Q3)
    # Este será nuestro umbral de "Riesgo Alto" para Montería.
    threshold = df_historical[ith_col].quantile(0.75)

    print(f"EXITO: Umbral de Riesgo Histórico (P75 ITH): {threshold:.2f}")
    return threshold


# --- 2. FUNCIÓN DE ETIQUETADO DE RIESGO ---

def assign_risk_category(df_forecast: pd.DataFrame, threshold: float, ith_col: str = 'ITH') -> pd.DataFrame:
    """
    Asigna una categoría de riesgo al DataFrame de pronóstico basada en el umbral histórico.
    """
    if threshold is None or df_forecast.empty:
        df_forecast['risk'] = 'SIN DATOS'
        return df_forecast
    
    # Definición del riesgo basada en la lógica de negocio:
    # Si el ITH supera el umbral (P75 histórico), el riesgo es ALTO.
    df_forecast['risk'] = np.where(
        df_forecast[ith_col] > threshold,
        'RIESGO ALTO 🟥',
        'RIESGO MODERADO 🟨'
    )
    
    # Lógica de negocio adicional: si el ITH es > 70 (estrés leve para la ganadería),
    # el riesgo siempre debe ser al menos MODERADO.
    df_forecast['risk'] = np.where(
        (df_forecast[ith_col] > 70) & (df_forecast['risk'] == 'RIESGO MODERADO 🟨'),
        'RIESGO MODERADO 🟨',
        df_forecast['risk']
    )
    
    return df_forecast