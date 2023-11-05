from django.db import models
from django.db.models import SET_NULL
from simple_history.models import HistoricalRecords


class Paradigm(models.Model):
    parent = models.ForeignKey(
        null=True, blank=True, related_name="child_paradigm", to="studies.Paradigm", on_delete=SET_NULL
    )
    name = models.CharField(null=False, blank=False, max_length=100)
    sub_type = models.CharField(null=True, blank=True, max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        if self.sub_type is None:
            return f"{self.name}"
        else:
            return f"{self.name}, sub-type: {self.sub_type}"
