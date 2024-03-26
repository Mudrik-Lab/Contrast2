from django.db import models
from django.db.models import CASCADE, PROTECT


class UnConSuppressionMethodType(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return self.name


class UnConSuppressionMethodSubType(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50)
    parent = models.ForeignKey(
        null=False, blank=False, related_name="subtypes", to=UnConSuppressionMethodType, on_delete=CASCADE
    )

    def __str__(self):
        return self.name


class UnConSuppressionMethod(models.Model):
    experiment = models.ForeignKey(
        null=False,
        blank=False,
        to="uncontrast_studies.UnConExperiment",
        on_delete=CASCADE,
        related_name="suppression_methods",
    )
    type = models.ForeignKey(
        null=False, blank=False, related_name="suppression_method", to=UnConSuppressionMethodType, on_delete=PROTECT
    )
    sub_type = models.ForeignKey(
        null=True, blank=True, related_name="suppression_method", to=UnConSuppressionMethodSubType, on_delete=PROTECT
    )  # TODO: add validation for masking

    def __str__(self):
        if self.sub_type is None:
            return f"experiment: {self.experiment_id}, suppression method: {self.type}"
        return f"experiment: {self.experiment_id}, suppression method: {self.type} ({self.sub_type})"
