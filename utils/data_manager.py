import pandas as pd
import os

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
            'tipo'  # 'real' o 'proyectado'
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
    df = pd.read_csv(TRANSACTIONS_FILE)
    df['fecha'] = pd.to_datetime(df['fecha'].str.strip(), format='mixed')

    # Asegurar que exista la columna 'tipo'
    if 'tipo' not in df.columns:
        df['tipo'] = 'real'
        df.to_csv(TRANSACTIONS_FILE, index=False)

    return df

def save_transaction(transaction):
    """Save a new transaction to CSV file"""
    try:
        print("Iniciando guardado de transacción...")
        print(f"Datos recibidos: {transaction}")
        
        ensure_data_files()
        df = load_transactions()
        print(f"DataFrame actual: {len(df)} filas")
        
        # Crear un nuevo DataFrame con la transacción
        new_row = pd.DataFrame([{
            'fecha': pd.to_datetime(transaction['fecha']),
            'monto': float(transaction['monto']),
            'descripcion': str(transaction['descripcion']),
            'categoria': str(transaction['categoria']),
            'tipo': transaction.get('tipo', 'real')
        }])
        print(f"Nueva fila creada: {new_row.to_dict('records')}")
        
        # Concatenar con el DataFrame existente
        df = pd.concat([df, new_row], ignore_index=True)
        print(f"DataFrame después de concat: {len(df)} filas")
        
        # Guardar el DataFrame actualizado
        df.to_csv(TRANSACTIONS_FILE, index=False)
        print(f"Transacción guardada en {TRANSACTIONS_FILE}")
        
        # Verificar que el archivo existe y tiene el contenido correcto
        if os.path.exists(TRANSACTIONS_FILE):
            print(f"Archivo verificado: {os.path.getsize(TRANSACTIONS_FILE)} bytes")
            return True
        else:
            print("Error: El archivo no existe después de guardar")
            return False
    except Exception as e:
        print(f"Error guardando transacción: {str(e)}")
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