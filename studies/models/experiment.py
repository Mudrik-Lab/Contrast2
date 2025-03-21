from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, Q
from simple_history.models import HistoricalRecords

from contrast_api.choices import (
    TypeOfConsciousnessChoices,
    ReportingChoices,
    TheoryDrivenChoices,
    ExperimentTypeChoices,
)
from studies.managers import ExperimentManager


class Experiment(models.Model):
    """
    This is a major model here, lots of data "belongs" to the experiment in related models, so the experiment is codified there
    """

    class Meta:
        ordering = ["id"]

    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="experiments")
    # results_summary is nullable at the beginning, when finding tags are created it should be populated
    results_summary = models.TextField(null=True, blank=True)
    techniques = models.ManyToManyField(to="studies.Technique", related_name="experiments")  # validator at least one
    interpretations = models.ManyToManyField(
        to="studies.Theory",
        related_name="experiments_interpretations",
        limit_choices_to=Q(parent__isnull=False),
        through="studies.Interpretation",
    )
    paradigms = models.ManyToManyField(
        to="studies.Paradigm", related_name="experiments", limit_choices_to=Q(parent__isnull=False)
    )  # validator at least one
    type_of_consciousness = models.CharField(
        null=False, blank=False, choices=TypeOfConsciousnessChoices.choices, max_length=20
    )
    is_reporting = models.CharField(null=False, blank=False, choices=ReportingChoices.choices, max_length=20)
    theory_driven = models.CharField(null=False, blank=False, choices=TheoryDrivenChoices.choices, max_length=20)
    tasks_notes = models.TextField(null=True, blank=True)
    consciousness_measures_notes = models.TextField(null=True, blank=True)
    stimuli_notes = models.TextField(null=True, blank=True)
    paradigms_notes = models.TextField(null=True, blank=True)
    theory_driven_theories = models.ManyToManyField(
        to="studies.Theory",
        related_name="experiments_driven",
        limit_choices_to=Q(parent__isnull=False),
    )
    type = models.PositiveIntegerField(
        null=False, blank=False, choices=ExperimentTypeChoices.choices, default=ExperimentTypeChoices.NEUROSCIENTIFIC
    )
    sample_notes = models.TextField(null=True, blank=True)
    history = HistoricalRecords()
    objects = ExperimentManager()

    def __str__(self):
        return f"study {self.study_id}, id {self.id}"
