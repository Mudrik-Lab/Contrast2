from rest_framework import serializers

from studies.models import Experiment, Study, Theory, Interpretation, Technique, Author, Paradigm, ConsciousnessMeasure, \
    Measure, FindingTag, Sample, Stimulus, Task


class TheorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Theory
        depth = 2
        fields = ('id', 'name', 'parent')


class MeasureSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Measure
        fields = ("id", "type", "notes")


class FindingTagSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field="name", read_only=True)
    family = serializers.SlugRelatedField(slug_field="name", read_only=True)
    technique = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = FindingTag
        fields = ("id",
                  "family",
                  "type",
                  "onset",
                  "offset",
                  "band_lower_bound",
                  "band_higher_bound",
                  "AAL_atlas_tag",
                  "notes",
                  "analysis_type",
                  "technique")


class InterpretationSerializer(serializers.ModelSerializer):
    theory = TheorySerializer()

    class Meta:
        model = Interpretation
        fields = ("theory", "type")


class ConsciousnessMeasureSerializer(serializers.ModelSerializer):
    phase = serializers.SlugRelatedField(slug_field="name", read_only=True)
    type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = ConsciousnessMeasure
        fields = ("id", "phase", "type", "description")


class ParadigmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paradigm
        depth = 2
        fields = ("id", "name", "parent")


class SampleSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Sample
        fields = ("id", "type", "total_size", "size_included")


class StimulusSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    sub_category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    modality = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Stimulus
        fields = ("id", "category", "sub_category", "modality", "description", "duration")


class TaskSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Task
        fields = ("id", "description", "type")


class ExperimentSerializer(serializers.ModelSerializer):
    interpretations = InterpretationSerializer(many=True)
    finding_tags = FindingTagSerializer(many=True)
    measures = MeasureSerializer(many=True)
    samples = SampleSerializer(many=True)
    stimuli = StimulusSerializer(many=True)
    tasks = TaskSerializer(many=True)
    consciousness_measures = ConsciousnessMeasureSerializer(many=True)
    techniques = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    paradigms = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)
    theory_driven_theories = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)

    class Meta:
        model = Experiment
        depth = 2
        fields = ("id",
                  "study",
                  "interpretations",
                  "finding_description",
                  "techniques",
                  "paradigms",
                  "type_of_consciousness",
                  "is_reporting",
                  "theory_driven",
                  "theory_driven_theories",
                  "type",
                  "finding_tags",
                  "measures",
                  "consciousness_measures",
                  "samples",
                  "stimuli",
                  "tasks"
                  )


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class StudySerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)

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
                  "affiliations",
                  "submitter"
                  ]


class StudyWithExperimentsSerializer(serializers.Serializer):
    authors = AuthorSerializer(many=True)
    experiments = ExperimentSerializer(many=True)

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
                  "affiliations",
                  "submitter",
                  "experiments"
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
