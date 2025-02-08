import email
from email import policy
from datetime import datetime
import re

def parse_email_content(email_content):
    """
    Parse email content to extract transaction details.
    Assumes common Peruvian bank email notification formats.
    """
    try:
        # Extract information using regex patterns
        # Amount pattern (assuming Peruvian Soles format S/ XX.XX)
        amount_pattern = r'S/\s*(\d+(?:\.\d{2})?)'
        amount_match = re.search(amount_pattern, email_content)

        # Date pattern (mantener flexible para diferentes formatos)
        date_pattern = r'(\d{1,2}(?:/|-)\d{1,2}(?:/|-)\d{2,4})'
        date_match = re.search(date_pattern, email_content)

        # Description pattern (línea que contiene el monto)
        description = None
        for line in email_content.split('\n'):
            if 'S/' in line:
                description = line.strip()
                print(f"Línea con monto encontrada: {line.strip()}")
                break

        if amount_match:
            amount = amount_match.group(1)
            amount = float(amount)
            print(f"Monto extraído: S/ {amount:.2f}")

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

            return {
                'fecha': date,
                'monto': amount,
                'descripcion': description or 'Sin descripción',
                'categoria': 'Sin Categorizar'
            }
        else:
            print("No se encontró ningún monto en formato S/ XX.XX")
            print(f"Contenido del correo: {email_content[:200]}...")  # Primeros 200 caracteres para debug

    except Exception as e:
        print(f"Error parseando el correo: {str(e)}")
        print(f"Contenido del correo: {email_content[:200]}...")  # Primeros 200 caracteres para debug
        return None

    return None