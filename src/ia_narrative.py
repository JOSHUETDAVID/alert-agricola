# src/ia_narrative.py
import pandas as pd
from google import genai
from os import getenv
from dotenv import load_dotenv
from typing import Tuple
from datetime import datetime

# Carga la API Key de Gemini
load_dotenv()
GEMINI_API_KEY = getenv("GEMINI_API_KEY")

# Inicializa el cliente de Gemini (Global)
# Si la clave es inválida o no está, 'client' será None
client = None
try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        print("ADVERTENCIA: GEMINI_API_KEY no encontrada. La IA usará un mensaje de fallback.")
except Exception as e:
    print(f"Error inicializando el cliente Gemini: {e}")

# --- DOCUMENTACIÓN DEL USUARIO (Plan de Prevención Limpio) ---
# Este texto actúa como la 'memoria' de la IA para las recomendaciones
PREVENTION_DOCUMENTATION = """
### CONTEXTO: Plan de Prevención y Mitigación de Estrés Térmico (ITH)
DESCRIPCION: Documento para Ganaderos de Carne y Leche Enfocados en la Eficiencia Productiva.
PRINCIPIO_BASE: El estrés térmico es la principal amenaza a la rentabilidad ganadera. El ITH permite la prevención proactiva para proteger: Ganancia de Peso, Producción de Leche y Crianza Estructurada.
SECCION: I
OBJETIVO: Ganancia de Peso (Bovinos de Carne)
RIESGO_NIVEL: ITH >= 75 (Alerta)
MEDIDA_PREVENCION: Ajuste Hídrico: Incrementar la disponibilidad de agua fresca y potable en un 15-25% más de lo habitual. Revisar bebederos dos veces al día para asegurar flujo y limpieza.
IMPACTO_NO_EJECUCION: Caída de Ingesta y Eficiencia. Pérdida de Peso Diaria (PPD) por ineficiencia digestiva y metabólica.
FRECUENCIA_EJECUCION: Diario, monitoreo constante.
RIESGO_NIVEL: ITH >= 79 (Peligro)
MEDIDA_PREVENCION: Ajuste Nutricional: Modificar la rutina de alimentación. Mover la alimentación concentrada (la de mayor generación de calor metabólico) a las horas más frescas (tarde-noche, entre 6 PM y 8 AM).
IMPACTO_NO_EJECUCION: Riesgo de Acidosis y PPD. Pérdida aguda y reversible de PPD por acidosis ruminal.
FRECUENCIA_EJECUCION: Durante la ola de calor.
RIESGO_NIVEL: ITH >= 84 (Emergencia)
MEDIDA_PREVENCION: Implementación de Refugios/Aspersión: Limitar drásticamente el movimiento. Mover el ganado a las zonas de sombra más densa y usar sistemas de aspersión y ventilación forzada si están disponibles, especialmente en los corrales de espera o comederos.
IMPACTO_NO_EJECUCION: Estrés Severo y Morbilidad. Pérdida de PPD irreversible y riesgo de mortalidad.
FRECUENCIA_EJECUCION: Inmediato, a cada hora.
SECCION: II
OBJETIVO: Producción de Leche (Bovinos Lecheros)
RIESGO_NIVEL: ITH > 72 (Alerta)
MEDIDA_PREVENCION: Optimización del Pastoreo/Descanso: Evitar el pastoreo o el encierro en corrales de espera durante las horas de 10 AM a 4 PM. Asegurar que haya sombra suficiente (natural o artificial) en el área de descanso post-ordeño.
IMPACTO_NO_EJECUCION: Disminución Leve de Producción (5-10%). La vaca redirige energía del mantenimiento al control térmico.
FRECUENCIA_EJECUCION: Diario, durante las horas pico.
RIESGO_NIVEL: ITH >= 75 (Peligro)
MEDIDA_PREVENCION: Refrigeración en Ordeño: Reducir el tiempo de espera en el corral de ordeño a un máximo de 60 minutos. Implementar aspersión (ducha) y ventilación forzada en el corral de espera inmediatamente antes del ordeño.
IMPACTO_NO_EJECUCION: Descenso Significativo (10-25%). Pérdida de litros de leche y descenso de la calidad (sólidos) por reducción drástica del consumo.
FRECUENCIA_EJECUCION: Durante la ola de calor.
RIESGO_NIVEL: ITH >= 79 (Emergencia)
MEDIDA_PREVENCION: Protocolo de Enfriamiento Extremo: Aplicar duchas intermitentes de alta intensidad (3-5 minutos cada 15-20 minutos) y forzar la ventilación para maximizar el enfriamiento evaporativo en la zona de espera o comedero. Usar bloques de hielo en los bebederos.
IMPACTO_NO_EJECUCION: Falla Reproductiva y Cetosis. Impacto negativo a largo plazo en la fertilidad del hato (días abiertos, concepción) e incremento de mastitis.
FRECUENCIA_EJECUCION: Inmediato, a cada hora.
SECCION: III
OBJETIVO: Crianza Estructurada (Terneros y Reproductores)
FACTOR_CRITICO: Terneros (0-3 meses)
MEDIDA_PREVENCION: Control de la Humedad en Cunas/Corrales: Asegurar que las camas/corrales estén secos. Proveer agua fresca constantemente, incluso si aún están con leche.
IMPACTO_NO_EJECUCION: Aumento de Morbilidad y Deshidratación. Retraso en el desarrollo y destete.
MONITOREO_SUGERIDO: Revisar la frecuencia respiratoria (jadeo) 3 veces al día.
FACTOR_CRITICO: Reproductores (Toros y Vacas)
MEDIDA_PREVENCION_TOROS: Manejo de Toros: Proteger a los toros reproductores con sombra densa 24/7. Evitar la monta natural o la colecta de semen en periodos de ITH > 75.
MEJOR_MOMENTO_APAREAMIENTO: El momento óptimo para realizar la monta natural o la Inseminación Artificial (IA) es durante las horas más frescas del día (tarde-noche, después de las 6 PM, o temprano en la mañana, antes de las 8 AM) para minimizar el estrés térmico de la hembra y el macho/semen y maximizar la tasa de concepción.
IMPACTO_NO_EJECUCION: Impacto Agudo en la Fertilidad. El efecto en el toro puede durar hasta 8 semanas. Incremento drástico en días abiertos y tasa de concepción baja en vacas.
MONITOREO_SUGERIDO: Monitorear el consumo de agua del toro. Uso de sombra artificial si la natural es insuficiente.
SECCION: IV
OBJETIVO: Protocolos Obligatorios de Prevención (Transversales)
PROTOCOLO_1_NOMBRE: ITH en Tiempo Real
PROTOCOLO_1_ACCION: Designar persona para monitorear el ITH. No fiarse solo de la temperatura del aire; la humedad es co-piloto del peligro.
PROTOCOLO_2_NOMBRE: Densidad de Población
PROTOCOLO_2_ACCION: Reducir la densidad en corrales o áreas de espera para permitir libre flujo de aire entre los animales. A mayor ITH, mayor espacio requerido.
PROTOCOLO_3_NOMBRE: Vigilancia Comportamental
PROTOCOLO_3_ACCION: Actuar inmediatamente al observar jadeo (más de 60 respiraciones/minuto). El ganado pasa de pastorear/comer a buscar sombra y beber.
PROTOCOLO_4_NOMBRE: Botiquín de Emergencia
PROTOCOLO_4_ACCION: Mantener sales de rehidratación oral y electrolitos disponibles para la atención inmediata de animales postrados o deshidratados severamente.
CONCLUSION: Ejecutar estas medidas de forma proactiva garantiza sostener los niveles productivos y mitigar pérdidas bajo condiciones ambientales adversas."""

