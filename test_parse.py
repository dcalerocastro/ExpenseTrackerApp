
from utils.email_parser import parse_email_content
from utils.data_manager import save_transaction

# Simulación de contenido de correo BCP
test_email_content = """
Estimado cliente:
Se realizó una compra con tu tarjeta terminada en 1234 el 08/02/2025.
Monto: S/ 90.00 en <b>OPENPAY*SUSHI POP MIRALIM</b>
Gracias por tu preferencia.
"""

# Probar el parseo
print("\n--- PRUEBA DE PARSEO ---")
transaction = parse_email_content(test_email_content)
print(f"Resultado del parseo: {transaction}")

# Probar el guardado
if transaction:
    print("\n--- PRUEBA DE GUARDADO ---")
    result = save_transaction(transaction)
    print(f"Resultado del guardado: {result}")
