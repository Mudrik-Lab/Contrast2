import logging

from django.template.loader import render_to_string

from django.utils.safestring import mark_safe
from rest_framework.request import Request

from contrast_api.locator import ServiceLocator
import urllib.parse
from django.conf import settings

logger = logging.getLogger(__name__)


class NotifierService:
    """
    Applicative abstraction contains templates. and uses the email service
    """

    def __init__(self):
        self.email_service = ServiceLocator.get_service("EMAIL_SERVICE")
        self.default_from_email = settings.DEFAULT_FROM_EMAIL

    def notify_feedback(self, subject, message):
        recipient = settings.SITE_MANAGER_ADDRESS
        logger.info(f"Sending feedback notification with subject: {subject}")
        self.email_service.send_email(
            subject=subject, recipient=recipient, from_email=self.default_from_email, html_text=message
        )

    def notify_reset_password_request(self, request: Request, recipient, **kwargs):
        subject = "Reset your ContrastDb password"
        quoted_email = urllib.parse.quote_plus(recipient)
        reset_email_link = mark_safe(
            f"{request.scheme}://{request.get_host()}/reset_password?email={quoted_email}&token={kwargs['token']}"
        )
        message = render_to_string(
            "password_reset_email.html", {"user": kwargs["user"], "reset_email_link": reset_email_link}
        )
        logger.info(f"Sending reset password notification for {quoted_email} with message {message}")
        self.email_service.send_email(
            subject=subject, recipient=recipient, from_email=self.default_from_email, html_text=message
        )

    def notify_recipient(self, recipient, subject, message, **kwargs):
        logger.info(f"Recipient notification with subject: {subject}")
        self.email_service.send_email(
            subject=subject, recipient=recipient, from_email=self.default_from_email, html_text=message
        )

    def notify_site_manager(self, message, subject):
        recipient = settings.SITE_MANAGER_ADDRESS
        logger.info(f"Site manager notification with subject: {subject}")
        self.email_service.send_email(
            subject=subject, recipient=recipient, from_email=self.default_from_email, html_text=message
        )
