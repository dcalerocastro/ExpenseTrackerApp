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
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        print(f"Cargando transacciones existentes: {len(df)} registros")
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    except Exception as e:
        print(f"Error cargando transacciones: {str(e)}")
        return pd.DataFrame()

def save_transaction(transaction):
    """Save a new transaction to CSV file"""
    try:
        ensure_data_files()
        
        # Crear un nuevo DataFrame con la transacción
        new_transaction = pd.DataFrame([{
            'fecha': pd.to_datetime(transaction['fecha']),
            'monto': float(transaction['monto']),
            'descripcion': str(transaction['descripcion']),
            'categoria': str(transaction['categoria']),
            'tipo': 'real'
        }])
        
        # Verificar si el archivo existe y tiene contenido
        try:
            df = pd.read_csv(TRANSACTIONS_FILE)
            df['fecha'] = pd.to_datetime(df['fecha'])
            new_df = pd.concat([df, new_transaction], ignore_index=True)
        except:
            new_df = new_transaction
            
        # Guardar directamente
        new_df.to_csv(TRANSACTIONS_FILE, index=False)
        return True
        
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