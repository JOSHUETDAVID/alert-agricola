# src/load.py
import smtplib
import ssl
from os import getenv
from dotenv import load_dotenv
import pandas as pd

# Carga las credenciales del .env
load_dotenv() 

EMAIL_USER = getenv("EMAIL_USER")
EMAIL_PASS = getenv("EMAIL_PASS") # Usar App Password si tienes 2FA

# =======================================================================
# FUNCIÓN DE ENVÍO DE EMAIL
# =======================================================================

def send_email_alert(recipient_email: str, subject: str, body: str) -> bool:
    """
    Envía un correo electrónico de alerta utilizando SMTP seguro.
    """
    if not EMAIL_USER or not EMAIL_PASS:
        print("-- ERROR: Credenciales de email (EMAIL_USER o EMAIL_PASS) no configuradas en .env.")
        return False
        
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()

    try:
        # Configuración del mensaje MIME simple
        message = f"Subject: {subject}\nTo: {recipient_email}\n\n{body}"

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, recipient_email, message.encode("utf-8"))

            print(f"-- EXITO -- Alerta enviada a: {recipient_email}")
            return True

    except smtplib.SMTPAuthenticationError:
        print("-- FALLO DE AUTENTICACIÓN. Revisa tu EMAIL_PASS (App Password) o credenciales.")
        return False
    except Exception as e:
        print(f"-- ERROR al enviar correo a {recipient_email}: {e}")
        return False