from django.db import models
from django.db.models import PROTECT
from simple_history.models import HistoricalRecords


class UnConMainParadigm(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self):
        return self.name


class UnConSpecificParadigm(models.Model):
    main = models.ForeignKey(
        null=False,
        blank=False,
        related_name="specific_paradigm",
        to=UnConMainParadigm,
        on_delete=PROTECT,
    )
    name = models.CharField(null=False, blank=False, max_length=100)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.main}; {self.name}"
