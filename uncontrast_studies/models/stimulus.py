from django.db import models
from django.db.models import CASCADE, PROTECT
from simple_history.models import HistoricalRecords


class ModalityType(models.Model):
    class Meta:
        verbose_name_plural = "stimulus modalities"

    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return self.name


class StimulusCategory(models.Model):
    class Meta:
        verbose_name_plural = "stimulus categories"

    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return self.name


class StimulusSubCategory(models.Model):
    class Meta:
        verbose_name_plural = "stimulus sub categories"

    name = models.CharField(null=False, blank=False, max_length=50)
    parent = models.ForeignKey(null=True, blank=True, on_delete=CASCADE, to=StimulusCategory)

    def __str__(self):
        return self.name


class UnConStimulus(models.Model):
    # TODO: understand if this is one model for suppressed and unsuppressed?
    #  is it used as the same "graph breakdown"?
    # To add novel primes, soa, duration, (size? might be another sub model) or just height/width

    class Meta:
        verbose_name_plural = "stimuli"

    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="stimuli"
    )

    category = models.ForeignKey(
        null=False, blank=False, on_delete=PROTECT, to=StimulusCategory, related_name="stimuli"
    )
    sub_category = models.ForeignKey(
        null=True, blank=True, on_delete=PROTECT, to=StimulusSubCategory, related_name="stimuli"
    )  # TODO validators from config
    modality = models.ForeignKey(
        null=False, blank=False, on_delete=PROTECT, to=ModalityType, related_name="stimuli"
    )  # TODO validators from config
    duration = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3)  # ms
    history = HistoricalRecords()

    def __str__(self):
        if self.sub_category is None:
            return f"experiment: {self.experiment_id}, category: {self.category}, modality: {self.modality}"
        return f"experiment: {self.experiment_id}, category: {self.category} ({self.sub_category}), modality: {self.modality}"

