import pandas as pd
import os
from datetime import datetime
import traceback

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
    """Save a new transaction to CSV file with improved validation and error handling"""
    try:
        print("\n--- Iniciando guardado de transacción en data_manager ---")
        print("Transacción a guardar:", transaction)
        ensure_data_files()

        # Validar y formatear la transacción
        if not isinstance(transaction['fecha'], (datetime, pd.Timestamp)):
            raise ValueError(f"Tipo de fecha inválido: {type(transaction['fecha'])}")

        formatted_transaction = {
            'fecha': pd.to_datetime(transaction['fecha']).strftime('%Y-%m-%d'),
            'monto': float(transaction['monto']),
            'descripcion': str(transaction['descripcion']).strip(),
            'categoria': str(transaction['categoria']),
            'tipo': str(transaction.get('tipo', 'real'))
        }
        print("Transacción formateada:", formatted_transaction)

        # Crear DataFrame con la nueva transacción
        new_transaction = pd.DataFrame([formatted_transaction])
        print("DataFrame creado:", new_transaction.to_string())

        # Cargar y validar transacciones existentes
        try:
            existing_df = pd.read_csv(TRANSACTIONS_FILE)
            if len(existing_df) > 0:
                existing_df['fecha'] = pd.to_datetime(existing_df['fecha']).dt.strftime('%Y-%m-%d')
            print("Transacciones existentes cargadas:", len(existing_df))
        except Exception as e:
            print("Error cargando existentes, creando nuevo DataFrame:", str(e))
            existing_df = pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo'])

        # Concatenar y guardar
        final_df = pd.concat([existing_df, new_transaction], ignore_index=True)
        print("DataFrame final antes de guardar:")
        print(final_df.to_string())

        final_df.to_csv(TRANSACTIONS_FILE, index=False)
        print("Archivo guardado exitosamente")

        # Verificar que se guardó correctamente
        verification_df = pd.read_csv(TRANSACTIONS_FILE)
        print(f"Verificación - registros en archivo: {len(verification_df)}")

        return True

    except Exception as e:
        print(f"Error guardando transacción: {str(e)}")
        print(f"Detalles completos del error:\n{traceback.format_exc()}")
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