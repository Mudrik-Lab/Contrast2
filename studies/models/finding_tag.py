from django.db import models
from django.db.models import IntegerChoices, TextChoices, SET_NULL, CASCADE

from studies.choices import AnalysisTypeChoices, CorrelationSignChoices


class FindingTag(models.Model):
    # TODO validator + custom admin form
    experiment = models.ForeignKey(null=False, blank=False, to="studies.Experiment",
                                   on_delete=CASCADE,
                                   related_name="finding_tags")
    family = models.CharField(null=False, blank=False, max_length=100)
    name = models.CharField(null=False, blank=True, max_length=100)
    onset = models.PositiveBigIntegerField(null=True, blank=True)  # ms
    offset = models.PositiveBigIntegerField(null=True, blank=True)  # ma
    band_lower_bound = models.PositiveBigIntegerField(null=True, blank=True)  # HZ
    band_higher_bound = models.PositiveBigIntegerField(null=True, blank=True)  # HZ
    AAL_atlas_tag = models.CharField(null=True, blank=True, max_length=100)
    notes = models.TextField(null=True, blank=True)
    analysis_type = models.CharField(null=True, blank=True, max_length=100,
                                     choices=AnalysisTypeChoices.choices,
                                     default=AnalysisTypeChoices.POWER)
    correlation_sign = models.CharField(null=True, blank=True, max_length=10,
                                        choices=CorrelationSignChoices.choices,
                                        default=CorrelationSignChoices.POSITIVE)
    technique = models.ForeignKey(null=True, blank=True, to="studies.Technique", related_name="findings_tags",
                                  on_delete=SET_NULL)