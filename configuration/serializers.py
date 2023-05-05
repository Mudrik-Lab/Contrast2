from typing import Optional

from rest_framework import serializers

from configuration.models import GraphImages
from studies.models import Theory, FindingTagType, Paradigm
from studies.models.stimulus import StimulusSubCategory


class TheoryConfigurationSerializer(serializers.ModelSerializer):
    parent = serializers.CharField(source="parent.name")

    class Meta:
        model = Theory
        fields = ('name', 'parent')


class FindingTagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTagType
        fields = ('name', 'family')


class StimulusSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StimulusSubCategory
        fields = ('name', 'parent')


class ParadigmSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Paradigm
        fields = ('name', 'parent')

    def get_parent(self, obj) -> Optional[str]:
        if obj.parent is None:
            return None
        return obj.parent.name


class StudiesConfigurationSerializer(serializers.Serializer):
    available_techniques = serializers.ListSerializer(child=serializers.CharField())
    available_finding_tags_types = FindingTagTypeSerializer(many=True)
    available_finding_tags_families = serializers.ListSerializer(child=serializers.CharField())
    available_measure_types = serializers.ListSerializer(child=serializers.CharField())
    available_theories = TheoryConfigurationSerializer(many=True)
    available_paradigms = ParadigmSerializer(many=True)
    available_paradigms_families = ParadigmSerializer(many=True)
    available_consciousness_measure_phase_type = serializers.ListSerializer(child=serializers.CharField())
    available_populations_types = serializers.ListSerializer(child=serializers.CharField())
    available_theory_driven_types = serializers.ListSerializer(child=serializers.CharField())
    available_experiment_types = serializers.ListSerializer(child=serializers.CharField())
    available_consciousness_measure_type = serializers.ListSerializer(child=serializers.CharField())
    available_tasks_types = serializers.ListSerializer(child=serializers.CharField())
    available_stimulus_modality_type = serializers.ListSerializer(child=serializers.CharField())
    available_stimulus_category_type = serializers.ListSerializer(child=serializers.CharField())
    available_stimulus_sub_category_type = StimulusSubCategorySerializer(many=True)
    available_authors = serializers.ListSerializer(child=serializers.CharField())


class GraphImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphImages
        fields = ("key", "image")


class GraphsConfigurationSerializer(serializers.Serializer):
    available_parent_theories = serializers.ListSerializer(child=serializers.CharField())
    available_finding_tags_types_for_timings = serializers.ListSerializer(child=serializers.CharField())
    available_techniques_for_timings = serializers.ListSerializer(child=serializers.CharField())
    available_techniques_for_frequencies = serializers.ListSerializer(child=serializers.CharField())
    images = GraphImagesSerializer(many=True)
