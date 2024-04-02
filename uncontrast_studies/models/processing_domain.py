from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords


class UnConProcessingSubDomain(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return {self.name}


class UnConProcessingMainDomain(models.Model):
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
    main = models.ForeignKey(
        null=False, blank=False, to=UnConProcessingMainDomain, on_delete=CASCADE, related_name="processing_domains"
    )
    sub_domain = models.ForeignKey(
        null=True, blank=True, to=UnConProcessingSubDomain, on_delete=CASCADE, related_name="processing_domains"
    )
    history = HistoricalRecords()

    def __str__(self):
        if self.sub_domain is None:
            return f"{self.main}"
        return f"{self.main}; {self.sub_domain}"
