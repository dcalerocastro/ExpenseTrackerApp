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
        # Parse email
        msg = email.message_from_string(email_content, policy=policy.default)
        
        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        
        # Extract information using regex patterns
        # Amount pattern (assuming Peruvian Soles)
        amount_pattern = r'S/\.\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        amount_match = re.search(amount_pattern, body)
        
        # Date pattern
        date_pattern = r'(\d{1,2}(?:/|-)\d{1,2}(?:/|-)\d{2,4})'
        date_match = re.search(date_pattern, body)
        
        # Description pattern (assumes description is between amount and date)
        description = body.strip().split('\n')[0]  # Simple approach: take first line
        
        if amount_match and date_match:
            amount = float(amount_match.group(1).replace(',', ''))
            
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
        return None
    
    return None
