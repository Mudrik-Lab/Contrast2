from django_countries import countries
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from approval_process.models import ApprovalProcess

from studies.models import Study, Author
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
    sub_type = serializers.PrimaryKeyRelatedField(queryset=UnConsciousnessMeasureSubType.objects.all(), allow_null=True)

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
    sub_category = serializers.PrimaryKeyRelatedField(
        queryset=UnConStimulusSubCategory.objects.all(), required=False, allow_null=True
    )
    modality = serializers.PrimaryKeyRelatedField(queryset=UnConModalityType.objects.all())
    suppressed_stimulus = serializers.PrimaryKeyRelatedField(queryset=UnConSuppressedStimulus.objects.all())

    class Meta:
        model = UnConTargetStimulus
        fields = (
            "experiment",
            "id",
            "category",
            "sub_category",
            "modality",
            "suppressed_stimulus",
            "is_target_same_as_suppressed_stimulus",
            "number_of_stimuli",
        )


class UnConSuppressedStimulusSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=UnConStimulusCategory.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(
        queryset=UnConStimulusSubCategory.objects.all(), required=False, allow_null=True
    )
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
            "is_target_stimulus",
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
    sub_type = serializers.PrimaryKeyRelatedField(queryset=UnConSuppressionMethodSubType.objects.all(), allow_null=True)
    type = serializers.PrimaryKeyRelatedField(queryset=UnConSuppressionMethodType.objects.all())

    class Meta:
        model = UnConSuppressionMethod
        fields = ("experiment", "id", "type", "sub_type")


class UnConSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConSample
        fields = ("experiment", "id", "type", "size_excluded", "size_included", "size_total")


class FullUnConExperimentSerializer(serializers.ModelSerializer):
    study = serializers.PrimaryKeyRelatedField(queryset=Study.objects.all())
    findings = serializers.SerializerMethodField()
    samples = serializers.SerializerMethodField()
    suppressed_stimuli = serializers.SerializerMethodField()
    target_stimuli = serializers.SerializerMethodField()
    processing_domains = serializers.SerializerMethodField()
    suppression_methods = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    consciousness_measures = serializers.SerializerMethodField()
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
            "consciousness_measures_notes",
            "processing_domains",
            "suppression_methods",
            "significance",
        )

    @extend_schema_field(UnConFindingSerializer(many=True))
    def get_findings(self, obj: UnConExperiment):
        findings = obj.findings.order_by("id")
        return UnConFindingSerializer(many=True, instance=findings).data

    @extend_schema_field(UnConsciousnessMeasureSerializer(many=True))
    def get_consciousness_measures(self, obj: UnConExperiment):
        consciousness_measures = obj.unconsciousness_measures.order_by("id")
        return UnConsciousnessMeasureSerializer(many=True, instance=consciousness_measures).data

    @extend_schema_field(UnConSampleSerializer(many=True))
    def get_samples(self, obj: UnConExperiment):
        samples = obj.samples.order_by("id")
        return UnConSampleSerializer(many=True, instance=samples).data

    @extend_schema_field(UnConSuppressedStimulusSerializer(many=True))
    def get_suppressed_stimuli(self, obj: UnConExperiment):
        suppressed_stimuli = obj.suppressed_stimuli.order_by("id")
        return UnConSuppressedStimulusSerializer(many=True, instance=suppressed_stimuli).data

    @extend_schema_field(UnConTargetStimulusSerializer(many=True))
    def get_target_stimuli(self, obj: UnConExperiment):
        target_stimuli = obj.target_stimuli.order_by("id")
        return UnConTargetStimulusSerializer(many=True, instance=target_stimuli).data

    @extend_schema_field(UnConTaskSerializer(many=True))
    def get_tasks(self, obj: UnConExperiment):
        tasks = obj.tasks.order_by("id")
        return UnConTaskSerializer(many=True, instance=tasks).data

    @extend_schema_field(UnConProcessingDomainSerializer(many=True))
    def get_processing_domains(self, obj: UnConExperiment):
        processing_domains = obj.processing_domains.order_by("id")
        return UnConProcessingDomainSerializer(many=True, instance=processing_domains).data

    @extend_schema_field(UnConSuppressionMethodSerializer(many=True))
    def get_suppression_methods(self, obj: UnConExperiment):
        suppression_methods = obj.suppression_methods.order_by("id")
        return UnConSuppressionMethodSerializer(many=True, instance=suppression_methods).data


class StudyWithUnConExperimentsSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, required=False)
    experiments = FullUnConExperimentSerializer(many=True, required=False, source="uncon_experiments", read_only=True)
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
            "paradigm",
            "consciousness_measures_notes",
        ]


class UnConCreateExperimentSerializer(FullUnConExperimentSerializer):
    paradigm = serializers.PrimaryKeyRelatedField(queryset=UnConSpecificParadigm.objects.all())

    class Meta:
        model = UnConExperiment
        fields = [
            "id",
            "study",
            "experiment_findings_notes",
            "type",
            "paradigm",
            "consciousness_measures_notes",
        ]


class ThinStudyWithUnConExperimentsSerializer(StudyWithUnConExperimentsSerializer):
    experiments = ThinUnConExperimentSerializer(many=True, required=False, source="uncon_experiments", read_only=True)


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
