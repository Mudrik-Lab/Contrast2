from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import filters

from contrast_api.choices import StudyTypeChoices
from contrast_api.studies.permissions import SubmitterOnlyPermission
from studies.models import Study

from studies.views.base_submitted_studies import BaseSubmitStudiesViewSert
from uncontrast_studies.models import (
    UnConsciousnessMeasure,
    UnConTask,
    UnConFinding,
    UnConTargetStimulus,
    UnConSuppressedStimulus,
    UnConSuppressionMethod,
    UnConProcessingDomain,
    UnConExperiment,
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

    search_fields = ["title", "DOI"]
    filter_backends = [filters.SearchFilter]

    permission_classes = [SubmitterOnlyPermission]
    queryset = Study.objects.select_related("approval_process")

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
            Prefetch("uncon_experiments", queryset=UnConExperiment.objects.select_related("paradigm")),
            "authors",
            Prefetch("uncon_experiments__tasks", queryset=UnConTask.objects.select_related("type")),
            Prefetch("uncon_experiments__findings", queryset=UnConFinding.objects.select_related("outcome")),
            Prefetch(
                "uncon_experiments__unconsciousness_measures",
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
                "uncon_experiments__suppression_methods",
                queryset=UnConSuppressionMethod.objects.select_related("type", "sub_type"),
            ),
            Prefetch(
                "uncon_experiments__processing_domains",
                queryset=UnConProcessingDomain.objects.select_related("main"),
            ),
            "uncon_experiments__samples",
        )

    @extend_schema(request=StudyWithExperimentsUnConCreateSerializer, responses=StudyWithUnConExperimentsSerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
