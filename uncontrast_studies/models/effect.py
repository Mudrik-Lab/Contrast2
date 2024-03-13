from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords


class UnConEffectOutcome(models.Model):
    type = models.CharField(null=False, blank=False, max_length=250)

    def __str__(self):
        return self.type


class UnConEffect(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="findings"
    )
    outcome = models.ManyToManyField(null=False, blank=False, to=UnConEffectOutcome)
    significance = models.BooleanField(null=False, blank=False)

    reported_statistic = models.CharField(null=True, blank=True, max_length=250)
    p_value = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3)
    mean1 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Mean for 1st condition")
    mean2 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Mean for 2nd condition")
    sd1 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Standard deviation for 1st condition")
    sd2 = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Standard deviation for 2nd condition")
    sd_difference = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="SD of the difference between conditions")
    trials = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Number of trials per condition")

    # Attributes that might be relevant some day:
    # onset = models.IntegerField(null=True, blank=True, verbose_name="Onset timing in ms")
    # offset = models.IntegerField(null=True, blank=True, verbose_name="Offset timing in ms")
    # band_lower_bound = models.DecimalField(
    #     null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Band Lower bound in Hz"
    # )
    # band_higher_bound = models.DecimalField(
    #     null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Band Higher bound in Hz"
    # )
    # AAL_atlas_tag = models.CharField(null=True, blank=True, max_length=500, choices=AALAtlasTagChoices.choices)
    # analysis_type = models.CharField(
    #     null=True, blank=True, max_length=100, choices=AnalysisTypeChoices.choices, default=AnalysisTypeChoices.POWER
    # )
    # direction = models.CharField(
    #     null=True, blank=True, max_length=10, choices=DirectionChoices.choices, default=DirectionChoices.POSITIVE
    # )

    history = HistoricalRecords()

    def __str__(self):
        return f"experiment: {self.experiment_id}, outcome: {self.outcome}, significance: {self.significance}"
