from django.db import models
from django.db.models import CASCADE
from django.core.exceptions import ValidationError


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
    allowed_categories_by_modality = {
        "Auditory": ["Animals", "Bodies", "Contours", "Digits", "Drawings", "Electric Stimulation", "Letters", "Motion",
                     "Music", "Noise", "Numbers", "Objects", "Patterns", "Real Objects", "Sounds", "Speech", "Videos",
                     "Words"],
        "None": ["None"],
        "Olfactory": ["Animals", "Objects"],
        "Tactile": ["Animals", "Bodies", "Checkerboard", "Electric Stimulation", "Faces", "Geometric Shapes", "Letters",
                    "Motion", "Objects", "Pacman", "Patterns", "Real Objects", "Symbols", "Textures"],
        "Visual": ["Animals", "Artificial Scenes", "Bodies", "Checkerboard", "Color", "Contours"    "Digits",
                   "Drawings", "Faces",
                   "Figure-Ground", "Geometric Shapes", "Gratings/Kanizsa", "Letters", "Light Flashes", "Motion",
                   "Natural Scenes",
                   "Numbers", "Objects", "Pacman", "Patterns", "Real Objects", "Sexual Images", "Symbols", "Videos",
                   "Virtual Reality Objects", "Words"]
    }

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
    duration = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=3)  # ms

    def __str__(self):
        return f"experiment: {self.experiment_id}  modality {self.modality}"

    def clean(self):
        # validating category by modality
        if self.category not in self.allowed_categories_by_modality[self.modality]:
            # raise ValidationError({"category": f"Stimulus category {self.category} isn't allowed for Stimulus modality "
            #                                    f"{self.modality}"})
            pass
