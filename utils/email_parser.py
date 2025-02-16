import email
from email import policy
from datetime import datetime
import re

def parse_email_content(email_content, bank='BCP'):
    """
    Parse email content to extract transaction details.
    """
    try:
        print(f"\n=== Parseando correo del {bank} ===")
        print(f"Contenido: {email_content[:200]}...")

        # Patrones específicos por banco
        patterns = {
            'BCP': {
                'amount': r'(?:S/|US\$)\s*(\d+(?:\.\d{2})?)',
                'date': r'(\d{1,2}(?:/|-)\d{1,2}(?:/|-)\d{2,4})',
                'merchant': r'en\s*<b>(.*?)</b>'
            },
            'INTERBANK': {
                'amount': r'(?:S/\.|US\$)\s*(\d+(?:\.\d{2})?)',
                'date': r'(\d{1,2}/\d{1,2}/\d{4})',
                'merchant': r'en\s*(.*?)\s*por'
            },
            'SCOTIABANK': {
                'amount': r'(?:S/\.|US\$)\s*(\d+(?:\.\d{2})?)',
                'date': r'(\d{1,2}/\d{1,2}/\d{4})',
                'merchant': r'en\s*(.*?)\s*fue'
            }
        }

        if bank not in patterns:
            raise ValueError(f"Banco no soportado: {bank}")

        bank_patterns = patterns[bank]

        # Extract amount and determine currency
        amount_match = re.search(bank_patterns['amount'], email_content)
        currency = 'PEN' if 'S/' in email_content else 'USD' if 'US$' in email_content else 'PEN'

        # Extract date
        date_match = re.search(bank_patterns['date'], email_content)

        # Extract merchant name
        merchant_match = re.search(bank_patterns['merchant'], email_content)

        if amount_match:
            amount = float(amount_match.group(1))
            print(f"Monto extraído: {amount:.2f} {currency}")

            # Get merchant name or use default
            description = (merchant_match.group(1) if merchant_match 
                         else 'Transacción sin comercio')
            description = description.strip().replace('<b>', '').replace('</b>', '')
            print(f"Comercio extraído: {description}")

            # Parse date
            if date_match:
                date_str = date_match.group(1)
                try:
                    # Try different date formats
                    for date_format in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y']:
                        try:
                            date = datetime.strptime(date_str, date_format)
                            break
                        except ValueError:
                            continue
                    else:
                        date = datetime.now()
                except Exception:
                    date = datetime.now()
            else:
                date = datetime.now()

            transaction = {
                'fecha': date,
                'monto': float(amount),  # Asegurar que es float
                'descripcion': description,  # Limpiar espacios y tags HTML
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
        print(f"Error parseando el correo del {bank}: {str(e)}")
        print(f"Contenido del correo: {email_content[:200]}...")
        return None

    return None