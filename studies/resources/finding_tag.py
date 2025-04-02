from import_export import resources
from import_export.fields import Field

from studies.models import FindingTag, Theory, Interpretation
from contrast_api.choices import InterpretationsChoices


class FindingTagResource(resources.ModelResource):
    id = Field(attribute="id")
    experiment_id = Field(attribute="experiment")
    family = Field(dehydrate_method="dehydrate_family")
    type = Field(dehydrate_method="dehydrate_type")
    technique = Field(dehydrate_method="dehydrate_technique")
    AAL_atlas_tags = Field(dehydrate_method="dehydrate_aal_atlas_tags")
    interpretations = Field(dehydrate_method="dehydrate_interpretations")

    class Meta:
        model = FindingTag
        fields = (
            "id",
            "experiment_id",
            "family",
            "type",
            "onset",
            "offset",
            "band_lower_bound",
            "band_higher_bound",
            "AAL_atlas_tags",
            "notes",
            "analysis_type",
            "direction",
            "technique",
            "is_NCC",
            "interpretations"
        )
        export_order = fields

    def dehydrate_family(self, finding_tag: FindingTag):
        return finding_tag.family.name if finding_tag.family else None

    def dehydrate_type(self, finding_tag: FindingTag):
        return finding_tag.type.name if finding_tag.type else None

    def dehydrate_technique(self, finding_tag: FindingTag):
        return finding_tag.technique.name if finding_tag.technique else None

    def dehydrate_aal_atlas_tags(self, finding_tag: FindingTag):
        return " | ".join([tag.name for tag in finding_tag.AAL_atlas_tags.all()]) if finding_tag.AAL_atlas_tags.exists() else None

    def dehydrate_interpretations(self, finding_tag: FindingTag):
        interpretations = [
            f"{i.theory.parent.name} - {i.type}" 
            for i in finding_tag.experiment.theories.all()
            if i.theory.parent
        ]
        return " | ".join(interpretations) if interpretations else None

