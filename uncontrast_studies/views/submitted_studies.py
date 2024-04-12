from django.db.models import Prefetch, Q
from drf_spectacular.utils import extend_schema

from contrast_api.choices import StudyTypeChoices
from studies.models import Study, Measure, Task, FindingTag, ConsciousnessMeasure, Stimulus, Paradigm

from studies.views.base_submitted_studies import BaseSubmitStudiesViewSert
from uncontrast_studies.models import (
    UnConsciousnessMeasure,
    UnConSpecificParadigm,
    UnConTask,
    UnConFinding,
    UnConTargetStimulus,
    UnConSuppressedStimulus,
    UnConSuppressionMethod,
)
from uncontrast_studies.serializers import (
    StudyWithUnConExperimentsSerializer,
    ThinStudyWithUnConExperimentsSerializer,
    StudyWithExperimentsUnConCreateSerializer,
)


class SubmitUnContrastStudiesViewSet(BaseSubmitStudiesViewSert):
    """
    Getting/creating studies I've submitted, editing, etc
    Also allows single link of a specific study (as result of search perhaps)
    And searching for studies by title/DOI
    """

    serializer_class = StudyWithUnConExperimentsSerializer

    def get_serializer_class(self):
        if self.action in ["list", "my_studies"]:
            return ThinStudyWithUnConExperimentsSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return StudyWithExperimentsUnConCreateSerializer
        else:
            return super().get_serializer_class()

    def filter_and_prefetch_queryset(self, queryset):
        return queryset.filter(type=StudyTypeChoices.UNCONSCIOUSNESS).prefetch_related(
            "uncon_experiments",
            "authors",
            Prefetch("uncon_experiments__tasks", queryset=UnConTask.objects.select_related("type")),
            Prefetch("uncon_experiments__findings", queryset=UnConFinding.objects.select_related("type")),
            Prefetch(
                "uncon_experiments__consciousness_measures",
                queryset=UnConsciousnessMeasure.objects.select_related("type", "sub_type", "phase"),
            ),
            Prefetch(
                "uncon_experiments__suppressed_stimuli",
                queryset=UnConSuppressedStimulus.objects.select_related("category", "sub_category", "modality"),
            ),
            Prefetch(
                "uncon_experiments__target_stimuli",
                queryset=UnConTargetStimulus.objects.select_related("category", "sub_category", "modality"),
            ),
            Prefetch(
                "uncon_experiments__paradigms",
                queryset=UnConSpecificParadigm.objects.select_related("main"),
            ),
            Prefetch(
                "uncon_experiments__suppression_methods",
                queryset=UnConSuppressionMethod.objects.select_related("type", "sub_type"),
            ),
            "uncon_experiments__samples",
        )

    @extend_schema(request=StudyWithExperimentsUnConCreateSerializer, responses=StudyWithUnConExperimentsSerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