def generate_risk_narrative(df_forecast: pd.DataFrame, user_type: str, ith_threshold: float, farm_name: str) -> Tuple[str, str]:
    """
    Genera el asunto y el cuerpo del correo utilizando el modelo de Gemini.
    """
    # === FIX 1: Verificación de cliente de Gemini ===
    if client is None:
        subject = f"ALERTA TEMP. - {farm_name} ({user_type})"
        body = (f"El sistema de Inteligencia Artificial no está activo (GEMINI_API_KEY es inválida o falta).\n"
                f"REPORTE MANUAL: Umbral de riesgo: {ith_threshold:.2f}. Máximo ITH pronosticado: {df_forecast['ITH'].max():.2f}\n"
                f"Horas de ALTO riesgo (ITH > {ith_threshold:.2f}):\n"
                f"{df_forecast[df_forecast['risk'].str.contains('ALTO')][['time', 'ITH']].to_string(index=False)}\n"
                f"Por favor, active su clave API de Gemini para recibir las recomendaciones personalizadas.")
        return subject, body

    # 1. Preparar los datos del pronóstico (Hoy y Mañana)
    now = pd.Timestamp(datetime.now().strftime('%Y-%m-%d'), tz='America/Bogota')
    
    # Filtrar hoy y mañana
    df_today = df_forecast[df_forecast['time'].dt.date == now.date()]
    df_tomorrow = df_forecast[df_forecast['time'].dt.date == (now + pd.Timedelta(days=1)).date()]

    # --- CAMBIO CLAVE: FILTRAR RIESGO ALTO Y MODERADO ---
    # Esto filtra todas las filas que contengan 'ALTO' o 'MODERADO' en la columna 'risk'
    df_risk_today_filtered = df_today[df_today['risk'].str.contains('ALTO|MODERADO', case=False, na=False)]
    df_risk_tomorrow_filtered = df_tomorrow[df_tomorrow['risk'].str.contains('ALTO|MODERADO', case=False, na=False)]

    # Formatear las horas críticas (concatenando ITH para mejor contexto)
    risk_summary_today = "\n".join([
        f"{row['time'].strftime('%H:%M')} (ITH: {row['ITH']:.1f}, {row['risk']})" 
        for _, row in df_risk_today_filtered.iterrows()
    ])
    
    risk_summary_tomorrow = "\n".join([
        f"{row['time'].strftime('%H:%M')} (ITH: {row['ITH']:.1f}, {row['risk']})" 
        for _, row in df_risk_tomorrow_filtered.iterrows()
    ])
    
    # Si no hay riesgo, usar un mensaje claro
    if not risk_summary_today:
        risk_summary_today = "No se proyecta riesgo MODERADO o ALTO hoy. Mantenga monitoreo."
    if not risk_summary_tomorrow:
        risk_summary_tomorrow = "No se proyecta riesgo MODERADO o ALTO para mañana."

    # 2. Construir el Prompt
    system_instruction = (
        "Eres un Analista de Datos Agrícola experto en Estrés Térmico (ITH). "
        "Tu tarea es generar una alerta de correo electrónico proactiva, profesional y fácil de entender usando las etiquetas <p>. "
        "Formatea tu respuesta de esta manera EXACTA: '1. ASUNTO: [Tu Asunto]\n2. CUERPO: [Tu Cuerpo]'. "
        "La información más importante son las horas de ALERTA/MODERADA y las recomendaciones específicas del 'CONTEXTO' para el tipo de ganado con 3 recomendaciones especificas."
        "El mensaje debe ser claro, conciso y accionable no muy largo señalando en HTML las horas criticas de hoy y mañana en negruilla."
        "No incluyas saludos ni despedidas en el cuerpo del mensaje."
        "No uses h1 ni h2 en el cuerpo del mensaje."
        "Haz un salto de línea cada vez que haya una alerta de ITH."
        "Al final da una recomendación general para el usuario si sobre el mejor momento para la reproducción."
        
    )

    prompt = (
        f"{system_instruction}\n\n"
        f"{PREVENTION_DOCUMENTATION}\n\n"
        f"DATOS DE ANÁLISIS:\n"
        f"Granja: {farm_name}, Tipo: {user_type}, Umbral Histórico (P75): {ith_threshold:.2f}\n"
        f"Máximo ITH pronosticado en 48h: {df_forecast['ITH'].max():.2f}\n\n"
        f"RESUMEN DE HORAS CRÍTICAS (MODERADO y ALTO):\n"
        f"HOY:\n{risk_summary_today}\n\n"
        f"MAÑANA:\n{risk_summary_tomorrow}\n\n"
        f"INSTRUCCIÓN: Genera el ASUNTO y CUERPO de la alerta. El cuerpo debe tener 3 secciones:\n"
        f"I. Resumen: Riesgo general y ITH máximo.\n"
        f"II. HOY (Acción Inmediata): Menciona y discute las HORAS CRÍTICAS de HOY (listadas arriba) y proporciona las recomendaciones de manejo del 'CONTEXTO' que apliquen a esas horas y al ganado '{user_type}'.\n"
        f"III. MAÑANA (Planificación): Menciona las HORAS CRÍTICAS de MAÑANA y ofrece consejos de preparación. "
        f"Si solo hay riesgo MODERADO, usa un tono de 'Advertencia de Prevención'."
        
    )

    try:
        # Llama al modelo
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(system_instruction=system_instruction)
        )
        
        # === FIX 2: Separación robusta del Asunto y Cuerpo ===
        # Se busca el delimitador "1. ASUNTO:"
        if not response.text:
            raise ValueError("Respuesta de la IA vacía.")

        # Separar por el patrón de asunto
        if "1. ASUNTO:" in response.text:
            parts = response.text.split("1. ASUNTO:", 1)
            full_content = parts[1].strip()
            
            # Separar el cuerpo que empieza con "2. CUERPO:"
            if "2. CUERPO:" in full_content:
                subject_raw, body = full_content.split("2. CUERPO:", 1)
                subject = subject_raw.strip().split('\n')[0].strip() # Tomar solo la primera línea del asunto
                body = body.strip()
                return subject, body
        
        # Fallback si el formato de la IA no es el esperado
        print("ADVERTENCIA: La IA no siguió el formato de respuesta esperado (1. ASUNTO: / 2. CUERPO:).")
        subject = f"ALERTA IA NO ESTRUCTURADA - {farm_name}"
        return subject, response.text 

    except Exception as e:
        print(f"--- ERROR CRÍTICO en la llamada a la API de Gemini: {e}")
        # Retorna el mensaje de fallback en caso de cualquier excepción de la API.
        return "ALERTA FALLIDA (Error API)", f"Error al generar la narrativa de la IA. Mensaje: {e}"