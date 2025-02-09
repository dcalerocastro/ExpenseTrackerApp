import email
from email import policy
from datetime import datetime
import re

def parse_email_content(email_content):
    """
    Parse email content to extract transaction details.
    """
    try:
        # Extract information using regex patterns
        # Amount pattern (supports both S/ and US$)
        amount_pattern = r'(?:S/|US\$)\s*(\d+(?:\.\d{2})?)'
        amount_match = re.search(amount_pattern, email_content)

        # Determine currency
        currency = 'PEN' if 'S/' in email_content else 'USD' if 'US$' in email_content else 'PEN'

        # Date pattern
        date_pattern = r'(\d{1,2}(?:/|-)\d{1,2}(?:/|-)\d{2,4})'
        date_match = re.search(date_pattern, email_content)

        # Extract merchant name (between <b> tags after "en")
        merchant_pattern = r'en\s*<b>(.*?)</b>'
        merchant_match = re.search(merchant_pattern, email_content)

        if amount_match:
            amount = float(amount_match.group(1))
            print(f"Monto extraído: {amount:.2f} {currency}")

            # Get merchant name or use default
            description = (merchant_match.group(1) if merchant_match 
                         else 'Transacción sin comercio')
            print(f"Comercio extraído: {description}")

            # Parse date
            if date_match:
                date_str = date_match.group(1)
                try:
                    date = datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    try:
                        date = datetime.strptime(date_str, '%d-%m-%Y')
                    except ValueError:
                        date = datetime.now()
            else:
                date = datetime.now()

            transaction = {
                'fecha': date,
                'monto': float(amount),  # Asegurar que es float
                'descripcion': description.strip(),  # Limpiar espacios
                'categoria': 'Sin Categorizar',
                'moneda': currency,
                'tipo': 'real'
            }
            print(f"Transacción parseada: {transaction}")
            return transaction
        else:
            print("No se encontró ningún monto en el formato esperado")
            print(f"Contenido del correo: {email_content[:200]}...")

    except Exception as e:
        print(f"Error parseando el correo: {str(e)}")
        print(f"Contenido del correo: {email_content[:200]}...")
        return None

    return None