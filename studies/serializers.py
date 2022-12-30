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
                  "key_words",
                  "references",
                  "funding",
                  "source_title",
                  "abbreviated_source_title",
                  "link",
                  "publisher",
                  "abstract",
                  "countries",
                  "affiliations"
                  ]


class ExcludedStudySerializer(StudySerializer):
    sub_research_area = serializers.CharField(source="approval_process__sub_research_area")
    research_area = serializers.CharField(source="approval_process__research_area")
    exclusion_reason = serializers.CharField(source="approval_process__exclusion_reason")
    class Meta:
        model = Study
        fields = StudySerializer.Meta.fields + ["exclusion_reason", "research_area", "sub_research_area"]
