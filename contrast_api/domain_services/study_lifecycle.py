from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string

from approval_process.choices import ApprovalChoices
from approval_process.models import ApprovalProcess, ApprovalComment
from contrast_api.application_services.notifer import NotifierService
from studies.models import Study


class StudyLifeCycleService:
    def __init__(self):
        self.notifier = NotifierService()

    def submitted(self, submitter, study: Study):
        submitter_subject = "your submission was received"

        data = dict(study=study, username=study.submitter.username)
        message = render_to_string("approval_process/received_submission.html", data)
        self.notifier.notify_recipient(subject=submitter_subject, recipient=submitter.email, message=message)
        site_manager_subject = "A submission was received"
        message = render_to_string("approval_process/study_submitted.html", data)
        self.notifier.notify_site_manager(subject=site_manager_subject, message=message)

    def approved(self, reviewer, studies: QuerySet[Study]):
        for study in studies:
            self._approve_study(reviewer, study)

    @transaction.atomic
    def _approve_study(self, reviewer, study: Study):
        study.approval_status = ApprovalChoices.REJECTED
        study.save()
        ApprovalComment.objects.create(process=study.approval_process, reviewer=reviewer,
                                       text="Submission approved")
        data = dict(study=study, username=study.submitter.username)
        subject = "your submission was approved"
        message = render_to_string("approval_process/submission_approved.html", data)
        self.notifier.notify_recipient(subject=subject, recipient=study.submitter.email, message=message)

    def rejected(self, reviewer, studies: QuerySet[Study]):
        for study in studies:
            self._reject_study(reviewer, study)

    @transaction.atomic
    def _reject_study(self, reviewer, study: Study):
        study.approval_status = ApprovalChoices.REJECTED
        study.save()
        ApprovalComment.objects.create(process=study.approval_process, reviewer=reviewer, text="Submission rejected")
        data = dict(study=study, username=study.submitter.username)
        subject = "your submission was rejected"
        message = render_to_string("approval_process/submission_rejected.html", data)
        self.notifier.notify_recipient(subject=subject, recipient=study.submitter.email, message=message)
