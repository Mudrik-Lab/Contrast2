from django.db import models
from simple_history.models import HistoricalRecords


class Author(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name}"
