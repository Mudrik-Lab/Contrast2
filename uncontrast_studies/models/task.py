from django.db import models
from django.db.models import CASCADE, PROTECT
from simple_history.models import HistoricalRecords


class UnConTaskType(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return self.name


class UnConTask(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="tasks"
    )

    type = models.ForeignKey(
        null=False, blank=False, on_delete=PROTECT, to=UnConTaskType
    )  # TODO validators from configuration
    history = HistoricalRecords()

    def __str__(self):
        return f"experiment: {self.experiment_id}, type {self.type}"
