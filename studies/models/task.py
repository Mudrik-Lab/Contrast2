from django.db import models
from django.db.models import CASCADE


class Task(models.Model):
    experiment = models.ForeignKey(null=False, blank=False, to="studies.Experiment",
                                   on_delete=CASCADE,
                                   related_name="tasks")

    description = models.TextField(null=False, blank=False)
    type = models.CharField(null=False, blank=False, max_length=30)  # TODO validators from configuration
