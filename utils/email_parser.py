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
        print(f"\nIniciando parseo de correo...")
        # Extract information using regex patterns
        # Amount pattern (assuming Peruvian Soles format S/ XX.XX)
        amount_pattern = r'S/\.?\s*(\d+(?:[.,]\d{2})?)'
        amount_matches = re.finditer(amount_pattern, email_content)
        amounts = [float(match.group(1).replace(',', '.')) for match in amount_matches]

        if amounts:
            amount = max(amounts)  # Tomamos el monto más alto si hay varios
            print(f"Monto encontrado: S/ {amount:.2f}")
        else:
            print("No se encontró ningún monto en formato S/ XX.XX")
            print(f"Contenido del correo: {email_content[:200]}...")  # Primeros 200 caracteres para debug
            return None

        # Date pattern (mantener flexible para diferentes formatos)
        date_pattern = r'(\d{1,2}(?:/|-)\d{1,2}(?:/|-)\d{2,4})'
        date_match = re.search(date_pattern, email_content)

        # Description pattern (extraer comercio del mensaje)
        description = None
        merchant_patterns = [
            r'en\s+(?:<[^>]+>)?([^<]+)(?:</[^>]+>)?',  # Patrón para "en Comercio"
            r'(?:consumo|cargo|pago)[^\n]*?(?:en|con)\s+([^\n.]+)',  # Patrón alternativo
            r'(?:realizado en|hecho en)\s+([^\n.]+)'  # Otro patrón alternativo
        ]

        for pattern in merchant_patterns:
            merchant_match = re.search(pattern, email_content, re.IGNORECASE)
            if merchant_match:
                description = merchant_match.group(1).strip()
                break

        if not description:
            description = "Consumo BCP"

        print(f"Descripción extraída: {description}")

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

    except Exception as e:
        print(f"Error parseando el correo: {str(e)}")
        print(f"Contenido del correo: {email_content[:200]}...")  # Primeros 200 caracteres para debug
        return None

    return None