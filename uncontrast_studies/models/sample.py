from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords

from contrast_api.choices import UnConSampleChoices


class UnConSample(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="samples"
    )
    type = models.CharField(null=False, blank=False, choices=UnConSampleChoices.choices, max_length=30)
    size_included = models.IntegerField(null=False, blank=False)
    size_total = models.IntegerField(null=False, blank=False)
    size_excluded = models.IntegerField(
        null=True, blank=True, verbose_name="how many participants were excluded based on awareness measure?"
    )

    history = HistoricalRecords()

    def __str__(self):
        if self.size_excluded is None:
            return f"{self.type}, included: {self.size_included}"
        return f"{self.type}, included: {self.size_included}, excluded: {self.size_excluded}"
