from django_countries import countries
from rest_framework import serializers

from approval_process.models import ApprovalProcess
from contrast_api.choices import SignificanceChoices
from studies.models import Study, Author, ConsciousnessMeasureType, TaskType
from studies.serializers import AuthorSerializer
from uncontrast_studies.models import (
    UnConExperiment,
    UnConSpecificParadigm,
    UnConTask,
    UnConsciousnessMeasure,
    UnConProcessingDomain,
    UnConTargetStimulus,
    UnConSuppressedStimulus,
    UnConFinding,
    UnConSample,
    UnConSuppressionMethod,
    UnConStimulusCategory,
    UnConStimulusSubCategory,
    UnConModalityType,
    UnConsciousnessMeasurePhase,
    UnConsciousnessMeasureType,
    UnConTaskType,
    UnConMainParadigm,
    UnConsciousnessMeasureSubType,
    UnConSuppressionMethodSubType,
    UnConSuppressionMethodType,
)


class UnConSpecificParadigmSerializer(serializers.ModelSerializer):
    main = serializers.PrimaryKeyRelatedField(queryset=UnConMainParadigm.objects.all())

    class Meta:
        model = UnConSpecificParadigm
        fields = ("id", "main", "name")


class UnConTaskSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=UnConTaskType.objects.all())

    class Meta:
        model = UnConTask
        fields = ("experiment", "id", "type")


class UnConsciousnessMeasureSerializer(serializers.ModelSerializer):
    phase = serializers.PrimaryKeyRelatedField(queryset=UnConsciousnessMeasurePhase.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=UnConsciousnessMeasureType.objects.all())
    sub_type = serializers.PrimaryKeyRelatedField(queryset=UnConsciousnessMeasureSubType.objects.all())

    class Meta:
        model = UnConsciousnessMeasure
        fields = (
            "experiment",
            "id",
            "phase",
            "type",
            "sub_type",
            "number_of_trials",
            "number_of_participants_in_awareness_test",
            "is_cm_same_participants_as_task",
            "is_performance_above_chance",
            "is_trial_excluded_based_on_measure",
        )


class UnConTargetStimulusSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=UnConStimulusCategory.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(queryset=UnConStimulusSubCategory.objects.all(), required=False)
    modality = serializers.PrimaryKeyRelatedField(queryset=UnConModalityType.objects.all())

    class Meta:
        model = UnConTargetStimulus
        fields = ("experiment", "id", "category", "sub_category", "modality", "number_of_stimuli")


class UnConSuppressedStimulusSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=UnConStimulusCategory.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(queryset=UnConStimulusSubCategory.objects.all(), required=False)
    modality = serializers.PrimaryKeyRelatedField(queryset=UnConModalityType.objects.all())

    class Meta:
        model = UnConSuppressedStimulus
        fields = (
            "experiment",
            "id",
            "category",
            "sub_category",
            "modality",
            "duration",
            "mode_of_presentation",
            "duration",
            "soa",
            "number_of_stimuli",
        )


class UnConFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConFinding
        fields = ("experiment", "id", "outcome", "is_significant", "is_important")


class UnConProcessingDomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnConProcessingDomain
        fields = ("experiment", "id", "main")


class UnConSuppressionMethodSerializer(serializers.ModelSerializer):
    sub_type = serializers.PrimaryKeyRelatedField(queryset=UnConSuppressionMethodSubType.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=UnConSuppressionMethodType.objects.all())

    class Meta:
        model = UnConSuppressionMethod
        fields = ("experiment", "id", "type", "sub_type")


class UnConSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConSample
        fields = ("experiment", "id", "type", "size_excluded", "size_included")


class FullUnConExperimentSerializer(serializers.ModelSerializer):
    study = serializers.PrimaryKeyRelatedField(queryset=Study.objects.all())
    findings = UnConFindingSerializer(many=True, read_only=True)
    samples = UnConSampleSerializer(many=True, read_only=True)
    suppressed_stimuli = UnConSuppressedStimulusSerializer(many=True, read_only=True)
    target_stimuli = UnConTargetStimulusSerializer(many=True, read_only=True)
    processing_domains = UnConProcessingDomainSerializer(many=True, read_only=True)
    suppression_methods = UnConSuppressionMethodSerializer(many=True, read_only=True)
    tasks = UnConTaskSerializer(many=True, read_only=True)
    consciousness_measures = UnConsciousnessMeasureSerializer(many=True, read_only=True)
    paradigm = UnConSpecificParadigmSerializer(read_only=True)

    class Meta:
        model = UnConExperiment
        depth = 2
        fields = (
            "id",
            "study",
            "experiment_findings_notes",
            "paradigm",
            "type",
            "findings",
            "consciousness_measures",
            "samples",
            "suppressed_stimuli",
            "target_stimuli",
            "tasks",
            "is_target_same_as_suppressed_stimulus",
            "is_target_stimulus",
            "consciousness_measures_notes",
            "processing_domains",
            "suppression_methods",
            "significance",
        )


class StudyWithUnConExperimentsSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, required=False)
    experiments = FullUnConExperimentSerializer(many=True, required=False)
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
            "is_author_submitter",
            "type",
        ]


class ThinUnConExperimentSerializer(FullUnConExperimentSerializer):
    class Meta:
        model = UnConExperiment
        fields = [
            "id",
            "study",
            "experiment_findings_notes",
            "type",
            "is_target_same_as_suppressed_stimulus",
            "is_target_stimulus",
            "consciousness_measures_notes",
        ]


class ThinStudyWithUnConExperimentsSerializer(StudyWithUnConExperimentsSerializer):
    experiments = ThinUnConExperimentSerializer(many=True, required=False)


class StudyWithExperimentsUnConCreateSerializer(StudyWithUnConExperimentsSerializer):
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


class NationOfConsciousnessBySignificanceGraphSerializer(serializers.Serializer):
    country = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    value = serializers.IntegerField()
    total = serializers.IntegerField()
    significance = serializers.CharField()

    def get_country(self, obj) -> str:
        return countries.alpha3(obj["country"])

    def get_country_name(self, obj) -> str:
        return countries.name(obj["country"])
