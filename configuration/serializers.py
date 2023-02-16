from rest_framework import serializers

from configuration.models import GraphImages
from studies.models import Theory, FindingTagType, Paradigm


class TheorySerializer(serializers.ModelSerializer):
    parent = serializers.CharField(source="parent.name")

    class Meta:
        model = Theory
        fields = ('name', 'parent')


class FindingTagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTagType
        fields = ('name', 'family')


class ParadigmSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Paradigm
        fields = ('name', 'parent')

    def get_parent(self, obj):
        if obj.parent is None:
            return None
        return obj.parent.name


class StudiesConfigurationSerializer(serializers.Serializer):
    available_techniques = serializers.ListSerializer(child=serializers.CharField())
    available_finding_tags_types = FindingTagTypeSerializer(many=True)
    available_finding_tags_families = serializers.ListSerializer(child=serializers.CharField())
    available_measure_types = serializers.ListSerializer(child=serializers.CharField())
    available_theories = TheorySerializer(many=True)
    available_paradigms = ParadigmSerializer(many=True)
    available_consciousness_measure_phase_type = serializers.ListSerializer(child=serializers.CharField())
    available_consciousness_measure_type = serializers.ListSerializer(child=serializers.CharField())
    available_tasks_types = serializers.ListSerializer(child=serializers.CharField())
    available_authors = serializers.ListSerializer(child=serializers.CharField())


class GraphImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphImages
        fields = ("key", "image")


class GraphsConfigurationSerializer(serializers.Serializer):
    available_parent_theories = serializers.ListSerializer(child=serializers.CharField())
    available_finding_tags_types_for_timings = serializers.ListSerializer(child=serializers.CharField())
    images = GraphImagesSerializer(many=True)
