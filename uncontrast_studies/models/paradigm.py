from django.db import models
from django.db.models import PROTECT, CASCADE


class UnConMainParadigm(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self):
        return self.name


class UnConSpecificParadigm(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="paradigms"
    )
    main = models.ForeignKey(
        null=False,
        blank=False,
        related_name="specific_paradigm",
        to=UnConMainParadigm,
        on_delete=CASCADE,
    )
    name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self):
        return f"{self.main}; {self.name}"
