from datetime import datetime
from .database import User, SessionLocal
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(email: str, username: str, password: str) -> tuple[bool, str]:
    """
    Registra un nuevo usuario en el sistema.
    Retorna (éxito, mensaje)
    """
    print(f"\n=== Registrando nuevo usuario ===")
    print(f"Email: {email}")
    print(f"Username: {username}")

    db = SessionLocal()
    try:
        # Verificar si el email ya existe
        if db.query(User).filter(User.email == email).first():
            print("Email ya registrado")
            return False, "El email ya está registrado"

        # Verificar si el username ya existe
        if db.query(User).filter(User.username == username).first():
            print("Username ya en uso")
            return False, "El nombre de usuario ya está en uso"

        # Crear nuevo usuario
        hashed_password = generate_password_hash(password)
        user = User(
            email=email,
            username=username,
            password_hash=hashed_password
        )

        print("Creando nuevo usuario...")
        db.add(user)
        db.commit()
        print("Usuario registrado exitosamente")

        # Verificar que el usuario se creó correctamente
        created_user = db.query(User).filter(User.email == email).first()
        if created_user:
            print(f"Usuario verificado - ID: {created_user.id}")
            return True, "Usuario registrado exitosamente"
        else:
            print("Error: Usuario no encontrado después de crear")
            return False, "Error en el registro: Usuario no creado"

    except Exception as e:
        print(f"Error en el registro: {str(e)}")
        db.rollback()
        return False, f"Error en el registro: {str(e)}"
    finally:
        db.close()

def validate_login(email: str, password: str) -> tuple[bool, str, User | None]:
    """
    Valida las credenciales de un usuario.
    Retorna (éxito, mensaje, usuario)
    """
    print(f"\n=== Validando login ===")
    print(f"Email: {email}")

    db = SessionLocal()
    try:
        print("Buscando usuario...")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("Usuario no encontrado")
            return False, "Usuario no encontrado", None

        print("Verificando contraseña...")
        if not check_password_hash(user.password_hash, password):
            print("Contraseña incorrecta")
            return False, "Contraseña incorrecta", None

        print(f"Login exitoso para usuario {user.username}")
        return True, "Login exitoso", user

    except Exception as e:
        print(f"Error en el login: {str(e)}")
        return False, f"Error en el login: {str(e)}", None
    finally:
        db.close()