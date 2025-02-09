
import streamlit as st
import os
from utils.email_reader import EmailReader
from utils.data_manager import save_transaction, load_transactions

def test_app_flow():
    print("\n--- PRUEBA DE FLUJO DE APLICACIÓN ---")
    
    email_user = "dcalerocastro@gmail.com"
    email_password = "fvtv jxim bsdq htwc"
    
    try:
        print("\n1. Conectando con el servidor de correo...")
        reader = EmailReader(email_user, email_password)
        transactions = reader.fetch_bcp_notifications(days_back=1)
        
        if not transactions:
            print("No se encontraron transacciones")
            return
            
        print(f"\n2. Transacciones encontradas: {len(transactions)}")
        
        print("\n3. Intentando guardar transacciones...")
        for idx, transaction in enumerate(transactions):
            print(f"\nGuardando transacción {idx + 1}:")
            print(f"Datos: {transaction}")
            
            save_result = save_transaction(transaction)
            print(f"Resultado del guardado: {'Éxito' if save_result else 'Falló'}")
            
        print("\n4. Verificando transacciones guardadas...")
        saved_transactions = load_transactions()
        print(f"Total de transacciones en archivo: {len(saved_transactions)}")
        
    except Exception as e:
        print(f"Error en el flujo: {str(e)}")

if __name__ == "__main__":
    test_app_flow()
