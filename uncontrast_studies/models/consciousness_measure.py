from django.db import models
from django.db.models import CASCADE


class UnConsciousnessMeasurePhaseType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=30)

    def __str__(self):
        return self.name


class UnConsciousnessMeasureType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=30)

    def __str__(self):
        return self.name


class UnConsciousnessMeasure(models.Model):
    experiment = models.ForeignKey(to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="unconsciousness_measures")
    phase = models.ForeignKey(
        blank=False,
        null=False,
        on_delete=CASCADE,
        to=UnConsciousnessMeasurePhaseType,
        related_name="unconsciousness_measures",
    )
    type = models.ForeignKey(
        blank=False, null=False, on_delete=CASCADE, to=UnConsciousnessMeasureType, related_name="unconsciousness_measures"
    )

    def __str__(self):
        return f"experiment: {self.experiment_id} phase {self.phase}, type {self.type}"
