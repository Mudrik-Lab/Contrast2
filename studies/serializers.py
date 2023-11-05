from django_countries import countries
from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import serializers

from approval_process.models import ApprovalProcess
from studies.models import (
    Experiment,
    Study,
    Theory,
    Interpretation,
    Technique,
    Author,
    Paradigm,
    ConsciousnessMeasure,
    Measure,
    FindingTag,
    Sample,
    Stimulus,
    Task,
    TaskType,
    ConsciousnessMeasurePhaseType,
    ConsciousnessMeasureType,
    FindingTagType,
    FindingTagFamily,
    MeasureType,
)
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, ModalityType


class TheorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Theory
        depth = 2
        fields = ("id", "name", "parent")


class MeasureSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=MeasureType.objects.all())

    class Meta:
        model = Measure
        fields = ("experiment", "id", "type", "notes")


class FindingTagSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=FindingTagType.objects.all())
    family = serializers.PrimaryKeyRelatedField(queryset=FindingTagFamily.objects.all())
    technique = serializers.PrimaryKeyRelatedField(queryset=Technique.objects.all())

    class Meta:
        model = FindingTag
        fields = (
            "experiment",
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
            "is_NCC",
            "technique",
            "direction",
        )


class InterpretationSerializer(serializers.ModelSerializer):
    theory = TheorySerializer()

    class Meta:
        model = Interpretation
        fields = ("experiment", "theory", "type", "id")


class InterpretationCreateSerializer(serializers.ModelSerializer):
    theory = serializers.PrimaryKeyRelatedField(queryset=Theory.objects.all())

    class Meta:
        model = Interpretation
        fields = ("experiment", "theory", "type", "id")


class ConsciousnessMeasureSerializer(serializers.ModelSerializer):
    phase = serializers.PrimaryKeyRelatedField(queryset=ConsciousnessMeasurePhaseType.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=ConsciousnessMeasureType.objects.all())

    class Meta:
        model = ConsciousnessMeasure
        fields = ("experiment", "id", "phase", "type")


class ParadigmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paradigm
        depth = 2
        fields = ("id", "name", "parent", "sub_type")


class ParadigmAddRemoveSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ("experiment", "id", "type", "total_size", "size_included")


class StimulusSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=StimulusCategory.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(queryset=StimulusSubCategory.objects.all(), required=False)
    modality = serializers.PrimaryKeyRelatedField(queryset=ModalityType.objects.all())

    class Meta:
        model = Stimulus
        fields = ("experiment", "id", "category", "sub_category", "modality", "duration")


class TaskSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=TaskType.objects.all())

    class Meta:
        model = Task
        fields = ("experiment", "id", "type")


class TechniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technique
        fields = ("id", "name")


class TechniqueAddRemoveSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class FullExperimentSerializer(serializers.ModelSerializer):
    study = serializers.PrimaryKeyRelatedField(queryset=Study.objects.all())
    interpretations = serializers.SerializerMethodField()
    finding_tags = FindingTagSerializer(many=True, read_only=True)
    measures = MeasureSerializer(many=True, read_only=True)
    samples = SampleSerializer(many=True, read_only=True)
    stimuli = StimulusSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    consciousness_measures = ConsciousnessMeasureSerializer(many=True, read_only=True)
    techniques = TechniqueSerializer(many=True, read_only=True)
    paradigms = ParadigmSerializer(many=True, read_only=True)
    theory_driven_theories = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Theory.objects.all())

    class Meta:
        model = Experiment
        depth = 2
        fields = (
            "id",
            "study",
            "interpretations",
            "results_summary",
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
            "tasks",
            "tasks_notes",
            "stimuli_notes",
            "consciousness_measures_notes",
            "paradigms_notes",
            "sample_notes",
        )

    @extend_schema_field(InterpretationSerializer(many=True))
    def get_interpretations(self, obj: Experiment):
        interpretations = Interpretation.objects.filter(experiment=obj)
        return InterpretationSerializer(many=True, instance=interpretations).data


class ExperimentSerializer(FullExperimentSerializer):
    techniques = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Technique.objects.all())
    paradigms = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Paradigm.objects.all())
    theory_driven_theories = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Theory.objects.all())

    class Meta:
        model = Experiment
        fields = (
            "id",
            "study",
            "results_summary",
            "techniques",
            "paradigms",
            "is_reporting",
            "theory_driven",
            "theory_driven_theories",
            "type",
            "tasks_notes",
            "stimuli_notes",
            "consciousness_measures_notes",
            "paradigms_notes",
            "sample_notes",
        )


class ThinExperimentSerializer(ExperimentSerializer):
    theory_driven_theories = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Theory.objects.all())

    class Meta:
        model = Experiment
        fields = (
            "id",
            "study",
            "results_summary",
            "type_of_consciousness",
            "is_reporting",
            "theory_driven",
            "type",
            "theory_driven_theories",
        )


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class StudySerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)

    class Meta:
        model = Study
        fields = [
            "authors",
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
        ]


class StudyWithExperimentsSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, required=False)
    experiments = FullExperimentSerializer(many=True, required=False)
    authors_key_words = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = Study
        fields = [
            "id",
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
            "experiments",
        ]


class StudyWithExperimentsCreateSerializer(StudyWithExperimentsSerializer):
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        if not hasattr(instance, "approval_process") or instance.approval_process is None:
            process = ApprovalProcess.objects.create()
            instance.approval_process = process
            instance.save()
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        authors = Author.objects.filter(id__in=validated_data.get("authors", []))
        for author in authors:
            instance.authors.add(author)

        return instance


class ThinStudyWithExperimentsSerializer(StudyWithExperimentsSerializer):
    experiments = ThinExperimentSerializer(many=True, required=False)


class ExcludedStudySerializer(StudySerializer):
    sub_research_area = serializers.CharField(source="approval_process.sub_research_area")
    research_area = serializers.CharField(source="approval_process.research_area")
    exclusion_reason = serializers.CharField(source="approval_process.exclusion_reason")

    class Meta:
        model = Study
        fields = StudySerializer.Meta.fields + ["exclusion_reason", "research_area", "sub_research_area"]


class NoteUpdateSerializer(serializers.Serializer):
    note = serializers.CharField()


class OptionalNoteUpdateSerializer(serializers.Serializer):
    note = serializers.CharField(trim_whitespace=True, allow_blank=True, allow_null=True)


class NationOfConsciousnessGraphSerializer(serializers.Serializer):
    country = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    value = serializers.IntegerField()
    total = serializers.IntegerField()
    theory = serializers.CharField(source="theory__parent__name")

    def get_country(self, obj) -> str:
        return countries.alpha3(obj["country"])

    def get_country_name(self, obj) -> str:
        return countries.name(obj["country"])


class YearlySeriesSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    value = serializers.IntegerField()


class TrendsOverYearsGraphSerializer(serializers.Serializer):
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
    series_name = serializers.CharField()
    value = serializers.IntegerField()
    series = BarGraphSerializer(many=True)


class ComparisonNestedPieChartSerializer(serializers.Serializer):
    theories = PieChartSerializer(many=True)
