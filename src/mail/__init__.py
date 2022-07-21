import threading
from src.mail.authentication import authenticate
from src.mail.message import build_message
from src import app


class MailService:

    def __init__(self):
        self.mail_service = authenticate()

    def send_email(self, destination, subject, body, attachments=None):
        app.logger.info(f"Sending email to {destination}")
        threading.Thread(target=self._send_message, args=(destination, subject, body, attachments)).start()

    def _send_message(self, destination, subject, body, attachments):
        try:
            self.mail_service.users().messages().send(
                userId="me", body=build_message(destination, subject, body, attachments)).execute()
            app.logger.info(f"Email sent to {destination}")
        except Exception as e:
            app.logger.error(f"Error sending email to {destination}: {e}")
            # TODO let dev know some other way.
