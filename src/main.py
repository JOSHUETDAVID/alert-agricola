# src/main.py (ORQUESTADOR FINAL ESCALABLE)

from extract import (
    fetch_openweather_forecast, 
    fetch_openmeteo_forecast, 
    load_historical_data,
    load_user_data
)
from transform import standardize_and_clean_data, calculate_ith 
from analyze import calculate_historical_threshold, assign_risk_category 
from load import send_email_alert 
from ia_narrative import generate_risk_narrative # <--- Módulo IA
from constants import (
    URL_OPENWEATHER_FORECAST, 
    URL_OPENMETEO_FORECAST, 
    DATA_FILE_PATH_HISTORICAL,
    DATA_FILE_PATH_USERS
)
import pandas as pd 

from templates import generate_alert_html

# --- FUNCIONES DE SOPORTE PARA EL PIPELINE ---

def run_single_pipeline(lat: float, lon: float, ith_threshold: float):
    """
    Ejecuta el pipeline E-T-A completo para UNA única coordenada.
    """
    forecast_data = None
    
    # 1. Extracción Resiliente (E)
    forecast_data = fetch_openweather_forecast(URL_OPENWEATHER_FORECAST, lat, lon)
    if not forecast_data:
        forecast_data = fetch_openmeteo_forecast(URL_OPENMETEO_FORECAST, lat, lon)
    
    if not forecast_data:
        return None

    # 2. Transformación (T)
    # Se usa una simple verificación para saber qué fuente estandarizar
    source = "OpenWeatherMap" if forecast_data.get('city') else "OpenMeteo"
    df_forecast_standard = standardize_and_clean_data(forecast_data, source)
    if df_forecast_standard is None or df_forecast_standard.empty:
        return None

    # 3. Cálculo del ITH y Análisis (T-A)
    df_forecast_with_ith = calculate_ith(df_forecast_standard, temp_col='temperature_2m', hum_col='relative_humidity_2m')
    
    # Asignar riesgo usando el umbral histórico
    df_final_report = assign_risk_category(df_forecast_with_ith, ith_threshold)
    
    return df_final_report


# --- FUNCIÓN ORQUESTADORA ESCALABLE ---

def run_scalable_pipeline():
    print("--- INICIO DEL PROCESO ESCALABLE E-T-A-L ---")
    
    # 0. Cargar datos base (Usuarios e Histórico)
    df_users = load_user_data(DATA_FILE_PATH_USERS)
    df_historical = load_historical_data(DATA_FILE_PATH_HISTORICAL)
    
    if df_users.empty or df_historical.empty:
        print("--- FALLO: Base de usuarios o Histórico vacíos. Deteniendo.")
        return

    # 1. Calcular Umbral Histórico GLOBAL
    df_historical_ith = calculate_ith(df_historical, temp_col='temperature_2m', hum_col='relative_humidity_2m')
    ith_threshold = calculate_historical_threshold(df_historical_ith)
    
    if ith_threshold is None:
        print("--- FALLO: No se pudo calcular el umbral histórico. Deteniendo.")
        return

    print(f"\n2. Iniciando Bucle de Envío para {len(df_users)} fincas (Umbral Global: {ith_threshold:.2f})...")
    
    # 2. BUCLÉ DE ESCALABILIDAD (Iterar sobre cada usuario)
    for index, user in df_users.iterrows():
        print(f"\n  > Procesando Finca: {user['farm_name']} ({user['product_type']}) - Lat:{user['latitude']:.2f}, Lon:{user['longitude']:.2f}")

        # 2.1 E-T-A: Ejecutar pipeline para las coordenadas de la finca
        df_alert = run_single_pipeline(
            lat=user['latitude'], 
            lon=user['longitude'], 
            ith_threshold=ith_threshold
        )
        
        if df_alert is None:
            print(f"   --- ALERTA Saltando envío para {user['farm_name']} por falta de datos de pronóstico.")
            continue
            
        # 2.2 Generar Contenido (NARRATIVA IA)
        print("    > Generando narrativa con IA...")
        subject, ai_generated_body = generate_risk_narrative(
            df_alert, 
            user_type=user['product_type'], 
            ith_threshold=ith_threshold, 
            farm_name=user['farm_name']
        )
        print(f"    > Asunto generado: {subject}")

        #Llama a la función del template para construir el HTML ---
        html_body = generate_alert_html(
            farm_name=user['farm_name'],
            product_type=user['product_type'],
            ith_threshold=ith_threshold,
            ai_generated_body=ai_generated_body
        )

        # 2.3 Carga (L): Envío de correo
        send_email_alert(user['email'], subject, html_body)

    print("\n--- PROCESO DE ALERTA FINALIZADO ---")

if __name__ == "__main__":
    run_scalable_pipeline()