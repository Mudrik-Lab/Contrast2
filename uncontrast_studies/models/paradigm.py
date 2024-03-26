from django.db import models
from django.db.models import PROTECT, CASCADE


class UnConMainParadigm(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self):
        return self.name


class UnConSpecificParadigm(models.Model):
    main = models.ForeignKey(
        null=True,
        blank=True,
        related_name="specific_paradigm",
        to=UnConMainParadigm,
        on_delete=CASCADE,
    )
    name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self):
        return self.name


class UnConParadigm(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="paradigms"
    )
    main = models.ForeignKey(
        null=True,
        blank=True,
        related_name="paradigms",
        to=UnConMainParadigm,
        on_delete=PROTECT,
    )
    specific = models.ForeignKey(
        null=True, blank=True, related_name="paradigms", to=UnConSpecificParadigm, on_delete=PROTECT
    )

    def __str__(self):
        return f"{self.main}; {self.specific}"
