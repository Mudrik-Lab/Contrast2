from typing import Optional

from rest_framework import serializers

from configuration.models import GraphImage
from studies.models import Theory, FindingTagType, Paradigm, Technique, FindingTagFamily, MeasureType, \
    ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, TaskType, Author
from studies.models.stimulus import StimulusSubCategory, ModalityType, StimulusCategory


class TheoryConfigurationSerializer(serializers.ModelSerializer):
    parent = serializers.CharField(source="parent.name")
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Theory
        fields = ('name', 'parent', 'acronym', 'full_name', 'id', 'parent_id')

    def get_full_name(self, obj) -> str:
        if obj.acronym:
            return f"{obj.name} ({obj.acronym})"
        else:
            return f"{obj.name}"


class TechniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technique
        fields = ('name', 'id')


class FindingTagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTagType
        fields = ('name', 'family', 'id')


class FindingTagFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTagFamily
        fields = ('name', 'id')


class MeasureTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasureType
        fields = ('name', 'id')


class ConsciousnessMeasurePhaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsciousnessMeasurePhaseType
        fields = ('name', 'id')


class AnalysisMeasureTypeSerializer(serializers.ModelSerializer):
    # Formerly: ConsciousnessMeasureTypeSerializer
    class Meta:
        model = ConsciousnessMeasureType
        fields = ('name', 'id')


class StimulusSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StimulusSubCategory
        fields = ('name', 'parent', 'id')


class ConfigurationAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('name', 'id')


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ('name', 'id')


class ModalityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModalityType
        fields = ('name', 'id')


class StimulusCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StimulusCategory
        fields = ('name', 'id')


class ParadigmSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Paradigm
        fields = ('name', 'parent', 'id')

    def get_parent(self, obj) -> Optional[str]:
        if obj.parent is None:
            return None
        return obj.parent.name


class ExperimentTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()


class StudiesConfigurationSerializer(serializers.Serializer):
    available_techniques = TechniqueSerializer(many=True)
    available_finding_tags_types = FindingTagTypeSerializer(many=True)
    available_finding_tags_families = FindingTagFamilySerializer(many=True)
    available_measure_types = MeasureTypeSerializer(many=True)
    available_theories = TheoryConfigurationSerializer(many=True)
    available_paradigms = ParadigmSerializer(many=True)
    available_paradigms_families = ParadigmSerializer(many=True)
    available_consciousness_measure_phase_type = ConsciousnessMeasurePhaseTypeSerializer(many=True)
    available_populations_types = serializers.ListSerializer(child=serializers.CharField())
    available_theory_driven_types = serializers.ListSerializer(child=serializers.CharField())
    available_AAL_atlas_tag_types = serializers.ListSerializer(child=serializers.CharField())
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


class GraphImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphImage
        fields = ("key", "image")


class GraphsConfigurationSerializer(serializers.Serializer):
    available_parent_theories = serializers.ListSerializer(child=serializers.CharField())
    available_finding_tags_types_for_timings = serializers.ListSerializer(child=serializers.CharField())
    available_techniques_for_timings = serializers.ListSerializer(child=serializers.CharField())
    available_techniques_for_frequencies = serializers.ListSerializer(child=serializers.CharField())
    images = GraphImageSerializer(many=True)


class RegistrationConfigurationSerializer(serializers.Serializer):
    gender_options = serializers.ListSerializer(child=serializers.CharField())
    academic_stage_options = serializers.ListSerializer(child=serializers.CharField())
