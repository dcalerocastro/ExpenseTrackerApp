import pandas as pd
import os
from datetime import datetime

# Constants
TRANSACTIONS_FILE = "data/transactions.csv"
CATEGORIES_FILE = "data/categories.csv"

def ensure_data_files():
    """Ensure data files exist with correct structure"""
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(TRANSACTIONS_FILE):
        pd.DataFrame(columns=[
            'fecha',
            'monto',
            'descripcion',
            'categoria',
            'tipo'
        ]).to_csv(TRANSACTIONS_FILE, index=False)

    if not os.path.exists(CATEGORIES_FILE):
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
        pd.DataFrame(default_categories, columns=['categoria']).to_csv(CATEGORIES_FILE, index=False)

def load_transactions():
    """Load transactions from CSV file"""
    ensure_data_files()
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        print(f"Cargando transacciones existentes: {len(df)} registros")
        if len(df) > 0:
            df['fecha'] = pd.to_datetime(df['fecha'])
            print(f"Transacciones actuales: \n{df.to_string()}")
        return df
    except Exception as e:
        print(f"Error cargando transacciones: {str(e)}")
        return pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo'])

def save_transaction(transaction):
        """Save a new transaction to CSV file"""
        try:
            print("\n--- Iniciando guardado de transacción ---")
            print("Transacción a guardar:", transaction)
            ensure_data_files()

            # Formatear la transacción
            formatted_transaction = {
                'fecha': pd.to_datetime(transaction['fecha']).strftime('%Y-%m-%d'),
                'monto': float(transaction['monto']),
                'descripcion': str(transaction['descripcion']).strip(),
                'categoria': str(transaction['categoria']),
                'tipo': 'real'
            }
            print("Transacción formateada:", formatted_transaction)

            # Crear DataFrame con la nueva transacción
            new_transaction = pd.DataFrame([formatted_transaction])
            print("DataFrame creado:", new_transaction.to_string())

            # Cargar transacciones existentes
            try:
                existing_df = pd.read_csv(TRANSACTIONS_FILE)
                existing_df['fecha'] = pd.to_datetime(existing_df['fecha']).dt.strftime('%Y-%m-%d')
                print("Transacciones existentes cargadas:", len(existing_df))
            except Exception as e:
                print("Error cargando existentes:", str(e))
                existing_df = pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo'])

            # Concatenar y guardar
            new_df = pd.concat([existing_df, new_transaction], ignore_index=True)
            print("DataFrame final:", new_df.to_string())
            new_df.to_csv(TRANSACTIONS_FILE, index=False)
            print("Archivo guardado exitosamente")

            return True

        except Exception as e:
            print(f"Error guardando transacción: {str(e)}")
            print(f"Detalles de la transacción que causó el error: {transaction}")
            import traceback
            print("Stacktrace completo:", traceback.format_exc())
            return False

def load_categories():
    """Load categories from CSV file"""
    ensure_data_files()
    df = pd.read_csv(CATEGORIES_FILE)
    return df['categoria'].tolist()

def save_categories(categories):
    """Save categories to CSV file"""
    ensure_data_files()
    pd.DataFrame(categories, columns=['categoria']).to_csv(CATEGORIES_FILE, index=False)