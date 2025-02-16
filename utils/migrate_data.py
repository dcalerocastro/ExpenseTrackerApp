import pandas as pd
from database import SessionLocal, Transaction, Category, init_db
from datetime import datetime

def migrate_csv_to_sql():
    """
    Migra los datos existentes de los archivos CSV a la base de datos SQL.
    """
    try:
        # Inicializar la base de datos
        init_db()
        db = SessionLocal()
        
        # Migrar categorías
        categories_df = pd.read_csv("data/categories.csv")
        print(f"Migrando {len(categories_df)} categorías...")
        
        for _, row in categories_df.iterrows():
            category = Category(categoria=row['categoria'])
            db.merge(category)
        
        # Migrar transacciones
        transactions_df = pd.read_csv("data/transactions.csv")
        print(f"Migrando {len(transactions_df)} transacciones...")
        
        for _, row in transactions_df.iterrows():
            transaction = Transaction(
                fecha=pd.to_datetime(row['fecha']),
                monto=float(row['monto']),
                descripcion=str(row['descripcion']),
                categoria=str(row['categoria']),
                tipo=str(row['tipo'])
            )
            db.add(transaction)
        
        db.commit()
        print("Migración completada exitosamente")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_csv_to_sql()
