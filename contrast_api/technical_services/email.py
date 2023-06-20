from django.core.mail import send_mail


class EmailService:

    def send_email(self, recipient, from_email, subject, html_text):
        send_mail(subject=subject, recipient_list=[recipient], message=html_text, from_email=from_email)