from datetime import datetime
from .database import User, SessionLocal

def register_user(email: str, username: str, password: str) -> tuple[bool, str]:
    """
    Registra un nuevo usuario en el sistema.
    Retorna (éxito, mensaje)
    """
    db = SessionLocal()
    try:
        # Verificar si el email ya existe
        if db.query(User).filter(User.email == email).first():
            return False, "El email ya está registrado"
        
        # Verificar si el username ya existe
        if db.query(User).filter(User.username == username).first():
            return False, "El nombre de usuario ya está en uso"
        
        # Crear nuevo usuario
        user = User(email=email, username=username)
        user.set_password(password)
        
        db.add(user)
        db.commit()
        return True, "Usuario registrado exitosamente"
    
    except Exception as e:
        db.rollback()
        return False, f"Error en el registro: {str(e)}"
    finally:
        db.close()

def validate_login(email: str, password: str) -> tuple[bool, str, User | None]:
    """
    Valida las credenciales de un usuario.
    Retorna (éxito, mensaje, usuario)
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "Usuario no encontrado", None
        
        if not user.check_password(password):
            return False, "Contraseña incorrecta", None
        
        return True, "Login exitoso", user
    
    except Exception as e:
        return False, f"Error en el login: {str(e)}", None
    finally:
        db.close()
