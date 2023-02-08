from django.db import models
from django.db.models import CASCADE


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
    parent = models.ForeignKey(null=True, blank=True, on_delete=CASCADE,
                               to=StimulusCategory)

    def __str__(self):
        return self.name


class Stimulus(models.Model):
    class Meta:
        verbose_name_plural = "stimuli"

    experiment = models.ForeignKey(null=False, blank=False, to="studies.Experiment",
                                   on_delete=CASCADE,
                                   related_name="stimuli")

    category = models.ForeignKey(null=False, blank=False, on_delete=CASCADE,
                                 to=StimulusCategory)
    sub_category = models.ForeignKey(null=True, blank=True, on_delete=CASCADE,
                                     to=StimulusSubCategory)  # TODO validators from config
    modality = models.ForeignKey(null=False, blank=False, on_delete=CASCADE,
                                 to=ModalityType)  # TODO validators from config
    description = models.TextField(null=True, blank=True)
    duration = models.PositiveBigIntegerField(null=True, blank=True)  # ms

    def __str__(self):
        return f"experiment: {self.experiment_id}  modality {self.modality}"
