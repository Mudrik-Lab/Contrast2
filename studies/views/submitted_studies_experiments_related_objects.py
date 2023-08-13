import copy

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from studies.models import Task, Sample, Stimulus, Measure, Interpretation, FindingTag, ConsciousnessMeasure
from studies.permissions import SubmitterOnlyPermission
from studies.serializers import TaskSerializer, SampleSerializer, StimulusSerializer, MeasureSerializer, \
    InterpretationCreateSerializer, FindingTagSerializer, ConsciousnessMeasureSerializer
from studies.views.base_study_related_views_mixins import StudyRelatedPermissionsViewMixin, \
    ExperimentRelatedNestedObjectMixin


class StudyExperimentsTasks(StudyRelatedPermissionsViewMixin,
                            ExperimentRelatedNestedObjectMixin,
                            ModelViewSet,
                            GenericViewSet,
                            ):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class BaseStudyExperimentObjectView(StudyRelatedPermissionsViewMixin,
                                    ExperimentRelatedNestedObjectMixin,
                                    ModelViewSet,
                                    GenericViewSet):
    pagination_class = None
    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsSamples(BaseStudyExperimentObjectView):
    serializer_class = SampleSerializer
    queryset = Sample.objects.all()


class StudyExperimentsStimuli(BaseStudyExperimentObjectView):
    serializer_class = StimulusSerializer
    queryset = Stimulus.objects.all()


class StudyExperimentsMeasures(BaseStudyExperimentObjectView):
    serializer_class = MeasureSerializer
    queryset = Measure.objects.all()


class StudyExperimentsInterpretations(BaseStudyExperimentObjectView):
    serializer_class = InterpretationCreateSerializer
    queryset = Interpretation.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Note: DONT pass explicit experiment id in the creation data, as it's provided by the URI
        """
        Interpretation.objects.filter(experiment=int(self.kwargs.get("experiment_pk")), theory=request.data["theory"]).delete()
        return super().create(request, *args, **kwargs)


class StudyExperimentsFindingTags(BaseStudyExperimentObjectView):
    serializer_class = FindingTagSerializer
    queryset = FindingTag.objects.all()


class StudyExperimentsConsciousnessMeasures(BaseStudyExperimentObjectView):
    # Formerly StudyExperimentsConsciousnessMeasures
    serializer_class = ConsciousnessMeasureSerializer
    queryset = ConsciousnessMeasure.objects.all()
