from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, Q
from simple_history.models import HistoricalRecords

from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices, ExperimentTypeChoices
from studies.managers import ExperimentManager


class UnConExperiment(models.Model):
    """
    This is a major model here, lots of data "belongs" to the experiment in related models, so the experiment is codified there
    """

    class Meta:
        ordering = ["id"]

    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="uncon_experiments")
    # results_summary is nullable at the beginning, when finding tags are created it should be populated
    results_summary = models.TextField(null=True, blank=True)
    techniques = models.ManyToManyField(to="uncontrast_studies.UnConTechnique", related_name="uncon_experiments")  # validator at least one
    processing_domains = models.ManyToManyField(to="uncontrast_studies.UnConProcessingDomain", related_name="uncon_experiments")  # validator at least one

    type_of_consciousness = models.CharField(
        null=False, blank=False, choices=TypeOfConsciousnessChoices.choices, max_length=20
    )
    type_of_evidence = models.CharField() # TODO: is this a configurable field e.g a model - like techniques
    type_of_attention = models.CharField() # TODO: is this a configurable field e.g a model- like techniques
    is_reporting = models.CharField(null=False, blank=False, choices=ReportingChoices.choices, max_length=20)
    # TODO: check if we need notes, check if we need is_reporting
    # tasks_notes = models.TextField(null=True, blank=True)
    # consciousness_measures_notes = models.TextField(null=True, blank=True)
    # stimuli_notes = models.TextField(null=True, blank=True)

    type = models.PositiveIntegerField(
        null=False, blank=False, choices=ExperimentTypeChoices.choices, default=ExperimentTypeChoices.NEUROSCIENTIFIC
    )
    # TODO: check if we need notes

    # sample_notes = models.TextField(null=True, blank=True)
    history = HistoricalRecords()
    # objects = ExperimentManager()

    def clean(self):
        super().clean()
        # TODO: check what the cleaning needed
        # if self.paradigms.count() == 0 or self.paradigms is None:
        #     raise ValidationError({"paradigms": "There should be at least one"})
        # if self.techniques.count() == 0 or self.techniques is None:
        #     raise ValidationError({"techniques": "There should be at least one"})

    def __str__(self):
        return f"study {self.study_id}, id {self.id}"
