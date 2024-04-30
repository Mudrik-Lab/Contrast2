import copy

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from rest_framework.viewsets import ModelViewSet, GenericViewSet

from contrast_api.studies.permissions import SubmitterOnlyPermission
from uncontrast_studies.models import (
    UnConTask,
    UnConSuppressedStimulus,
    UnConTargetStimulus,
    UnConSample,
    UnConSuppressionMethod,
    UnConProcessingDomain,
    UnConFinding,
    UnConsciousnessMeasure,
)
from uncontrast_studies.serializers import (
    UnConTaskSerializer,
    UnConSampleSerializer,
    UnConSuppressedStimulusSerializer,
    UnConTargetStimulusSerializer,
    UnConFindingSerializer,
    UnConsciousnessMeasureSerializer,
    UnConSuppressionMethodSerializer,
    UnConProcessingDomainSerializer,
)
from studies.views.base_study_related_views_mixins import (
    StudyRelatedPermissionsViewMixin,
    ExperimentRelatedNestedObjectMixin,
)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(location="path", name="study_pk", type=str),
            OpenApiParameter(location="path", name="experiment_pk", type=str),
        ]
    ),
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(location="path", name="study_pk", type=str),
            OpenApiParameter(location="path", name="experiment_pk", type=str),
        ]
    ),
    destroy=extend_schema(
        parameters=[
            OpenApiParameter(location="path", name="study_pk", type=str),
            OpenApiParameter(location="path", name="experiment_pk", type=str),
        ]
    ),
    update=extend_schema(
        parameters=[
            OpenApiParameter(location="path", name="study_pk", type=str),
            OpenApiParameter(location="path", name="experiment_pk", type=str),
        ]
    ),
    partial_update=extend_schema(
        parameters=[
            OpenApiParameter(location="path", name="study_pk", type=str),
            OpenApiParameter(location="path", name="experiment_pk", type=str),
        ]
    ),
    create=extend_schema(
        parameters=[
            OpenApiParameter(location="path", name="study_pk", type=str),
            OpenApiParameter(location="path", name="experiment_pk", type=str),
        ]
    ),
)
class BaseStudyExperimentObjectView(
    StudyRelatedPermissionsViewMixin, ExperimentRelatedNestedObjectMixin, ModelViewSet, GenericViewSet
):
    pagination_class = None
    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsTasks(BaseStudyExperimentObjectView):
    serializer_class = UnConTaskSerializer
    queryset = UnConTask.objects.all()


class StudyExperimentsSamples(BaseStudyExperimentObjectView):
    serializer_class = UnConSampleSerializer
    queryset = UnConSample.objects.all()


class StudyExperimentsSuppressedStimuli(BaseStudyExperimentObjectView):
    serializer_class = UnConSuppressedStimulusSerializer
    queryset = UnConSuppressedStimulus.objects.all()


class StudyExperimentsTargetStimuli(BaseStudyExperimentObjectView):
    serializer_class = UnConTargetStimulusSerializer
    queryset = UnConTargetStimulus.objects.all()


class StudyExperimentsFinding(BaseStudyExperimentObjectView):
    serializer_class = UnConFindingSerializer
    queryset = UnConFinding.objects.all()


class StudyExperimentsConsciousnessMeasures(BaseStudyExperimentObjectView):
    serializer_class = UnConsciousnessMeasureSerializer
    queryset = UnConsciousnessMeasure.objects.all()


class StudyExperimentsUnConSuppressionMethod(BaseStudyExperimentObjectView):
    serializer_class = UnConSuppressionMethodSerializer
    queryset = UnConSuppressionMethod.objects.all()


class StudyExperimentsUnConProcessingDomain(BaseStudyExperimentObjectView):
    serializer_class = UnConProcessingDomainSerializer
    queryset = UnConProcessingDomain.objects.all()
