from django.db import models
from django.db.models import CASCADE, PROTECT
from simple_history.models import HistoricalRecords

from contrast_api.choices import PresentationModeChoices


class UnConModalityType(models.Model):
    class Meta:
        verbose_name_plural = "stimulus modalities"

    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return self.name


class UnConStimulusCategory(models.Model):
    class Meta:
        verbose_name_plural = "stimulus categories"

    name = models.CharField(null=False, blank=False, max_length=50)

    def __str__(self):
        return self.name


class UnConStimulusSubCategory(models.Model):
    class Meta:
        verbose_name_plural = "stimulus sub categories"

    name = models.CharField(null=False, blank=False, max_length=50)
    parent = models.ForeignKey(null=True, blank=True, on_delete=CASCADE, to=UnConStimulusCategory)

    def __str__(self):
        return self.name


class UnConSuppressedStimulus(models.Model):

    class Meta:
        verbose_name_plural = "suppressed stimuli"

    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="suppressed stimuli"
    )

    category = models.ForeignKey(
        null=False, blank=False, on_delete=PROTECT, to=UnConStimulusCategory, related_name="suppressed stimuli"
    )
    sub_category = models.ForeignKey(
        null=True, blank=True, on_delete=PROTECT, to=UnConStimulusSubCategory, related_name="suppressed stimuli"
    )  # TODO validators from config
    modality = models.ForeignKey(
        null=False, blank=False, on_delete=PROTECT, to=UnConModalityType, related_name="suppressed stimuli"
    )  # TODO validators from config
    mode_of_presentation = models.CharField(null=False, blank=False, choices=PresentationModeChoices.choices, max_length=30)
    duration = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3)  # ms
    soa = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3)  # ms
    number_of_stimuli = models.PositiveSmallIntegerField(null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.sub_category is None:
            return f"experiment: {self.experiment_id}, category: {self.category}, modality: {self.modality}"
        return f"experiment: {self.experiment_id}, category: {self.category} ({self.sub_category}), modality: {self.modality}"


class UnConTargetStimulus(models.Model):

    class Meta:
        verbose_name_plural = "target stimuli"

    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="target stimuli"
    )

    category = models.ForeignKey(
        null=False, blank=False, on_delete=PROTECT, to=UnConStimulusCategory, related_name="target stimuli"
    )
    sub_category = models.ForeignKey(
        null=True, blank=True, on_delete=PROTECT, to=UnConStimulusSubCategory, related_name="target stimuli"
    )  # TODO validators from config
    modality = models.ForeignKey(
        null=False, blank=False, on_delete=PROTECT, to=UnConModalityType, related_name="target stimuli"
    )  # TODO validators from config
    duration = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3)  # ms
    number_of_stimuli = models.PositiveSmallIntegerField(null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.sub_category is None:
            return f"experiment: {self.experiment_id}, category: {self.category}, modality: {self.modality}"
        return f"experiment: {self.experiment_id}, category: {self.category} ({self.sub_category}), modality: {self.modality}"
