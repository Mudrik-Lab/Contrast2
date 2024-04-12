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
)


class UnConSpecificParadigmSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConSpecificParadigm


class UnConTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConTask


class UnConsciousnessMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConsciousnessMeasure


class UnConTargetStimulusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConTargetStimulus


class UnConSuppressedStimulusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConSuppressedStimulus


class UnConFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConFinding


class UnConProcessingDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConProcessingDomain


class UnConSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnConSample


class FullUnConExperimentSerializer(serializers.ModelSerializer):
    study = serializers.PrimaryKeyRelatedField(queryset=Study.objects.all())
    findings = UnConFindingSerializer(many=True, read_only=True)
    samples = UnConSampleSerializer(many=True, read_only=True)
    suppressed_stimuli = UnConSuppressedStimulusSerializer(many=True, read_only=True)
    target_stimuli = UnConTargetStimulusSerializer(many=True, read_only=True)
    processing_domains = UnConProcessingDomainSerializer(many=True, read_only=True)
    tasks = UnConTaskSerializer(many=True, read_only=True)
    consciousness_measures = UnConsciousnessMeasureSerializer(many=True, read_only=True)
    paradigms = UnConSpecificParadigmSerializer(many=True, read_only=True)

    class Meta:
        model = UnConExperiment
        depth = 2
        fields = (
            "id",
            "study",
            "experiment_findings_notes",
            "paradigms",
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
