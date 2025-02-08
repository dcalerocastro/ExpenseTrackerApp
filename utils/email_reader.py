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
        except imaplib.IMAP4.error as e:
            error_msg = str(e)
            if "Application-specific password required" in error_msg:
                raise Exception(
                    "Se requiere una contraseña de aplicación de Google. Por favor:\n"
                    "1. Ve a https://myaccount.google.com/security\n"
                    "2. Activa la verificación en dos pasos si no está activada\n"
                    "3. Ve a 'Contraseñas de aplicación'\n"
                    "4. Genera una nueva contraseña para 'Streamlit App'\n"
                    "5. Usa esa contraseña en lugar de tu contraseña normal de Gmail"
                )
            else:
                raise Exception(f"Error al conectar con Gmail: {error_msg}")

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

            # Buscar correos del BCP usando formato correcto de IMAP
            search_query = 'SUBJECT "Realizaste un consumo con tu Tarjeta de Credito BCP - Servicio de Notificaciones BCP"'
            result, messages = self.imap.search(None, search_query)

            if result == 'OK' and messages[0]:
                message_nums = messages[0].split()
                print(f"Se encontraron {len(message_nums)} correos para procesar")

                for num in message_nums:
                    try:
                        # Obtener el correo
                        _, msg_data = self.imap.fetch(num, '(RFC822)')
                        if not msg_data or not msg_data[0]:
                            continue

                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body, policy=policy.default)

                        # Extraer el contenido del correo
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        content = part.get_payload(decode=True).decode('utf-8')
                                    except UnicodeDecodeError:
                                        content = part.get_payload(decode=True).decode('latin-1')

                                    transaction = parse_email_content(content)
                                    if transaction:
                                        transactions.append(transaction)
                                    break
                        else:
                            try:
                                content = email_message.get_payload(decode=True).decode('utf-8')
                            except UnicodeDecodeError:
                                content = email_message.get_payload(decode=True).decode('latin-1')

                            transaction = parse_email_content(content)
                            if transaction:
                                transactions.append(transaction)

                    except Exception as e:
                        print(f"Error procesando correo individual: {str(e)}")
                        continue

            return transactions

        except Exception as e:
            print(f"Error general buscando correos: {str(e)}")
            raise Exception(f"Error al buscar correos: {str(e)}")

        finally:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass