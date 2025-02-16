import pandas as pd
from database import SessionLocal, Transaction, Category, init_db
from datetime import datetime

def migrate_csv_to_sql():
    """
    Migra los datos existentes de los archivos CSV a la base de datos SQL.
    """
    try:
        # Inicializar la base de datos
        print("Iniciando migración de datos...")
        init_db()
        db = SessionLocal()

        try:
            # Migrar transacciones desde la base de datos anterior
            print("Migrando transacciones existentes...")
            existing_transactions = db.query(Transaction).all()
            for transaction in existing_transactions:
                if not hasattr(transaction, 'moneda'):
                    transaction.moneda = 'PEN'

            db.commit()
            print("Migración completada exitosamente")

        except Exception as e:
            print(f"Error durante la migración: {e}")
            db.rollback()
        finally:
            db.close()

    except Exception as e:
        print(f"Error general durante la migración: {e}")

if __name__ == "__main__":
    migrate_csv_to_sql()