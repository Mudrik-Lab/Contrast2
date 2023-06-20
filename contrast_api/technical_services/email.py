import logging

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class EmailService:

    def send_email(self, recipient, from_email, subject, html_text):
        try:
            send_mail(subject=subject, recipient_list=[recipient], message=html_text, from_email=from_email)
        except Exception:
            logger.exception("Failing to send email")
            raise
