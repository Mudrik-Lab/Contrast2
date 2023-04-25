from django.db import models
from django.db.models import CASCADE


class ConsciousnessMeasurePhaseType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=30)

    def __str__(self):
        return self.name


class ConsciousnessMeasureType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=30)

    def __str__(self):
        return self.name


class ConsciousnessMeasure(models.Model):
    experiment = models.ForeignKey(to="studies.Experiment", on_delete=CASCADE, related_name="consciousness_measures")
    phase = models.ForeignKey(blank=False, null=False, on_delete=CASCADE, to=ConsciousnessMeasurePhaseType, related_name="consciousness_measures")
    type = models.ForeignKey(blank=False, null=False, on_delete=CASCADE, to=ConsciousnessMeasureType, related_name="consciousness_measures")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"experiment: {self.experiment_id} phase {self.phase}, type {self.type}"
