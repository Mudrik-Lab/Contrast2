from django.db import models
from django.db.models import CASCADE, PROTECT
from simple_history.models import HistoricalRecords


class UnConProcessingMainDomain(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return self.name


class UnConProcessingDomain(models.Model):
    experiment = models.ForeignKey(
        null=False,
        blank=False,
        to="uncontrast_studies.UnConExperiment",
        on_delete=CASCADE,
        related_name="processing_domains",
    )
    main = models.ForeignKey(
        null=False, blank=False, to=UnConProcessingMainDomain, on_delete=PROTECT, related_name="processing_domains"
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.main}"

