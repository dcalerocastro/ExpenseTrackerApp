import imaplib
import email
import os
from datetime import datetime, timedelta
from email import policy
from .email_parser import parse_email_content

class EmailReader:
    def __init__(self, email_user, email_password):
        self.email_user = email_user
        self.email_password = email_password
        self.imap_server = "imap.gmail.com"  # Por defecto Gmail

        # Configuración por banco
        self.bank_configs = {
            'BCP': {
                'sender': "notificaciones@notificacionesbcp.com.pe",
                'subject_filter': None
            },
            'INTERBANK': {
                'sender': "noreply@interbank.com.pe",
                'subject_filter': "Aviso de Operación"
            },
            'SCOTIABANK': {
                'sender': "noreply@scotiabank.com.pe",
                'subject_filter': "Alerta de Transacción"
            }
        }

    def connect(self):
        """Establece conexión con el servidor IMAP"""
        try:
            print(f"Intentando conectar a {self.imap_server} con usuario {self.email_user}")
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.email_user, self.email_password)
            print("Conexión IMAP exitosa")
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

    def fetch_notifications(self, days_back=30, bank='BCP'):
        """
        Busca y procesa correos de notificaciones del banco especificado
        """
        if bank not in self.bank_configs:
            raise ValueError(f"Banco no soportado: {bank}")

        bank_config = self.bank_configs[bank]
        transactions = []

        try:
            if not hasattr(self, 'imap'):
                if not self.connect():
                    return transactions

            self.imap.select('INBOX')
            print("Bandeja INBOX seleccionada")

            # Calcular la fecha límite
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            print(f"Buscando correos desde: {since_date}")

            # Construir query de búsqueda
            search_query = f'FROM "{bank_config["sender"]}" SINCE "{since_date}"'
            if bank_config['subject_filter']:
                search_query += f' SUBJECT "{bank_config["subject_filter"]}"'

            print(f"Ejecutando búsqueda con query: {search_query}")
            result, messages = self.imap.search(None, search_query)
            print(f"Resultado de búsqueda: {result}")

            if result == 'OK' and messages[0]:
                message_nums = messages[0].split()
                print(f"Se encontraron {len(message_nums)} correos para procesar")

                for num in message_nums:
                    try:
                        # Obtener el correo
                        _, msg_data = self.imap.fetch(num, '(RFC822)')
                        if not msg_data or not msg_data[0]:
                            print(f"No se pudo obtener datos del correo {num}")
                            continue

                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body, policy=policy.default)

                        # Imprimir el asunto para debugging
                        print(f"Procesando correo con asunto: {email_message['subject']}")

                        # Extraer el contenido del correo
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        content = part.get_payload(decode=True).decode('utf-8')
                                    except UnicodeDecodeError:
                                        content = part.get_payload(decode=True).decode('latin-1')

                                    transaction = parse_email_content(content, bank=bank)
                                    if transaction:
                                        transactions.append(transaction)
                                        print(f"Transacción encontrada: {transaction}")
                                    break
                        else:
                            try:
                                content = email_message.get_payload(decode=True).decode('utf-8')
                            except UnicodeDecodeError:
                                content = email_message.get_payload(decode=True).decode('latin-1')

                            transaction = parse_email_content(content, bank=bank)
                            if transaction:
                                transaction['tipo'] = 'real'  # Marcar como transacción real
                                if all(key in transaction for key in ['fecha', 'monto', 'descripcion']):
                                    transactions.append(transaction)
                                    print(f"Transacción encontrada y validada: {transaction}")
                                else:
                                    print(f"Transacción incompleta, falta algún campo requerido: {transaction}")

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