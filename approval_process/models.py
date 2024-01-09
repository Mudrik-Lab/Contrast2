from django.db import models
from django.db.models import CASCADE
from django.conf import settings

from approval_process.choices import ApprovalChoices


# Create your models here.


class ApprovalComment(models.Model):
    class Meta:
        ordering = ("created_at",)

    text = models.TextField(blank=False, null=False)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    process = models.ForeignKey("ApprovalProcess", on_delete=CASCADE, related_name="comments")


class ApprovalProcess(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(
        choices=ApprovalChoices.choices, null=False, blank=False, default=ApprovalChoices.PENDING
    )
    reviewers = models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name="approvals")
    exclusion_reason = models.TextField(null=True, blank=True)
    research_area = models.CharField(null=True, blank=True, max_length=50)  # currently only for excluded items
    sub_research_area = models.CharField(null=True, blank=True, max_length=50)  # currently only for excluded items
