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
    sender_email = os.getenv('EMAIL_USER')
    sender_password = os.getenv('EMAIL_PASSWORD')

    # Crear el mensaje
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Recuperación de Contraseña - GastoSync"

    # Crear el link de recuperación (ajusta la URL según tu dominio)
    reset_link = f"https://gastosync.replit.app/reset_password?token={reset_token}"

    # Crear el contenido HTML del correo
    body = f"""
    <html>
        <body>
            <h2>Recuperación de Contraseña - GastoSync</h2>
            <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
            <p><a href="{reset_link}">Restablecer mi contraseña</a></p>
            <p>Este enlace expirará en 1 hora.</p>
            <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.</p>
            <br>
            <p>Saludos,<br>Equipo GastoSync</p>
        </body>
    </html>
    """

    message.attach(MIMEText(body, "html"))

    try:
        # Conectar al servidor SMTP de Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Enviar el correo
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando correo: {str(e)}")
        return False

def initiate_password_reset(email: str) -> tuple[bool, str]:
    """Inicia el proceso de recuperación de contraseña"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "No existe una cuenta con ese correo electrónico"

        # Generar y guardar el token
        token = generate_reset_token()
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        # Enviar el correo
        if send_reset_email(email, token):
            return True, "Se ha enviado un correo con las instrucciones para restablecer tu contraseña"
        else:
            return False, "Error al enviar el correo de recuperación"

    except Exception as e:
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
