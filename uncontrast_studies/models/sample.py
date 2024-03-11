from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords

from studies.choices import SampleChoices


class UnConSample(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="samples"
    )

    type = models.CharField(null=False, blank=False, choices=SampleChoices.choices, max_length=30)
    # TODO: check if total_size is needed
    # total_size = models.IntegerField(null=False, blank=False)
    size_included = models.IntegerField(null=False, blank=False)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.type}, total: {self.total_size}, included: {self.size_included}"
