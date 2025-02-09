import pandas as pd
import os
from datetime import datetime
import traceback

# Constants
TRANSACTIONS_FILE = "data/transactions.csv"
CATEGORIES_FILE = "data/categories.csv"

def ensure_data_files():
    """Ensure data files exist with correct structure"""
    print("\n--- Verificando archivos de datos ---")
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(TRANSACTIONS_FILE):
        print(f"Creando archivo de transacciones: {TRANSACTIONS_FILE}")
        pd.DataFrame(columns=[
            'fecha',
            'monto',
            'descripcion',
            'categoria',
            'tipo'
        ]).to_csv(TRANSACTIONS_FILE, index=False)
    else:
        print(f"Archivo de transacciones existe: {TRANSACTIONS_FILE}")

    if not os.path.exists(CATEGORIES_FILE):
        print(f"Creando archivo de categorías: {CATEGORIES_FILE}")
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
    else:
        print(f"Archivo de categorías existe: {CATEGORIES_FILE}")

def load_transactions():
    """Load transactions from CSV file"""
    ensure_data_files()
    try:
        print("\n--- Cargando transacciones ---")
        df = pd.read_csv(TRANSACTIONS_FILE)
        print(f"Archivo leído exitosamente: {len(df)} registros")
        if len(df) > 0:
            df['fecha'] = pd.to_datetime(df['fecha'])
            print("Fechas convertidas a datetime")
        return df
    except Exception as e:
        print(f"Error cargando transacciones: {str(e)}")
        print(traceback.format_exc())
        return pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo'])

def save_transaction(transaction):
    """Save a new transaction to CSV file"""
    try:
        print("\n--- Iniciando guardado de transacción ---")
        print(f"Datos recibidos: {transaction}")
        
        ensure_data_files()

        # Formatear transacción asegurando tipos de datos
        formatted_transaction = {
            'fecha': pd.to_datetime(transaction['fecha']).strftime('%Y-%m-%d'),
            'monto': float(transaction['monto']),
            'descripcion': str(transaction['descripcion']).strip(),
            'categoria': str(transaction.get('categoria', 'Sin Categorizar')),
            'tipo': str(transaction.get('tipo', 'real'))
        }
        print(f"Datos formateados: {formatted_transaction}")

        # Cargar CSV existente o crear nuevo
        try:
            df = pd.read_csv(TRANSACTIONS_FILE)
        except Exception as e:
            print(f"Creando nuevo CSV: {str(e)}")
            df = pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo'])

        # Agregar nueva transacción
        df.loc[len(df)] = formatted_transaction
        
        # Guardar de vuelta al CSV
        df.to_csv(TRANSACTIONS_FILE, index=False)
        print(f"Transacción guardada. Total registros: {len(df)}")
        
        return True

    except Exception as e:
        print(f"Error guardando transacción: {str(e)}")
        print("Traceback:", traceback.format_exc())
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