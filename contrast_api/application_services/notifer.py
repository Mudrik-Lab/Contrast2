import logging

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from rest_framework.request import Request

from contrast_api.locator import ServiceLocator
import urllib.parse

logger = logging.getLogger(__name__)


class NotifierService:
    """
    Applicative abstraction contains templates. and uses the email service
    """

    def __init__(self):
        self.email_service = ServiceLocator.get_service("EMAIL_SERVICE")

    def notify_site_feedback(self, request, **kwargs):
        pass

    def notify_reset_password_request(self, request: Request, recipient, **kwargs):
        subject = 'Reset your ContrastDb password'
        quoted_email = urllib.parse.quote_plus(recipient)
        reset_email_link = mark_safe(
            f'{request.scheme}://{request.get_host()}/reset_password?email={quoted_email}&token={kwargs["token"]}')
        message = render_to_string('password_reset_email.html', {
            'user': kwargs["user"],
            'reset_email_link': reset_email_link
        })
        logger.info(f"Sending reset password notification for {quoted_email} with message {message}")

    def notify_study_status_change(self, request, recipient, **kwargs):
        pass
