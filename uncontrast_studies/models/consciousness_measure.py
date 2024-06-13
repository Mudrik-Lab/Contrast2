from django.db import models
from django.db.models import CASCADE, PROTECT
from simple_history.models import HistoricalRecords


class UnConsciousnessMeasurePhase(models.Model):
    name = models.CharField(blank=False, null=False, max_length=50)

    def __str__(self):
        return self.name


class UnConsciousnessMeasureType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=50)

    def __str__(self):
        return self.name


class UnConsciousnessMeasureSubType(models.Model):
    name = models.CharField(blank=False, null=False, max_length=50)
    type = models.ForeignKey(
        blank=False,
        null=False,
        on_delete=PROTECT,
        to=UnConsciousnessMeasureType,
        related_name="unconsciousness_measure_sub_types",
    )

    def __str__(self):
        return self.name


class UnConsciousnessMeasure(models.Model):
    experiment = models.ForeignKey(
        to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="unconsciousness_measures"
    )
    phase = models.ForeignKey(
        blank=False,
        null=False,
        on_delete=PROTECT,
        to=UnConsciousnessMeasurePhase,
        related_name="unconsciousness_measures",
    )
    type = models.ForeignKey(
        blank=False,
        null=False,
        on_delete=PROTECT,
        to=UnConsciousnessMeasureType,
        related_name="unconsciousness_measures",
    )
    sub_type = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=PROTECT,
        to=UnConsciousnessMeasureSubType,
        related_name="unconsciousness_measures",
    )
    # Consciousness Measure metadata
    number_of_trials = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="consciousness measure # of trials for the objective measure"
    )
    number_of_participants_in_awareness_test = models.PositiveSmallIntegerField(null=True, blank=True)
    is_cm_same_participants_as_task = models.BooleanField(
        null=False,
        blank=False,
        verbose_name="was consciousness measure taken from the same participants as the main task",
    )
    is_performance_above_chance = models.BooleanField(null=True, blank=True)
    is_trial_excluded_based_on_measure = models.BooleanField(
        null=False, blank=False, verbose_name="were trials excluded from the analysis based on the measure"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"experiment: {self.experiment_id} phase {self.phase}, type {self.type} ({self.sub_type})"
