from django.template.loader import render_to_string

from contrast_api.application_services.notifer import NotifierService


class StudyLifeCycleService:
    def __init__(self):
        self.notifier = NotifierService()

    def submitted(self, submitter, data):
        submitter_subject = "your submission was received"
        message = render_to_string("approval_process/received_submission.html", data)
        self.notifier.notify_recipient(subject=submitter_subject, recipient=submitter.email, message=message)
        site_manager_subject = "A submission was received"
        message = render_to_string("approval_process/study_submitted.html", data)
        self.notifier.notify_site_manager(subject=site_manager_subject, message=message)
