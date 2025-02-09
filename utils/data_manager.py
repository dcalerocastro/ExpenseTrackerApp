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
        # Verificar permisos
        import os
        print(f"Permisos de escritura del archivo: {os.access(TRANSACTIONS_FILE, os.W_OK)}")
        
        print("Intentando guardar la transacción:", transaction)
        ensure_data_files()

        # Crear un nuevo DataFrame con la transacción
        new_transaction = pd.DataFrame([{
            'fecha': pd.to_datetime(transaction['fecha']),
            'monto': float(transaction['monto']),
            'descripcion': str(transaction['descripcion']),
            'categoria': str(transaction['categoria']),
            'tipo': 'real'
        }])
        print(f"Nueva transacción formateada: \n{new_transaction.to_string()}")

        # Cargar transacciones existentes
        existing_df = load_transactions()
        print(f"Transacciones existentes:\n{existing_df.to_string()}")

        # Concatenar la nueva transacción
        new_df = pd.concat([existing_df, new_transaction], ignore_index=True)
        print(f"DataFrame después de concatenar: \n{new_df.to_string()}")

        # Guardar el archivo actualizado
        new_df.to_csv(TRANSACTIONS_FILE, index=False)
        
        # Verificar el guardado
        print(f"Verificando contenido de {TRANSACTIONS_FILE} después de guardar:")
        df_check = pd.read_csv(TRANSACTIONS_FILE)
        print(df_check.to_string())
        
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