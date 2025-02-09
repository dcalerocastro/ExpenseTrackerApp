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
    """Save a new transaction to CSV file with improved validation and error handling"""
    try:
        print("\n=== INICIANDO PROCESO DE GUARDADO ===")
        print(f"Directorio actual: {os.getcwd()}")
        print(f"Archivo de transacciones: {TRANSACTIONS_FILE}")
        print("Transacción a guardar:", transaction)

        ensure_data_files()

        # Validación de datos
        print("\n--- Validando datos ---")
        if not isinstance(transaction['fecha'], (datetime, pd.Timestamp)):
            raise ValueError(f"Tipo de fecha inválido: {type(transaction['fecha'])}")

        formatted_transaction = {
            'fecha': pd.to_datetime(transaction['fecha']).strftime('%Y-%m-%d'),
            'monto': float(transaction['monto']),
            'descripcion': str(transaction['descripcion']).strip(),
            'categoria': str(transaction['categoria']),
            'tipo': str(transaction.get('tipo', 'real'))
        }
        print("Datos formateados:", formatted_transaction)

        # Crear nuevo DataFrame
        print("\n--- Creando DataFrame ---")
        new_transaction = pd.DataFrame([formatted_transaction])
        print("Nuevo DataFrame creado:")
        print(new_transaction.to_string())

        # Cargar transacciones existentes
        print("\n--- Cargando transacciones existentes ---")
        try:
            existing_df = pd.read_csv(TRANSACTIONS_FILE)
            if len(existing_df) > 0:
                existing_df['fecha'] = pd.to_datetime(existing_df['fecha']).dt.strftime('%Y-%m-%d')
            print(f"Transacciones existentes cargadas: {len(existing_df)} registros")
        except Exception as e:
            print(f"Error cargando existentes, creando nuevo DataFrame: {str(e)}")
            existing_df = pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo'])

        # Concatenar DataFrames
        print("\n--- Concatenando DataFrames ---")
        final_df = pd.concat([existing_df, new_transaction], ignore_index=True)
        print("DataFrame final:")
        print(final_df.to_string())

        # Guardar archivo
        print("\n--- Guardando archivo ---")
        try:
            final_df.to_csv(TRANSACTIONS_FILE, index=False)
            print("Archivo guardado exitosamente")
        except Exception as e:
            print(f"Error guardando archivo: {str(e)}")
            print(traceback.format_exc())
            raise

        # Verificar guardado
        print("\n--- Verificando guardado ---")
        verification_df = pd.read_csv(TRANSACTIONS_FILE)
        print(f"Verificación - registros en archivo: {len(verification_df)}")

        print("\n=== GUARDADO COMPLETADO EXITOSAMENTE ===")
        return True

    except Exception as e:
        print("\n=== ERROR EN EL PROCESO DE GUARDADO ===")
        print(f"Error: {str(e)}")
        print("Stacktrace:")
        print(traceback.format_exc())
        print("Datos que causaron el error:", transaction)
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