# src/load.py (CORREGIDO Y COMPLETO PARA HTML)
import smtplib
import ssl
from os import getenv
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart # Necesario para correos con múltiples formatos
from email.mime.text import MIMEText           # Necesario para definir el cuerpo como HTML

load_dotenv() 
EMAIL_SENDER = getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = getenv("EMAIL_PASS")

def send_email_alert(recipient_email: str, subject: str, html_body: str) -> bool:
    """
    Envía un correo electrónico de alerta con contenido HTML.
    """
    if not EMAIL_SENDER or not EMAIL_APP_PASSWORD:
        print("---- ERROR: Credenciales de email no configuradas en .env.")
        return False
        
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()

    try:
        # 1. Crear el objeto MIME principal
        message = MIMEMultipart("alternative") # 'alternative' permite que el cliente elija (texto o html)
        message["From"] = EMAIL_SENDER
        message["To"] = recipient_email
        message["Subject"] = subject

        # 2. Adjuntar la parte HTML
        html_part = MIMEText(html_body, "html") # <-- Se define el tipo MIME como HTML
        message.attach(html_part)

        # 3. Conexión y envío
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            # sendmail ahora usa message.as_string()
            server.sendmail(EMAIL_SENDER, recipient_email, message.as_string())

            print(f"    --- EXITO Alerta HTML enviada a: {recipient_email}")
            return True

    except smtplib.SMTPAuthenticationError:
        print(f"    ---- FALLO DE AUTENTICACIÓN. Revisa tu App Password.")
        return False
    except Exception as e:
        print(f"    ---- ERROR al enviar correo HTML a {recipient_email}: {e}")
        return False