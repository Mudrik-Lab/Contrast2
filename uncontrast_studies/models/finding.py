from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords


class UnConFinding(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="findings"
    )
    outcome = models.CharField(null=False, blank=False, max_length=250)
    is_significant = models.BooleanField(null=False, blank=False, verbose_name="is effect significant")

    # reported_statistic = models.CharField(null=True, blank=True, max_length=250)
    # p_value = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3)
    # mean1 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Mean for 1st condition")
    # mean2 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Mean for 2nd condition")
    # sd1 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Standard deviation for 1st condition")
    # sd2 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Standard deviation for 2nd condition")
    # sd_difference = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="SD of the difference between conditions")
    # trials = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Number of trials per condition")

    history = HistoricalRecords()

    def __str__(self):
        return f"experiment: {self.experiment_id}, outcome: {self.outcome}, significance: {self.is_significant}"
