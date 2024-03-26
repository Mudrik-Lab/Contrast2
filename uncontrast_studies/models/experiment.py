from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords

from contrast_api.choices import ExperimentTypeChoices, ExperimentSuppressedStimuliChoices


class UnConExperiment(models.Model):
    """
    This is a major model here, lots of data "belongs" to the experiment in related models, so the experiment is codified there
    """

    class Meta:
        ordering = ["id"]

    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="uncon_experiments")
    type = models.PositiveIntegerField(
        null=False, blank=False, choices=ExperimentTypeChoices.choices, default=ExperimentTypeChoices.NEUROSCIENTIFIC
    )

    # Stimuli metadata
    is_target_stimulus = models.BooleanField(
        null=False, blank=False, verbose_name="are there also non-suppressed stimuli"
    )
    is_target_same_as_suppressed_stimulus = models.BooleanField(
        null=False, blank=False, verbose_name="is the non-suppressed stimulus the same as the suppressed stimulus"
    )

    # notes
    consciousness_measures_notes = models.TextField(null=True, blank=True)
    experiment_findings_notes = models.TextField(null=True, blank=True)

    history = HistoricalRecords()
    # objects = ExperimentManager()

    def clean(self):
        super().clean()
        # TODO: check what the cleaning needed

    def __str__(self):
        return f"study {self.study_id}, id {self.id}"
