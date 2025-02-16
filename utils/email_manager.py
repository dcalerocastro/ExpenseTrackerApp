from datetime import datetime
from .database import EmailAccount, SessionLocal
from .encryption import encrypt_password, decrypt_password

def save_email_account(email: str, password: str, bank_name: str, user_id: int) -> tuple[bool, str]:
    """
    Guarda una nueva cuenta de correo con sus credenciales cifradas.
    """
    db = SessionLocal()
    try:
        # Verificar si ya existe esta combinación de correo y banco para el usuario
        existing = db.query(EmailAccount).filter(
            EmailAccount.email == email,
            EmailAccount.bank_name == bank_name,
            EmailAccount.user_id == user_id
        ).first()

        if existing:
            return False, "Ya existe una cuenta configurada para este banco"

        # Cifrar la contraseña
        encrypted_password = encrypt_password(password)

        # Crear nueva cuenta
        account = EmailAccount(
            email=email,
            encrypted_password=encrypted_password,
            bank_name=bank_name,
            user_id=user_id
        )

        db.add(account)
        db.commit()
        return True, "Cuenta guardada exitosamente"

    except Exception as e:
        db.rollback()
        return False, f"Error guardando la cuenta: {str(e)}"
    finally:
        db.close()

def get_email_accounts(user_id: int):
    """
    Obtiene todas las cuentas de correo configuradas para un usuario.
    """
    db = SessionLocal()
    try:
        accounts = db.query(EmailAccount).filter(
            EmailAccount.user_id == user_id,
            EmailAccount.is_active == True
        ).all()
        return accounts
    finally:
        db.close()

def update_last_sync(account_id: int):
    """
    Actualiza la fecha de última sincronización de una cuenta.
    """
    db = SessionLocal()
    try:
        account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
        if account:
            account.last_sync = datetime.now()
            db.commit()
    finally:
        db.close()
