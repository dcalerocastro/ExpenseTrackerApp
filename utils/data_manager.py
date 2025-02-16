from datetime import datetime
import traceback
from .database import SessionLocal, Transaction, Category, init_db
import pandas as pd

def ensure_data_exists():
    """Asegura que la base de datos está inicializada con las categorías por defecto"""
    print("\n--- Verificando base de datos ---")
    db = SessionLocal()
    try:
        # Inicializar la base de datos si no existe
        init_db()

        # Verificar si hay categorías
        if db.query(Category).count() == 0:
            print("Inicializando categorías por defecto")
            default_categories = [
                "Gastos Corrientes",
                "Casa",
                "Servicios Básicos",
                "Transporte",
                "Alimentación",
                "Salud",
                "Entretenimiento",
                "Sin Categorizar"
            ]
            for cat in default_categories:
                db.add(Category(categoria=cat))
            db.commit()
            print("Categorías por defecto creadas")
    except Exception as e:
        print(f"Error verificando datos: {str(e)}")
        db.rollback()
    finally:
        db.close()

def load_transactions():
    """Carga todas las transacciones de la base de datos"""
    ensure_data_exists()
    db = SessionLocal()
    try:
        print("\n--- Cargando transacciones ---")
        transactions = db.query(Transaction).all()

        # Convertir a DataFrame para mantener compatibilidad con el código existente
        if transactions:
            data = [{
                'fecha': t.fecha,
                'monto': t.monto,
                'descripcion': t.descripcion,
                'categoria': t.categoria,
                'tipo': t.tipo,
                'moneda': t.moneda
            } for t in transactions]
            df = pd.DataFrame(data)
            print(f"Transacciones cargadas: {len(df)} registros")
            return df
        return pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo', 'moneda'])

    except Exception as e:
        print(f"Error cargando transacciones: {str(e)}")
        print(traceback.format_exc())
        return pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo', 'moneda'])
    finally:
        db.close()

def save_transaction(transaction_data):
    """Guarda una nueva transacción en la base de datos"""
    print("\n=== INICIANDO GUARDADO DE TRANSACCIÓN ===")
    print(f"Datos recibidos: {transaction_data}")

    # Verificar que todos los campos requeridos estén presentes
    required_fields = ['fecha', 'monto', 'descripcion', 'categoria']
    for field in required_fields:
        if field not in transaction_data:
            print(f"Error: Campo requerido faltante: {field}")
            return False

    db = SessionLocal()
    try:
        # Convertir fecha si es necesario
        if isinstance(transaction_data['fecha'], str):
            transaction_data['fecha'] = pd.to_datetime(transaction_data['fecha'])

        # Crear nueva transacción
        new_transaction = Transaction(
            fecha=transaction_data['fecha'],
            monto=float(transaction_data['monto']),
            descripcion=str(transaction_data['descripcion']),
            categoria=str(transaction_data['categoria']),
            tipo=str(transaction_data.get('tipo', 'real')),
            moneda=str(transaction_data.get('moneda', 'PEN'))
        )

        print(f"Transacción preparada: {vars(new_transaction)}")

        # Guardar en la base de datos
        db.add(new_transaction)
        db.commit()
        print("Transacción guardada exitosamente")

        # Verificar inmediatamente después del guardado
        saved_transactions = db.query(Transaction).all()
        print(f"Verificación inmediata - Registros en BD: {len(saved_transactions)}")
        print("Últimas 5 transacciones:")
        for t in saved_transactions[-5:]:
            print(f"{t.fecha}: {t.descripcion} - {t.monto}")
        return True

    except Exception as e:
        print(f"Error guardando transacción: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return False
    finally:
        db.close()

def load_categories():
    """Carga todas las categorías de la base de datos"""
    ensure_data_exists()
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return [cat.categoria for cat in categories]
    except Exception as e:
        print(f"Error cargando categorías: {str(e)}")
        return ["Sin Categorizar"]
    finally:
        db.close()

def save_categories(categories):
    """Guarda las categorías en la base de datos"""
    db = SessionLocal()
    try:
        # Eliminar categorías existentes
        db.query(Category).delete()

        # Agregar nuevas categorías
        for cat in categories:
            db.add(Category(categoria=cat))

        db.commit()
        return True
    except Exception as e:
        print(f"Error guardando categorías: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()