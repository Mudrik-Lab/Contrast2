from django.db import models
from django.db.models import CASCADE


class Stimulus(models.Model):


    # TODO validator
    experiment = models.ForeignKey(null=False, blank=False, to="studies.Experiment",
                                   on_delete=CASCADE,
                                   related_name="stimuli")

    category = models.CharField(null=False, blank=False, max_length=50)
    sub_category = models.CharField(null=True, blank=True, max_length=50) # TODO validators from config
    modality = models.CharField(null=False, blank=False, max_length=50) # TODO validators from config
    description = models.TextField(null=True, blank=True)
    duration = models.PositiveBigIntegerField(null=True, blank=True)  # ms
