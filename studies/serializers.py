from rest_framework import serializers

from approval_process.models import ApprovalProcess
from studies.models import Experiment, Study, Theory, Interpretation, Technique, Author, Paradigm, ConsciousnessMeasure, \
    Measure, FindingTag, Sample, Stimulus, Task, TaskType, ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, \
    FindingTagType, FindingTagFamily
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, ModalityType


class TheorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Theory
        depth = 2
        fields = ('id', 'name', 'parent')


class MeasureSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Measure
        fields = ("experiment", "id", "type", "notes")


class FindingTagSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field="name", queryset=FindingTagType.objects.all())
    family = serializers.SlugRelatedField(slug_field="name", queryset=FindingTagFamily.objects.all())
    technique = serializers.SlugRelatedField(slug_field="name", queryset=Technique.objects.all())

    class Meta:
        model = FindingTag
        fields = ("experiment",
                  "id",
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
        fields = ("experiment", "theory", "type")


class ConsciousnessMeasureSerializer(serializers.ModelSerializer):
    phase = serializers.SlugRelatedField(slug_field="name", queryset=ConsciousnessMeasurePhaseType.objects.all())
    type = serializers.SlugRelatedField(slug_field="name", queryset=ConsciousnessMeasureType.objects.all())

    class Meta:
        model = ConsciousnessMeasure
        fields = ("experiment", "id", "phase", "type", "description")


class ParadigmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paradigm
        depth = 2
        fields = ("id", "name", "parent")


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ("experiment", "id", "type", "total_size", "size_included")


class StimulusSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", queryset=StimulusCategory.objects.all())
    sub_category = serializers.SlugRelatedField(slug_field="name", queryset=StimulusSubCategory.objects.all())
    modality = serializers.SlugRelatedField(slug_field="name", queryset=ModalityType.objects.all())

    class Meta:
        model = Stimulus
        fields = ("experiment", "id", "category", "sub_category", "modality", "description", "duration")


class TaskSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field="name", queryset=TaskType.objects.all())

    class Meta:
        model = Task
        fields = ("experiment", "id", "description", "type")


class FullExperimentSerializer(serializers.ModelSerializer):
    interpretations = InterpretationSerializer(many=True, read_only=True)
    finding_tags = FindingTagSerializer(many=True, read_only=True)
    measures = MeasureSerializer(many=True, read_only=True)
    samples = SampleSerializer(many=True, read_only=True)
    stimuli = StimulusSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    consciousness_measures = ConsciousnessMeasureSerializer(many=True, read_only=True)
    techniques = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Technique.objects.all())
    paradigms = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Paradigm.objects.all())
    theory_driven_theories = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Theory.objects.all())

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


class ExperimentSerializer(FullExperimentSerializer):
    techniques = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Technique.objects.all())
    paradigms = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Paradigm.objects.all())
    theory_driven_theories = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Theory.objects.all())

    class Meta:
        model = Experiment
        fields = ("id",
                  "study",
                  "finding_description",
                  "techniques",
                  "paradigms",
                  "is_reporting",
                  "theory_driven",
                  "theory_driven_theories",
                  "type",

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


class StudyWithExperimentsSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, required=False)
    experiments = FullExperimentSerializer(many=True, required=False)

    class Meta:
        model = Study
        fields = ["id",
                  "authors",
                  "DOI",
                  "title",
                  "year",
                  "corresponding_author_email",
                  "approval_process",
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

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        if not hasattr(instance, "approval_process") or instance.approval_process is None:
            process = ApprovalProcess.objects.create()
            instance.approval_process = process
            instance.save()
        return instance


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


class DurationBarSerializer(serializers.Serializer):
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    name = serializers.CharField()


class DurationGraphSerializer(serializers.Serializer):
    series = DurationBarSerializer(many=True)


class NestedPieChartSerializer(serializers.Serializer):
    series_name = serializers.CharField()
    value = serializers.IntegerField()
    series = BarGraphSerializer(many=True)


class PieChartSerializer(serializers.Serializer):
    name = serializers.CharField()
    series = BarGraphSerializer(many=True)


class ComparisonNestedPieChartSerializer(serializers.Serializer):
    theories = PieChartSerializer(many=True)
