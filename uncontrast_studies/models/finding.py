from django.db import models
from django.db.models import CASCADE, PROTECT
from simple_history.models import HistoricalRecords


class UnConOutcome(models.Model):
    name = models.CharField(null=False, blank=False, max_length=30)


class UnConFinding(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="findings"
    )
    outcome = models.ForeignKey(null=False, blank=False, to=UnConOutcome, on_delete=PROTECT, related_name="findings")
    is_significant = models.BooleanField(null=False, blank=False, verbose_name="was the effect significant")
    is_important = models.BooleanField(null=False, blank=False, default=True, verbose_name="was the finding important")
    number_of_trials = models.PositiveSmallIntegerField(
        null=False, blank=False, default=1, verbose_name="number of trials for the task"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"experiment: {self.experiment_id}, outcome: {self.outcome.name}, significance: {self.is_significant}"
