import secrets
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from .database import User, SessionLocal
from werkzeug.security import generate_password_hash

def generate_reset_token():
    """Genera un token seguro para restablecer la contraseña"""
    return secrets.token_urlsafe(32)

def send_reset_email(email: str, reset_token: str):
    """Envía el correo de recuperación de contraseña"""
    print("\n=== Intentando enviar correo de recuperación ===")
    sender_email = os.getenv('EMAIL_USER')
    sender_password = os.getenv('EMAIL_PASSWORD')

    print(f"Configuración de correo:")
    print(f"- Remitente: {sender_email}")
    print(f"- Contraseña configurada: {'Sí' if sender_password else 'No'}")

    # Crear el mensaje
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Recuperación de Contraseña - GastoSync"

    # Crear el link de recuperación
    reset_link = f"https://gastosync.replit.app/reset_password?token={reset_token}"

    # Crear el contenido HTML del correo con mejor formato
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #4A4FEB; margin-bottom: 20px;">Recuperación de Contraseña - GastoSync</h2>
                <p style="color: #333; line-height: 1.6;">Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                <p style="margin: 25px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #4A4FEB; 
                              color: white; 
                              padding: 10px 20px; 
                              text-decoration: none; 
                              border-radius: 5px;
                              display: inline-block;">
                        Restablecer mi contraseña
                    </a>
                </p>
                <p style="color: #666; font-size: 0.9em;">Este enlace expirará en 1 hora.</p>
                <p style="color: #666; font-size: 0.9em;">Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #888; font-size: 0.8em;">Saludos,<br>Equipo GastoSync</p>
            </div>
        </body>
    </html>
    """

    message.attach(MIMEText(body, "html"))

    try:
        print("Conectando al servidor SMTP de Gmail...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        print("Iniciando TLS...")
        server.starttls()

        print("Intentando login...")
        server.login(sender_email, sender_password)
        print("Login exitoso")

        print("Enviando mensaje...")
        server.send_message(message)
        print("Mensaje enviado")

        server.quit()
        print("Conexión cerrada")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de autenticación SMTP: {str(e)}")
        print("Esto puede deberse a:")
        print("1. Contraseña incorrecta")
        print("2. Acceso de aplicaciones menos seguras desactivado")
        print("3. Autenticación de dos factores activada sin contraseña de aplicación")
        return False
    except Exception as e:
        print(f"Error enviando correo: {str(e)}")
        return False

def initiate_password_reset(email: str) -> tuple[bool, str]:
    """Inicia el proceso de recuperación de contraseña"""
    print(f"\n=== Iniciando recuperación de contraseña para: {email} ===")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("Usuario no encontrado")
            return False, "No existe una cuenta con ese correo electrónico"

        # Generar y guardar el token
        token = generate_reset_token()
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)

        print("Token generado y guardado")
        db.commit()

        # Enviar el correo
        if send_reset_email(email, token):
            print("Proceso de recuperación completado exitosamente")
            return True, "Se ha enviado un correo con las instrucciones para restablecer tu contraseña"
        else:
            print("Error al enviar el correo")
            return False, "Error al enviar el correo de recuperación. Por favor, contacta al soporte técnico."

    except Exception as e:
        print(f"Error en el proceso de recuperación: {str(e)}")
        db.rollback()
        return False, f"Error en el proceso de recuperación: {str(e)}"
    finally:
        db.close()

def reset_password(token: str, new_password: str) -> tuple[bool, str]:
    """Restablece la contraseña usando el token"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expiry > datetime.utcnow()
        ).first()

        if not user:
            return False, "Token inválido o expirado"

        # Actualizar la contraseña
        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()

        return True, "Contraseña actualizada exitosamente"

    except Exception as e:
        db.rollback()
        return False, f"Error al restablecer la contraseña: {str(e)}"
    finally:
        db.close()