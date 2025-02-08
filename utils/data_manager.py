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
    ensure_data_files()
    df = load_transactions()

    # Asegurar que el tipo esté definido
    if 'tipo' not in transaction:
        transaction['tipo'] = 'real'

    new_df = pd.concat([df, pd.DataFrame([transaction])], ignore_index=True)
    new_df.to_csv(TRANSACTIONS_FILE, index=False)

def load_categories():
    """Load categories from CSV file"""
    ensure_data_files()
    df = pd.read_csv(CATEGORIES_FILE)
    return df['categoria'].tolist()

def save_categories(categories):
    """Save categories to CSV file"""
    ensure_data_files()
    pd.DataFrame(categories, columns=['categoria']).to_csv(CATEGORIES_FILE, index=False)