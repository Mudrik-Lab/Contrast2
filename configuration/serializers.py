from typing import Optional

from rest_framework import serializers

from configuration.models import GraphImage
from studies.models import (
    Theory,
    FindingTagType,
    Paradigm,
    Technique,
    FindingTagFamily,
    MeasureType,
    ConsciousnessMeasurePhaseType,
    ConsciousnessMeasureType,
    TaskType,
    Author,
)
from studies.models.finding_tag import AALAtlasTag
from studies.models.stimulus import StimulusSubCategory, ModalityType, StimulusCategory
from uncontrast_studies.models import (
    UnConsciousnessMeasureSubType,
    UnConStimulusSubCategory,
    UnConSuppressionMethodSubType,
    UnConSpecificParadigm,
)


class TheoryConfigurationSerializer(serializers.ModelSerializer):
    parent = serializers.CharField(source="parent.name")
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Theory
        fields = ("name", "parent", "acronym", "full_name", "id", "parent_id")

    def get_full_name(self, obj) -> str:
        if obj.acronym:
            return f"{obj.name} ({obj.acronym})"
        else:
            return f"{obj.name}"


class TechniqueConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technique
        fields = ("name", "id")


class FindingTagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTagType
        fields = ("name", "family", "id")


class FindingTagFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTagFamily
        fields = ("name", "id")


class AALAtlasTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AALAtlasTag
        fields = ("name", "id")


class MeasureTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasureType
        fields = ("name", "id")


class ConsciousnessMeasurePhaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsciousnessMeasurePhaseType
        fields = ("name", "id")


class AnalysisMeasureTypeSerializer(serializers.ModelSerializer):
    # Formerly: ConsciousnessMeasureTypeSerializer
    class Meta:
        model = ConsciousnessMeasureType
        fields = ("name", "id")


class StimulusSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StimulusSubCategory
        fields = ("name", "parent", "id")


class ConfigurationAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("name", "id")


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ("name", "id")


class ModalityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModalityType
        fields = ("name", "id")


class StimulusCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StimulusCategory
        fields = ("name", "id")


class ParadigmSubTypeConfigurationSerializer(serializers.ModelSerializer):
    parent = serializers.CharField(source="name")
    name = serializers.CharField(source="sub_type")

    class Meta:
        model = Paradigm
        fields = ("name", "parent", "id")


class ParadigmConfigurationSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Paradigm
        fields = ("name", "parent", "id", "sub_type")

    def get_parent(self, obj) -> Optional[str]:
        if obj.parent is None:
            return None
        return obj.parent.name


class UnConSpecificParadigmSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConSpecificParadigm
        fields = ("name", "main", "id")


class ExperimentTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()


class GenericTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        fields = ("name", "id")


class UnConsciousnessMeasureSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConsciousnessMeasureSubType
        fields = ("name", "type", "id")


class UnConSuppressionMethodSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConSuppressionMethodSubType
        fields = ("name", "parent", "id")


class UnConStimulusSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConStimulusSubCategory
        fields = ("name", "id", "parent")


class UnConStudiesConfigurationSerializer(serializers.Serializer):
    available_authors = ConfigurationAuthorSerializer(many=True)
    existing_journals = serializers.ListSerializer(child=serializers.CharField())
    approved_experiments_count = serializers.IntegerField()
    available_populations_types = serializers.ListSerializer(child=serializers.CharField())
    available_mode_of_presentation = serializers.ListSerializer(child=serializers.CharField())
    available_outcomes_type = GenericTypeSerializer(many=True)
    available_consciousness_measure_phase_type = GenericTypeSerializer(many=True)
    available_consciousness_measure_type = GenericTypeSerializer(many=True)
    available_consciousness_measure_sub_type = UnConsciousnessMeasureSubTypeSerializer(many=True)
    available_tasks_types = GenericTypeSerializer(many=True)
    available_suppression_method_types = GenericTypeSerializer(many=True)
    available_suppression_method_sub_types = UnConSuppressionMethodSubTypeSerializer(many=True)
    available_processing_main_domain_types = GenericTypeSerializer(many=True)
    available_main_paradigm_type = GenericTypeSerializer(many=True)
    available_specific_paradigm_type = UnConSpecificParadigmSerializer(many=True)
    available_experiment_types = ExperimentTypeSerializer(many=True)
    available_stimulus_modality_type = GenericTypeSerializer(many=True)
    available_stimulus_category_type = GenericTypeSerializer(many=True)
    available_stimulus_sub_category_type = UnConStimulusSubCategorySerializer(many=True)
    are_participants_excluded_options = serializers.ListSerializer(child=serializers.BooleanField())
    is_trial_excluded_based_on_measure_options = serializers.ListSerializer(child=serializers.BooleanField())


class StudiesConfigurationSerializer(serializers.Serializer):
    available_techniques = TechniqueConfigurationSerializer(many=True)
    available_finding_tags_types = FindingTagTypeSerializer(many=True)
    available_finding_tags_families = FindingTagFamilySerializer(many=True)
    available_measure_types = MeasureTypeSerializer(many=True)
    available_theories = TheoryConfigurationSerializer(many=True)
    available_paradigms = ParadigmConfigurationSerializer(many=True)
    available_paradigms_families = ParadigmConfigurationSerializer(many=True)
    available_paradigms_sub_types = ParadigmSubTypeConfigurationSerializer(many=True)
    available_consciousness_measure_phase_type = ConsciousnessMeasurePhaseTypeSerializer(many=True)
    available_populations_types = serializers.ListSerializer(child=serializers.CharField())
    available_theory_driven_types = serializers.ListSerializer(child=serializers.CharField())
    available_AAL_atlas_tag_types = serializers.ListSerializer(child=serializers.CharField())
    available_AAL_atlas_tags_types = AALAtlasTagSerializer(many=True)
    available_analysis_type_choices = serializers.ListSerializer(child=serializers.CharField())
    available_direction_choices = serializers.ListSerializer(child=serializers.CharField())
    available_experiment_types = ExperimentTypeSerializer(many=True)
    available_consciousness_measure_type = AnalysisMeasureTypeSerializer(many=True)
    available_analysis_measure_type = AnalysisMeasureTypeSerializer(many=True)
    available_tasks_types = TaskTypeSerializer(many=True)
    available_stimulus_modality_type = ModalityTypeSerializer(many=True)
    available_stimulus_category_type = StimulusCategorySerializer(many=True)
    available_stimulus_sub_category_type = StimulusSubCategorySerializer(many=True)
    available_authors = ConfigurationAuthorSerializer(many=True)
    existing_journals = serializers.ListSerializer(child=serializers.CharField())
    approved_studies_count = serializers.IntegerField(default=0)
    approved_experiments_count = serializers.IntegerField()


class GraphImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphImage
        fields = ("key", "image")


class GraphsConfigurationSerializer(serializers.Serializer):
    available_parent_theories = serializers.ListSerializer(child=serializers.CharField())
    available_parent_theories_including_all = serializers.ListSerializer(child=serializers.CharField())
    available_finding_tags_types_for_timings = serializers.ListSerializer(child=serializers.CharField())
    available_techniques_for_timings = serializers.ListSerializer(child=serializers.CharField())
    available_techniques_for_frequencies = serializers.ListSerializer(child=serializers.CharField())
    images = GraphImageSerializer(many=True)


class RegistrationConfigurationSerializer(serializers.Serializer):
    gender_options = serializers.ListSerializer(child=serializers.CharField())
    academic_stage_options = serializers.ListSerializer(child=serializers.CharField())
