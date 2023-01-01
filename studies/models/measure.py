from django.db import models
from django.db.models import CASCADE


class Measure(models.Model):
    experiment = models.ForeignKey(null=False, blank=False, to="studies.Experiment",
                                   on_delete=CASCADE,
                                   related_name="measures")

    name = models.CharField(null=False, blank=False, max_length=50) # TODO configuration and validations
    notes = models.TextField(null=False, blank=False)