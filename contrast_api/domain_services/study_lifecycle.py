from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string

from approval_process.choices import ApprovalChoices
from approval_process.models import ApprovalProcess, ApprovalComment
from contrast_api.application_services.notifier import NotifierService
from studies.models import Study


class StudyLifeCycleService:
    def __init__(self):
        self.notifier = NotifierService()

    def submitted(self, submitter, study: Study):
        study.approval_status = ApprovalChoices.AWAITING_REVIEW
        study.save()
        submitter_subject = "Regarding your submission to ConTraSt database"

        data = dict(study=study, username=study.submitter.username)
        message = render_to_string("received_submission.html", data)
        self.notifier.notify_recipient(subject=submitter_subject, recipient=submitter.email, message=message)
        site_manager_subject = "A submission was received"
        message = render_to_string("study_submitted.html", data)
        self.notifier.notify_site_manager(subject=site_manager_subject, message=message)

    def approved(self, reviewer, studies: QuerySet[Study]):
        for study in studies:
            self._approve_study(reviewer, study)

    def pending(self, reviewer, studies: QuerySet[Study]):
        for study in studies:
            self._pending_study(reviewer, study)

    @transaction.atomic
    def _review_study(self, reviewer, study: Study):
        study.approval_status = ApprovalChoices.AWAITING_REVIEW
        study.save()
        ApprovalComment.objects.create(
            process=study.approval_process, reviewer=reviewer, text="Submission moved to review"
        )

    @transaction.atomic
    def _pending_study(self, reviewer, study: Study):
        study.approval_status = ApprovalChoices.PENDING
        study.save()

    @transaction.atomic
    def _approve_study(self, reviewer, study: Study):
        study.approval_status = ApprovalChoices.APPROVED
        study.save()
        ApprovalComment.objects.create(process=study.approval_process, reviewer=reviewer, text="Submission approved")
        data = dict(study=study, username=study.submitter.username)
        subject = "Regarding your submission to ConTraSt database"
        message = render_to_string("submission_approved.html", data)
        self.notifier.notify_recipient(subject=subject, recipient=study.submitter.email, message=message)

    def rejected(self, reviewer, studies: QuerySet[Study]):
        for study in studies:
            self._reject_study(reviewer, study)

    def reviewed(self, reviewer, studies: QuerySet[Study]):
        for study in studies:
            self._review_study(reviewer, study)

    @transaction.atomic
    def _reject_study(self, reviewer, study: Study):
        study.approval_status = ApprovalChoices.REJECTED
        study.save()
        ApprovalComment.objects.create(process=study.approval_process, reviewer=reviewer, text="Submission rejected")
        data = dict(study=study, username=study.submitter.username)
        subject = "Regarding your submission to ConTraSt database"
        message = render_to_string("submission_rejected.html", data)
        self.notifier.notify_recipient(subject=subject, recipient=study.submitter.email, message=message)
