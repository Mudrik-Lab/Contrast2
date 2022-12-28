from django.db.models import CASCADE, SET_NULL
from django.db import models

from approval_process.choices import ApprovalChoices


# from studies.models.author import Author


class Study(models.Model):
    # TODO should it be through affiliation?
    # authors = models.ManyToManyField(to=Author, related_name="studies", )
    name = models.TextField(null=False, blank=False)
    approval_process = models.OneToOneField(null=True,
                                            blank=True,
                                            to="approval_process.ApprovalProcess",
                                            on_delete=SET_NULL)
    approval_status = models.IntegerField(choices=ApprovalChoices.choices, null=False, blank=False,
                                          default=ApprovalChoices.PENDING)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # TODO: add creation of approval process here
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
