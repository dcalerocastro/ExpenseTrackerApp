import imaplib
import email
import os
from datetime import datetime
from email import policy
from .email_parser import parse_email_content

class EmailReader:
    def __init__(self, email_user, email_password):
        self.email_user = email_user
        self.email_password = email_password
        self.imap_server = "imap.gmail.com"  # Por defecto Gmail
        
    def connect(self):
        """Establece conexión con el servidor IMAP"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.email_user, self.email_password)
            return True
        except Exception as e:
            print(f"Error de conexión: {str(e)}")
            return False
            
    def fetch_bcp_notifications(self, days_back=30):
        """
        Busca y procesa correos de notificaciones del BCP
        """
        transactions = []
        try:
            if not hasattr(self, 'imap'):
                if not self.connect():
                    return transactions
                    
            self.imap.select('INBOX')
            
            # Buscar correos del BCP
            search_criteria = '(SUBJECT "Realizaste un consumo con tu Tarjeta de Crédito BCP - Servicio de Notificaciones BCP")'
            result, messages = self.imap.search(None, search_criteria)
            
            if result == 'OK':
                for num in messages[0].split():
                    try:
                        # Obtener el correo
                        _, msg_data = self.imap.fetch(num, '(RFC822)')
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body, policy=policy.default)
                        
                        # Procesar el contenido
                        if email_message:
                            transaction = parse_email_content(email_message.as_string())
                            if transaction:
                                transactions.append(transaction)
                    except Exception as e:
                        print(f"Error procesando correo: {str(e)}")
                        continue
                        
            return transactions
            
        except Exception as e:
            print(f"Error buscando correos: {str(e)}")
            return transactions
            
        finally:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
