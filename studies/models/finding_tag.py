from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE
from simple_history.models import HistoricalRecords

from contrast_api.choices import AnalysisTypeChoices, DirectionChoices, AALAtlasTagChoices


class FindingTagFamily(models.Model):
    class Meta:
        verbose_name_plural = "findings tags families"

    name = models.CharField(null=False, blank=False, max_length=250)

    def __str__(self):
        return self.name


class FindingTagType(models.Model):
    name = models.CharField(null=False, blank=False, max_length=250)
    family = models.ForeignKey(null=True, blank=True, on_delete=CASCADE, to=FindingTagFamily)

    def __str__(self):
        return self.name


class FindingTag(models.Model):
    """
    This is a polymorphic model. e.g different types of "finding tags" have different implementations
     We've decided to implement by "nullable" fields. and keep for via validator

    """

    available_properties_by_family = {
        "Temporal": ["onset", "offset"],
        "Frequency": ["onset", "offset", "direction", "band_lower_bound", "band_higher_bound", "analysis_type"],
        "Spatial Areas": ["AAL_atlas_tag"],
    }
    # properties changing by type, if you add one, you need to add it here also
    variable_properties = [
        "onset",
        "offset",
        "band_lower_bound",
        "band_higher_bound",
        "AAL_atlas_tag",
        "analysis_type",
        "direction",
    ]

    # TODO validator + custom admin form
    experiment = models.ForeignKey(
        null=False, blank=False, to="studies.Experiment", on_delete=CASCADE, related_name="finding_tags"
    )
    family = models.ForeignKey(null=False, blank=False, on_delete=CASCADE, to=FindingTagFamily)
    type = models.ForeignKey(null=False, blank=False, on_delete=CASCADE, to=FindingTagType)
    onset = models.IntegerField(null=True, blank=True, verbose_name="Onset timing in ms")
    offset = models.IntegerField(null=True, blank=True, verbose_name="Offset timing in ms")
    band_lower_bound = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Band Lower bound in Hz"
    )
    band_higher_bound = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=3, verbose_name="Band Higher bound in Hz"
    )
    AAL_atlas_tag = models.CharField(null=True, blank=True, max_length=500, choices=AALAtlasTagChoices.choices)
    notes = models.TextField(null=True, blank=True)
    analysis_type = models.CharField(
        null=True, blank=True, max_length=100, choices=AnalysisTypeChoices.choices, default=AnalysisTypeChoices.POWER
    )
    direction = models.CharField(
        null=True, blank=True, max_length=10, choices=DirectionChoices.choices, default=DirectionChoices.POSITIVE
    )
    technique = models.ForeignKey(
        null=True, blank=True, to="studies.Technique", related_name="findings_tags", on_delete=CASCADE
    )
    is_NCC = models.BooleanField(null=False, blank=False, default=True)  # later remove the default
    history = HistoricalRecords()

    def clean(self):
        if self.type.family != self.family:
            raise ValidationError({"type": f"Finding type {self.type} has different family then {self.family}"})
        # validating properties by family
        if self.family in self.available_properties_by_family.keys():
            available_props_for_type = self.available_properties_by_family[self.family]

            for possible_property in self.variable_properties:
                # First we check if the property is assigned
                if getattr(self, possible_property) is not None:
                    # check if it exists and it shouldn't
                    if possible_property not in available_props_for_type:
                        # if it wasn't expected raise
                        raise ValidationError(
                            {
                                possible_property: f"finding type for type {self.type} of family {self.family} was assigned  {possible_property} and doesn't support it"
                            }
                        )
                else:  # if it's not assigned
                    if possible_property in available_props_for_type:  # check if it's expected
                        raise ValidationError(
                            {
                                possible_property: f"finding type for type {self.type} of family {self.family} was not assigned {possible_property} and expects it"
                            }
                        )

    def __str__(self):
        return f"experiment: {self.experiment_id} family {self.family}, type {self.type}"
