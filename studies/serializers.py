from rest_framework import serializers

from studies.models import Experiment, Study


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        depth = 2
        fields = "__all__"


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ["authors",
                  "DOI",
                  "title",
                  "year",
                  "corresponding_author_email",
                  "approval_status",
                  "authors_key_words",
                  "funding",
                  "source_title",
                  "abbreviated_source_title",
                  "countries",
                  "affiliations"
                  ]


class ExcludedStudySerializer(StudySerializer):
    sub_research_area = serializers.CharField(source="approval_process.sub_research_area")
    research_area = serializers.CharField(source="approval_process.research_area")
    exclusion_reason = serializers.CharField(source="approval_process.exclusion_reason")

    class Meta:
        model = Study
        fields = StudySerializer.Meta.fields + ["exclusion_reason", "research_area", "sub_research_area"]


class NationOfConsciousnessGraphSerializer(serializers.Serializer):
    country = serializers.CharField()
    count = serializers.IntegerField()
    theory = serializers.CharField(source="theory__parent__name")


class YearlySeriesSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    value = serializers.IntegerField()


class AcrossTheYearsGraphSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    series = YearlySeriesSerializer(many=True)


class BarGraphSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    key = serializers.CharField()


class StackedBarGraphSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    series = BarGraphSerializer(many=True)
