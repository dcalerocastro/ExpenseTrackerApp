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
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

def save_transaction(transaction):
    """Save a new transaction to CSV file"""
    ensure_data_files()
    df = load_transactions()

    # Asegurar que el tipo esté definido
    if 'tipo' not in transaction:
        transaction['tipo'] = 'real'

    # Convertir fecha a datetime si es necesario
    if isinstance(transaction['fecha'], str):
        transaction['fecha'] = pd.to_datetime(transaction['fecha'])

    # Crear un nuevo DataFrame con la transacción y concatenar
    transaction_df = pd.DataFrame([transaction])
    new_df = pd.concat([df, transaction_df], ignore_index=True)

    # Guardar el archivo
    new_df.to_csv(TRANSACTIONS_FILE, index=False)
    print(f"Transacción guardada: {transaction}")
    return True

def load_categories():
    """Load categories from CSV file"""
    ensure_data_files()
    df = pd.read_csv(CATEGORIES_FILE)
    return df['categoria'].tolist()

def save_categories(categories):
    """Save categories to CSV file"""
    ensure_data_files()
    pd.DataFrame(categories, columns=['categoria']).to_csv(CATEGORIES_FILE, index=False)