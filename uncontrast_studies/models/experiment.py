from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords

from contrast_api.choices import ExperimentTypeChoices


class UnConExperiment(models.Model):
    """
    This is a major model here, lots of data "belongs" to the experiment in related models, so the experiment is codified there
    """

    class Meta:
        ordering = ["id"]

    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="uncon_experiments")
    techniques = models.ManyToManyField(to="uncontrast_studies.UnConTechnique", related_name="uncon_experiments")  # validator at least one
    processing_domains = models.ManyToManyField(to="uncontrast_studies.UnConProcessingDomain", related_name="uncon_experiments")  # validator at least one
    type_of_evidence = models.ManyToManyField(null=False, blank=False, to="uncontrast_studies.UnConEvidenceType", related_name="uncon_experiments")
    type_of_attention = models.ManyToManyField(null=True, blank=True, to="uncontrast_studies.UnConAttentionType", related_name="uncon_experiments")
    type = models.PositiveIntegerField(
        null=False, blank=False, choices=ExperimentTypeChoices.choices, default=ExperimentTypeChoices.NEUROSCIENTIFIC
    )
    consciousness_measures_notes = models.TextField(null=True, blank=True)
    experiment_findings_notes = models.TextField(null=True, blank=True)

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
