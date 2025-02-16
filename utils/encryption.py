import os
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode

def get_or_create_key():
    """
    Obtiene la clave de cifrado existente o crea una nueva.
    La clave se almacena en una variable de entorno.
    """
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        # Generar nueva clave
        key = Fernet.generate_key()
        os.environ['ENCRYPTION_KEY'] = key.decode()
    else:
        # Convertir la clave almacenada de string a bytes
        key = key.encode()
    return key

def encrypt_password(password: str) -> str:
    """
    Cifra una contraseña usando Fernet (cifrado simétrico).
    """
    key = get_or_create_key()
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())
    return b64encode(encrypted).decode()

def decrypt_password(encrypted_password: str) -> str:
    """
    Descifra una contraseña cifrada.
    """
    key = get_or_create_key()
    f = Fernet(key)
    decrypted = f.decrypt(b64decode(encrypted_password))
    return decrypted.decode()
