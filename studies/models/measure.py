from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords


class MeasureType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Measure(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="studies.Experiment", on_delete=CASCADE, related_name="measures"
    )

    type = models.ForeignKey(null=False, blank=False, to=MeasureType, related_name="measures", on_delete=CASCADE)
    notes = models.TextField(null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"experiment: {self.experiment_id}  type {self.type}"
