# src/templates.py (CÓDIGO CORREGIDO Y COMPLETO)
from datetime import datetime

def generate_alert_html(farm_name: str, product_type: str, ith_threshold: float, ai_generated_body: str) -> str:
    """
    Genera la estructura HTML completa y estilizada del correo de alerta.
    """
    
    # 1. Preparar el contenido de la IA (Corregir saltos de línea)
    # Reemplazamos los \n por la etiqueta <br> para que el formato se respete en HTML.
    html_content = ai_generated_body.replace('\n', '<br>')

    # 2. Estructura HTML (Usando f-string de Python)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {{ margin: 0; padding: 0; background-color: #f4f4f4; }}
            .container {{ 
                max-width: 650px; 
                margin: 20px auto; 
                padding: 0; 
                border: 1px solid #ddd; 
                border-radius: 12px; 
                background-color: #ffffff; 
                box-shadow: 0 4px 8px rgba(0,0,0,0.05); 
                font-family: Arial, sans-serif;
                color: #333; 
                font-size: 16px; 
            }}
            .header {{ 
                background-color: #2E7D32; 
                color: white; 
                padding: 15px 20px; 
                text-align: center; 
                border-radius: 10px 10px 0 0; 
            }}
            .header h1 {{ margin: 0; font-size: 26px; }}
            .content {{ padding: 25px 20px; }}
            .alert-box {{ 
                border: 1px solid #FFC107; 
                background-color: #FFFDE7; 
                padding: 15px; 
                margin-bottom: 20px; 
                border-radius: 8px; 
            }}
            .footer {{ 
                text-align: center; 
                font-size: 12px; 
                color: #777; 
                margin-top: 30px; 
                border-top: 1px solid #eee; 
                padding: 15px 0; 
            }}
            strong {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Agri-Alerta ITH</h1>
                <p style="font-size:14px; margin-top: 5px; margin-bottom: 0;">Reporte Proactivo de Estrés Térmico para Ganado</p>
            </div>
            <div class="content">
                <p style="font-weight: bold;">Estimado productor de {product_type} en {farm_name},</p>
                <p>Este es su reporte de 48 horas basado en el Índice de Temperatura y Humedad (ITH). Actuar a tiempo es vital para proteger la rentabilidad y bienestar de su ganado.</p>
                
                <div class="alert-box">
                    <p style="margin: 0;"><strong>ATENCIÓN:</strong> El sistema ha detectado horas de riesgo MODERADO y/o ALTO en su ubicación.</p>
                    <p style="font-size: 14px; color: #555; margin-top: 5px; margin-bottom: 0;">Tipo de Producción: <strong>{product_type}</strong> | Umbral de Alerta Histórico: <strong>{ith_threshold:.2f} ITH</strong></p>
                </div>
                
                <div class="ai-content">
                    {html_content}  </div>
                
                <p style="margin-top: 25px; text-align: center; font-weight: bold; color: #2E7D32;">¡La prevención es el camino a la máxima eficiencia!</p>
            </div>
            <div class="footer">
                <p>&copy; {datetime.now().year} Agri-Alerta. Plataforma de Mitigación de Estrés Térmico.</p>
                <p style="margin: 5px 0 0 0; font-size: 10px;">Este correo es automático. Por favor, no responda a este email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html