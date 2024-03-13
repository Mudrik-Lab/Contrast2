from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords

from contrast_api.choices import SampleChoices


class Sample(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="studies.Experiment", on_delete=CASCADE, related_name="samples"
    )

    type = models.CharField(null=False, blank=False, choices=SampleChoices.choices, max_length=30)
    total_size = models.IntegerField(null=False, blank=False)
    size_included = models.IntegerField(null=False, blank=False)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.type}, total: {self.total_size}, included: {self.size_included}"
