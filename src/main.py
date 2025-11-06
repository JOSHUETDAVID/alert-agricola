# src/main.py (NUEVA ESTRUCTURA ESCALABLE E-T-A-L)

from extract import (
    fetch_openweather_forecast, 
    fetch_openmeteo_forecast, 
    load_historical_data,
    load_user_data # <--- NUEVA FUNCIÓN
)
from transform import standardize_and_clean_data, calculate_ith 
from analyze import calculate_historical_threshold, assign_risk_category 
from load import send_email_alert # <--- MÓDULO DE CORREO
from constants import (
    URL_OPENWEATHER_FORECAST, 
    URL_OPENMETEO_FORECAST, 
    DATA_FILE_PATH_HISTORICAL,
    DATA_FILE_PATH_USERS # <--- RUTA DE USUARIOS
)
import pandas as pd 
from datetime import datetime

# --- FUNCIONES DE SOPORTE PARA EL PIPELINE ---

def run_single_pipeline(lat: float, lon: float, user_type: str, ith_threshold: float):
    """
    Ejecuta el pipeline E-T-A completo para UNA única coordenada.
    Devuelve el DataFrame final del pronóstico con el ITH y riesgo.
    """
    forecast_data = None
    source = None
    
    # 1. Extracción Resiliente (E)
    forecast_data = fetch_openweather_forecast(URL_OPENWEATHER_FORECAST, lat, lon)
    if not forecast_data:
        forecast_data = fetch_openmeteo_forecast(URL_OPENMETEO_FORECAST, lat, lon)
    
    if not forecast_data:
        print(f"-- ALERTA -- No se pudo obtener el pronóstico para {lat},{lon}.")
        return None

    # 2. Transformación (T)
    df_forecast_standard = standardize_and_clean_data(forecast_data, "OpenWeatherMap" if forecast_data.get('city') else "OpenMeteo")
    if df_forecast_standard is None or df_forecast_standard.empty:
        return None

    # 3. Cálculo del ITH y Análisis (T-A)
    df_forecast_with_ith = calculate_ith(df_forecast_standard, temp_col='temperature_2m', hum_col='relative_humidity_2m')
    
    # Asignar riesgo usando el umbral histórico de Montería
    df_final_report = assign_risk_category(df_forecast_with_ith, ith_threshold)
    
    return df_final_report


# --- FUNCIÓN ORQUESTADORA ESCALABLE ---

def run_scalable_pipeline():
    print("--- INICIO DEL PROCESO ESCALABLE E-T-A-L ---")
    
    # 0. Cargar datos base (Usuarios e Histórico)
    df_users = load_user_data(DATA_FILE_PATH_USERS)
    df_historical = load_historical_data(DATA_FILE_PATH_HISTORICAL)
    
    if df_users.empty or df_historical.empty:
        print("-- FALLO --: Base de usuarios o Histórico vacíos. Deteniendo.")
        return

    # 1. Calcular Umbral Histórico GLOBAL (Se asume una media para toda Montería)
    df_historical_ith = calculate_ith(df_historical, temp_col='temperature_2m', hum_col='relative_humidity_2m')
    ith_threshold = calculate_historical_threshold(df_historical_ith)
    
    if ith_threshold is None:
        print("-- FALLO: No se pudo calcular el umbral histórico. Deteniendo.")
        return

    # 2. BUCLÉ DE ESCALABILIDAD (Iterar sobre cada usuario)
    print(f"\n2. Iniciando Bucle de Envío para {len(df_users)} fincas (Umbral: {ith_threshold:.2f})...")
    
    for index, user in df_users.iterrows():
        print(f"\n  > Procesando Finca: {user['farm_name']} ({user['product_type']})")

        # 2.1 E-T-A: Ejecutar pipeline para las coordenadas de la finca
        df_alert = run_single_pipeline(
            lat=user['latitude'], 
            lon=user['longitude'], 
            user_type=user['product_type'],
            ith_threshold=ith_threshold
        )
        
        if df_alert is None:
            print(f"-- ALERTA -- Saltando envío para {user['farm_name']} por falta de datos de pronóstico.")
            continue
            
        # 2.2 Generar Contenido (TEMPORAL: Aquí se integrará la IA mañana)
        # Aquí se usará la IA para generar el 'subject' y el 'body'
        subject = f"ALERTA TEMP. | ITH - RIESGO {user['product_type']} - {user['farm_name']}"
        body = (
            f"REPORTE DE ALERTA PARA {user['farm_name']} (Tipo: {user['product_type']}):\n\n"
            f"El umbral histórico de riesgo (P75) en la zona es de {ith_threshold:.2f}.\n\n"
            f"PRONÓSTICO DE RIESGO ALTO (ITH > {ith_threshold:.2f}):\n"
            f"{df_alert[df_alert['risk'].str.contains('ALTO')][['time', 'ITH']].to_string(index=False)}\n\n"
            "--- ESTO SERÁ LA NARRATIVA GENERADA POR GEMINI MAÑANA ---"
        )

        # 2.3 Carga (L): Envío de correo
        send_email_alert(user['email'], subject, body)


if __name__ == "__main__":
    # Asegúrate de haber creado el data/users.csv y configurado tu .env
    run_scalable_pipeline()