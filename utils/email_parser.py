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
        # Amount pattern (assuming Peruvian Soles)
        amount_pattern = r'S/\.\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        amount_match = re.search(amount_pattern, email_content)

        # Date pattern
        date_pattern = r'(\d{1,2}(?:/|-)\d{1,2}(?:/|-)\d{2,4})'
        date_match = re.search(date_pattern, email_content)

        # Description pattern (assumes description is between amount and date)
        description = None
        lines = email_content.strip().split('\n')
        for line in lines:
            if "consumo" in line.lower():
                description = line.strip()
                break
        if not description:
            description = lines[0].strip()  # Fallback to first line

        if amount_match and date_match:
            amount = amount_match.group(1).replace(',', '')
            amount = float(amount)

            # Parse date
            date_str = date_match.group(1)
            try:
                date = datetime.strptime(date_str, '%d/%m/%Y')
            except ValueError:
                try:
                    date = datetime.strptime(date_str, '%d-%m-%Y')
                except ValueError:
                    date = datetime.now()

            return {
                'fecha': date,
                'monto': amount,
                'descripcion': description,
                'categoria': 'Sin Categorizar'  # Default category
            }
    except Exception as e:
        print(f"Error parsing email: {str(e)}")
        print(f"Email content: {email_content[:200]}...")  # Print first 200 chars for debugging
        return None

    return None