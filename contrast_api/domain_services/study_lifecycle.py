from django.db import transaction
from django.db.models import QuerySet
from django.template.loader import render_to_string

from approval_process.choices import ApprovalChoices
from approval_process.models import ApprovalProcess, ApprovalComment
from contrast_api.application_services.notifier import NotifierService
from contrast_api.choices import StudyTypeChoices
from studies.models import Study


class StudyLifeCycleService:
    def __init__(self):
        self.notifier = NotifierService()

    def resolve_site_name_by_study_type(self, study_type):
        if study_type == StudyTypeChoices.UNCONSCIOUSNESS:
            return "UnConTraSt"
        else:
            return "ConTraSt"

    def submitted(self, submitter, study: Study):
        study.approval_status = ApprovalChoices.AWAITING_REVIEW
        study.save()
        site_name = self.resolve_site_name_by_study_type(study.type)
        submitter_subject = f"Regarding your submission to {site_name} database"

        data = dict(study=study, username=study.submitter.username, site_name=site_name)
        message = render_to_string("received_submission.html", data)
        self.notifier.notify_recipient(subject=submitter_subject, recipient=submitter.email, message=message)
        site_manager_subject = f"{site_name} submission was received"
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
        site_name = self.resolve_site_name_by_study_type(study.type)

        ApprovalComment.objects.create(process=study.approval_process, reviewer=reviewer, text="Submission approved")
        data = dict(study=study, username=study.submitter.username, site_name=site_name)
        subject = f"Regarding your submission to {site_name} database"
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
        site_name = self.resolve_site_name_by_study_type(study.type)

        data = dict(study=study, username=study.submitter.username, site_name=site_name)
        subject = f"Regarding your submission to {site_name} database"
        message = render_to_string("submission_rejected.html", data)
        self.notifier.notify_recipient(subject=subject, recipient=study.submitter.email, message=message)
