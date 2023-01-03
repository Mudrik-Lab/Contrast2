from django.db import models
from django.db.models import CASCADE


class ConsciousnessMeasurePhaseType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=30)


class ConsciousnessMeasureType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=30)


class ConsciousnessMeasure(models.Model):
    experiment = models.ForeignKey(to="studies.Experiment", on_delete=CASCADE, related_name="consciousness_measures")
    phase = models.ForeignKey(blank=False, null=False, on_delete=CASCADE, to=ConsciousnessMeasurePhaseType)
    type = models.ForeignKey(blank=False, null=False, on_delete=CASCADE, to=ConsciousnessMeasureType)
    description = models.TextField(null=True, blank=True)

