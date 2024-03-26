from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords


class UnConProcessingSubDomain(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return {self.name}


class UnConProcessingDomain(models.Model):
    experiment = models.ForeignKey(
        null=False,
        blank=False,
        to="uncontrast_studies.UnConExperiment",
        on_delete=CASCADE,
        related_name="processing_domains",
    )
    name = models.CharField(null=False, blank=False, max_length=50)
    sub_domain = models.ForeignKey(
        null=False, blank=False, to=UnConProcessingSubDomain, on_delete=CASCADE, related_name="main_processing_domain"
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name}; {self.sub_domain}"
