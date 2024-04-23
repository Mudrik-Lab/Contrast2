from django.db import models
from django.db.models import CASCADE, PROTECT
from simple_history.models import HistoricalRecords

from contrast_api.choices import ExperimentTypeChoices, SignificanceChoices
from uncontrast_studies.managers import UnConExperimentManager


class UnConExperiment(models.Model):
    """
    This is a major model here, lots of data "belongs" to the experiment in related models, so the experiment is codified there
    """

    class Meta:
        ordering = ["id"]

    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="uncon_experiments")
    type = models.PositiveIntegerField(
        null=False, blank=False, choices=ExperimentTypeChoices.choices, default=ExperimentTypeChoices.BEHAVIORAL
    )
    paradigm = models.ForeignKey(
        to="uncontrast_studies.UnConSpecificParadigm", on_delete=PROTECT, related_name="experiments"
    )  # TODO: possibly turn into many-to-many field

    # Stimuli metadata
    is_target_stimulus = models.BooleanField(
        null=False, blank=False, verbose_name="are there also non-suppressed stimuli", default=False
    )
    is_target_same_as_suppressed_stimulus = models.BooleanField(
        null=False,
        blank=False,
        verbose_name="is the non-suppressed stimulus the same as the suppressed stimulus",
        default=False,
    )

    # notes
    consciousness_measures_notes = models.TextField(null=True, blank=True)
    experiment_findings_notes = models.TextField(null=True, blank=True)
    significance = models.PositiveIntegerField(null=True, blank=True, choices=SignificanceChoices)
    history = HistoricalRecords()
    objects = UnConExperimentManager()

    def clean(self):
        super().clean()
        # TODO: check what the cleaning needed

    def calculate_significance(self):
        findings_significance = self.findings.all().values_list("is_significant", flat=True)
        if all(x is True for x in findings_significance):
            self.significance = SignificanceChoices.POSITIVE
        elif all(x is False for x in findings_significance):
            self.significance = SignificanceChoices.POSITIVE
        else:
            self.significance = SignificanceChoices.MIXED
        self.save()

    def __str__(self):
        return f"study {self.study_id}, id {self.id}"
