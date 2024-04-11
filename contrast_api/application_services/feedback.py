from django.template.loader import render_to_string

from contrast_api.application_services.notifier import NotifierService


class FeedbackService:
    def __init__(self, site: str):
        self.notifier = NotifierService()
        self.site = site

    def vet_a_paper(self, data):
        subject = f"{self.site}: Vet a paper request received"
        message = render_to_string("vet_a_paper.html", data)
        self.notifier.notify_feedback(subject, message)

    def contact_us(self, data):
        subject = f"{self.site}: Contact request received"
        message = render_to_string("contact_us.html", data)
        self.notifier.notify_feedback(subject, message)

    def site_feedback(self, data):
        subject = f"{self.site}: Site feedback received"
        message = render_to_string("site_feedback.html", data)
        self.notifier.notify_feedback(subject, message)

    def suggest_query(self, data):
        subject = f"{self.site}: New query suggestion received"
        message = render_to_string("suggest_query.html", data)
        self.notifier.notify_feedback(subject, message)
